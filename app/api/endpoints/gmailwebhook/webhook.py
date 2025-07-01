from typing import Tuple 
from fastapi import APIRouter, Depends, HTTPException, status,UploadFile,File,Request,Header
from app.core.settings import get_settings
import httpx
import base64
import json
import requests

router = APIRouter()

settings = get_settings()


@router.get("/start-watch", status_code=status.HTTP_200_OK)
async def start_watch():
    url = "https://gmail.googleapis.com/gmail/v1/users/me/watch"

    tmp_token:str = "ya29.a0AS3H6NzQ_Jd_XfeDnLSAok3jnJo4zqQg0f5j4MkbvXnK1AYaEWmgW5bylD1aAmy5ddSbs7lIAAoeKxnTuTutPoYecNlEMqIGEd8TShRAgTUTld8uEaU-r2PUffvwF83qtm7xzg9XWpudqIbTiRbW-kJilAH9lQrP-8d4dCp5BuBV_kCWL6paSyFSaCgYKAQ4SARESFQHGX2MiWpQ7dYCCoNDRO5OIQewEdw0191"
    project:str = "emailagentetest"
    topic_name:str = "NotificationTest"
    headers = {
        "Authorization": f"Bearer {tmp_token}",
        "Content-Type": "application/json"
    }

    body = {
        "labelIds": ["INBOX"],
        "topicName": f"projects/{project}/topics/{topic_name}"
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        print("Watch registered:")
        print(response.json())
    else:
        print("Error:", response.status_code, response.text)

    return response.json()


@router.post("/gmail-webhook", status_code=status.HTTP_200_OK)
async def gmail_webhook(request: Request, content_length: int = Header(...)):
    body = await request.json()
    print("Pub/Sub Message Received:", json.dumps(body, indent=2))

    message_data = body.get("message", {}).get("data")
    if not message_data:
        return {"status": "no data"}

    # Decode the base64-encoded data
    decoded_data = base64.b64decode(message_data).decode("utf-8")
    # pubsub_message = json.loads(decoded_data)

    # history_id = pubsub_message.get("historyId")
    # if not history_id:
    #     return {"status": "no historyId"}

    # Optional: fetch new message(s)
    
    #await fetch_new_emails(history_id)

    return {"status": "ok"}