from langchain_core.messages import AIMessage, ToolCall


def convert_openai_to_langchain(openai_message):
    # Extract tool calls
    tool_calls_data = []
    langchain_tool_calls = []

    if openai_message.tool_calls:
        for i, tool_call in enumerate(openai_message.tool_calls):
            # Format for additional_kwargs
            tool_calls_data.append(
                {
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                    "index": i,
                }
            )

            # Format for tool_calls attribute
            # Parse the arguments from JSON string to dict
            import json

            args = json.loads(tool_call.function.arguments)

            langchain_tool_calls.append(
                ToolCall(
                    name=tool_call.function.name,
                    args=args,
                    id=tool_call.id,
                    type="tool_call",
                )
            )

    # Create AIMessage with the converted data
    message = AIMessage(
        content=openai_message.content or "",
        additional_kwargs={"tool_calls": tool_calls_data},
        tool_calls=langchain_tool_calls,
    )

    return message
