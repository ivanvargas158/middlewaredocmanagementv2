import httpx
import asyncio
from app.core.settings import get_settings

settings = get_settings()

async def azure_ocr_async(file_bytes: bytes) -> dict:
    headers = {
        "Ocp-Apim-Subscription-Key": settings.azurevision_subscription_key,
        "Content-Type": "application/octet-stream"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.azurevision_endpoint}/vision/v3.2/read/analyze",
            content=file_bytes,
            headers=headers
        )

        operation_url = response.headers.get("Operation-Location")
        if not operation_url:
            raise Exception("Missing Operation-Location header")

        # Poll until complete
        while True:
            status_response = await client.get(operation_url, headers=headers)
            result = status_response.json()
            if result['status'] not in ['notStarted', 'running']:
                break
            await asyncio.sleep(1)

        if result['status'] == 'succeeded':
            lines = []
            total_confidence = 0.0
            word_count = 0

            for page in result['analyzeResult']['readResults']:
                for line in page['lines']:
                    lines.append(line['text'])
                    for word in line['words']:
                        total_confidence += word.get('confidence', 0.0)
                        word_count += 1

            average_confidence = (total_confidence / word_count) if word_count > 0 else 0.0

            return {
                "ocr_text": "\n".join(lines),
                "ocr_confidence": round(average_confidence, 3)
            }

        raise Exception("OCR failed")
