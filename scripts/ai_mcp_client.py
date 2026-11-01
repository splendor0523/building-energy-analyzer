import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import Client,StdioServerParameters

import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")

def to_deepseek_tool(tool):
    return {
        "type": "function",
        "function":{
            "name": tool.name,
            "description": tool.description or "",
            "parameters" : tool.input_schema,
        },
    }

# ------ 接收 AI 下达的单次工具调用指令，执行 MCP Server 上的工具，然后把执行结果打包成 AI 能看懂的标准格式 ------
async def execute_tool_call(client,tool_call,allowed_names:set[str]) -> dict:
    name = tool_call.function.name

    try:
        if name not in allowed_names:
            raise ValueError(f"Tool not allowed: {name}")

        arguments = json.loads(tool_call.function.arguments)
        if not isinstance(arguments,dict):
            raise ValueError("Tool arguments must be a JSON object.")
    
    except (ValueError,TypeError) as exc:
        payload = {"status":"error","message":str(exc)}

    else:
        result = await client.call_tool(
            name,
            arguments,
            read_timeout_seconds=600,
        )

        if result.is_error:
            error_text = " ".join(
                part.text for part in result.content
                if part.type == "text"
            )
            payload = {
                "status": "error",
                "message": error_text or "MCP tool failed."
            }

        elif result.structured_content is None:
            payload = {
                "status": "error",
                "message": "Tool returned no structured result.",
            }
        
        else:
            payload = {
                "status": "success",
                "data": result.structured_content,
            }
        
    return {
        "role": "tool",
        "tool_call_id":tool_call.id,
        "content": json.dumps(payload,ensure_ascii=False)
    }

async def main(user_request: str):

    if not user_request.strip():
        raise ValueError("The request cannot be empty.")


    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "scripts" / "mcp_server.py")],
    )

    async with Client(server_params) as client:
        result = await client.list_tools()

        tools = [
            to_deepseek_tool(tool)
            for tool in result.tools
        ]

        allowed_names = {tool.name for tool in result.tools}

        if not allowed_names:
            raise RuntimeError("MCP sever exposed no tools.")

        print(f"Available tools: {len(tools)}")

        for tool in tools:
            print("Tool",tool["function"]["name"])

        print("\nDeepSeek Tool Definition:")
        print(json.dumps(tools[0], indent=2, ensure_ascii=False))

        api_key = os.getenv("DEEPSEEK_API_KEY")

        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set.")

        llm = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a building energy analysis assistant. "
                    "Use the available tools when numerical results are needed. "
                    "Do not invent simulation data or results. "
                    "Choose tools according to the user's actual request. "
                    "Execute dependent operations in order, using successful "
                    "outputs from earlier tool calls as inputs to later calls. "
                    "Do not treat tool errors as successful operations. "
                    "Do not claim to have read a generated file when only "
                    "its path was returned. "
                    "Existing output files and non-empty directories cannot be overwritten. "
                    "Report Ideal Loads as thermal energy demand, not actual HVAC electricity consumption. "
                    "Peak hourly energy values are in kWh, not kW. "
                    "Distinguish changes in peak magnitude from changes in peak timing. "
                    "Do not infer thermal comfort, daylight, glare, or overall building performance from energy results alone. "
                    "Clearly distinguish source-supported findings from additional engineering considerations. "

                ),
            },
            {
                "role": "user",
                "content": user_request
            }
        ]
        
        max_tool_calls = 10
        completed_calls = 0

        while True:
            response = await llm.chat.completions.create(
                model="deepseek-flash",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                extra_body = {"thinking": {"type": "disabled"}},
            )

            message = response.choices[0].message

            if not message.tool_calls:
                if not message.content:
                    raise RuntimeError(
                        "DeepSeek returned neither an answer nor tool calls."
                    )
                print("\nFinal AI Answer:\n")
                print(message.content)
                return

            if completed_calls + len(message.tool_calls) > max_tool_calls:
                raise RuntimeError("Tool call limit exceeded.")

            messages.append(message)

            for tool_call in message.tool_calls:
                print("\nSelected tool:",tool_call.function.name)

                tool_message = await execute_tool_call(
                    client,
                    tool_call,
                    allowed_names,
                )

                messages.append(tool_message)
                completed_calls += 1

                print("Tool response:",tool_message["content"][:1000])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Building Energy AI MCP Client"
    )
    parser.add_argument(
        "request",
        help = "Natural-Language energy analysis task",
    )

    args = parser.parse_args()
    asyncio.run(main(args.request))