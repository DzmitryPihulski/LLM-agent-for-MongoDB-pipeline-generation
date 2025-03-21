import json
from typing import Annotated, Any, Dict, List, Union

from bson import json_util
from components.prompts import DEEPSEEK_SYSTEM_PROMPT, EXPLORATION_AGENT_NODE
from db.db import mongo_db
from db.schema_analyser import analyze_mongo_schema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool  # type: ignore
from langgraph.prebuilt import InjectedState
from models.graph_models import State

from graph.llm import Deepseek, MistralLLM, OpenAI_llm
from graph.utils import convert_openai_to_langchain


async def input_validator(
    state: State, config: RunnableConfig
) -> Dict[str, list[HumanMessage]]:
    human_input = state["human_input"].replace("'", "").replace("`", "")
    return {"messages": [HumanMessage(content=human_input)]}


@tool("mongo_tool")  # type: ignore
async def mongo_tool(
    collection_name: str,
    aggregation_pipeline: List[Dict],
    database: Annotated[str, InjectedState("messages")],
) -> List[Dict[str, Any]]:
    """The input point to the db for running pipelines.

    Args:
        collection_name (str): The name of the collection to run the aggregation pipeline on.
        aggregation_pipeline (List[Dict]): The list of aggregation pipeline stages. For example:
            [
                {
                    $lookup: {
                    from: "transactions",
                    localField: "accounts",
                    foreignField: "account_id",
                    as: "customer_transactions"
                    }
                }
            ]

    Returns:
        List[Dict[str, Any]]: The result documents after running the pipeline.
    """
    try:
        collection = mongo_db._mongo_client[database][collection_name]
        result = collection.aggregate(aggregation_pipeline)
        json_compatible_result = json.loads(json_util.dumps(result.to_list()))

        return json_compatible_result
    except Exception as e:
        print(
            f"Args: collection_name: {collection_name}, aggregation_pipeline: {aggregation_pipeline}"
        )
        raise f"Pipeline is not valid! {str(e)}"


# CUSTOM TOOL NODE
async def custom_tool_node(
    state: State, config: RunnableConfig
) -> Dict[str, list[Union[ToolMessage, None]]]:
    outputs: List[ToolMessage] = list()
    if isinstance(state["messages"][-1], AIMessage):
        for tool_call in state["messages"][-1].tool_calls:
            arguments = tool_call["args"].copy()

            print("Arguments: ", arguments)
            arguments["database"] = state["database"]
            tool_result = await mongo_tool.ainvoke(input=arguments, config=config)  # type: ignore
            outputs.append(
                ToolMessage(
                    content=tool_result,
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
            return {
                "messages": outputs,  # type: ignore
                "answer": {
                    "tool_output": [output.content for output in outputs],
                    "collection": arguments["collection_name"],
                    "aggregation_pipeline": arguments["aggregation_pipeline"],
                },  # type: ignore
            }


async def exploration_node(
    state: State, config: RunnableConfig
) -> Dict[str, list[AIMessage]]:
    template = ChatPromptTemplate(
        [
            ("system", EXPLORATION_AGENT_NODE),
            ("human", "{user_query}"),
        ]
    )

    prompt_value = template.invoke(  # type: ignore
        {
            "mongo_scheme": str(
                await analyze_mongo_schema(mongo_db._mongo_client[state["database"]])
            ),
            "user_query": str(state["messages"][-1].content),  # type: ignore
        },
        config=config,
    )
    if state["model_name"] == "Mistral":
        llm_with_tools = MistralLLM.bind_tools([mongo_tool])  # type: ignore
        print("PROMPT FOR RESEARCH LLM:", prompt_value)
        response = llm_with_tools.invoke(input=prompt_value)
        print("RESPONSE: ", response)
        return {"messages": [response]}  # type: ignore

    if state["model_name"] == "Deepseek":
        deep_seek_prompt = [
            {
                "role": "system",
                "content": DEEPSEEK_SYSTEM_PROMPT.replace(
                    "{mongo_scheme}",
                    str(
                        await analyze_mongo_schema(
                            mongo_db._mongo_client[state["database"]]
                        )
                    ),
                ),
            },
            {"role": "user", "content": str(state["messages"][-1].content)},
        ]
        print("PROMPT FOR DEEPSEEK LLM:", deep_seek_prompt)
        response = Deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=deep_seek_prompt,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": mongo_tool.name,
                        "description": mongo_tool.description,
                        "parameters": {
                            "type": "object",  # This was missing
                            "properties": {  # Parameters should be under 'properties'
                                "collection_name": {
                                    "title": "Collection Name",
                                    "type": "string",
                                },
                                "aggregation_pipeline": {
                                    "title": "Aggregation Pipeline",
                                    "type": "array",
                                    "items": {"type": "object"},
                                },
                                "database_name": {
                                    "title": "Database Name",
                                    "type": "string",
                                },
                            },
                            "required": [
                                "collection_name",
                                "aggregation_pipeline",
                            ],
                        },
                    },
                },
            ],
        )
        print("RESPONSE: ", response.choices[0].message)
        print("CONVERTED: ", convert_openai_to_langchain(response.choices[0].message))
        return {"messages": [convert_openai_to_langchain(response.choices[0].message)]}  # type: ignore

    if state["model_name"] == "OpenAI":
        print(mongo_tool.tool_call_schema.schema())
        llm_with_tools = OpenAI_llm.bind_tools([mongo_tool])  # type: ignore
        print("PROMPT FOR RESEARCH LLM:", prompt_value)
        response = llm_with_tools.invoke(input=prompt_value)
        print("RESPONSE: ", response)
        return {"messages": [response]}  # type: ignore
