import requests
from pydantic import BaseModel, ValidationError

class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str

res = requests.get("https://jsonplaceholder.typicode.com/posts/1")
rawData = res.json()

try:
    post = Post.model_validate(rawData)
    print(f"Success! Title: {post.title}")
    print(f"Body: {post.body}")
    
except ValidationError as e:
    print("API returned the wrong shape!")
    print(e.json())