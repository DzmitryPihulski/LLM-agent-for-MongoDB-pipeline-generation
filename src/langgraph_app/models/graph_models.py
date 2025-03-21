from typing import Annotated, List, Union

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages  # type: ignore
from typing_extensions import TypedDict


class State(TypedDict):
    human_input: Annotated[str, "The initial query."]
    database: Annotated[str, "The initial database."]
    model_name: Annotated[str, "The initial model."]
    messages: Annotated[
        List[Union[AIMessage, HumanMessage, ToolMessage, None]],
        add_messages,
        "Messages between nodes.",
    ]
    answer: Annotated[Union[List, None], "Final response"]


class Config(TypedDict):
    pass


class InputModel(TypedDict):
    human_input: Annotated[str, "The initial query."]
    database: Annotated[str, "The initial database."]
    model_name: Annotated[str, "The initial model."]


class OutputModel(TypedDict):
    answer: Annotated[Union[dict, None], "Final response"]
