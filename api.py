import httpx
import asyncio
from pydantic import BaseModel, ValidationError

class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str

async def main():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://jsonplaceholder.typicode.com/posts/1")
        post = Post.model_validate(res.json())
        print(post)

asyncio.run(main())
