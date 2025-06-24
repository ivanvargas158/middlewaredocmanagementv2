import asyncio

async def background_job():
    await asyncio.sleep(5)
    print("Job done.")
