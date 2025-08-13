import json
import httpx
from app.utils.global_resources import remove_yaml_block

async def create_chat_session(bearer: str, uuui: str) -> str:
    url = f"https://app.gpt-trainer.com/api/v1/chatbot/{uuui}/session/create"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer}",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers)

        if response.status_code == 200:
            try:
                session_data = response.json()
                return session_data["uuid"]
            except json.JSONDecodeError as e:
                raise Exception(f"JSON decoding error: {e}")
        else:
            raise Exception(
                f"Failed to create chat session. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )

    except httpx.RequestError as e:
        raise Exception(f"Request error: {e}")
    except KeyError as e:
        raise Exception(f"Missing expected key in response: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")

    
async def create_request(content: str, bearer: str, uuui: str,is_remove_yaml_block:bool = False)->str:
    agent_response:str = ""
    session_uuid = await create_chat_session(bearer, uuui)  # Ensure this is also async

    url_endpoint = f"https://app.gpt-trainer.com/api/v1/session/{session_uuid}/message/stream"
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    payload = {"query": content}

    async  with httpx.AsyncClient(timeout=500) as client:
        async with client.stream("POST", url_endpoint, headers=headers, json=payload) as response:
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line.strip():
                        agent_response += line + "\n"
                        print(line)
            else:
                print("Error:", response.status_code)
    if is_remove_yaml_block:
        agent_response = remove_yaml_block(agent_response)
    return agent_response
