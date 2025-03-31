from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from browser_use import Agent,Controller
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

from pydantic import BaseModel

class TaskRequest(BaseModel):
    prompt: str

from typing import List, Optional, Any



class QueryParam(BaseModel):
    key: str
    value: str


class Url(BaseModel):
    raw: str
    host: Optional[List[str]]
    path: Optional[List[str]]
    query: Optional[List[QueryParam]]


class Header(BaseModel):
    key: str
    value: str
    type: Optional[str]


class Body(BaseModel):
    mode: Optional[str]
    raw: Optional[str]


class Request(BaseModel):
    method: str
    header: List[Header]
    body: Optional[Body]
    url: Url


class Response(BaseModel):
    # You can add more fields if needed
    pass


class Item(BaseModel):
    name: str
    request: Request
    response: Optional[List[Response]]


class Script(BaseModel):
    exec: List[str]
    type: Optional[str]


class Event(BaseModel):
    listen: str
    script: Optional[Script]


class Variable(BaseModel):
    key: str
    value: Any


class Info(BaseModel):
    name: str
    schema: str
    _postman_id: Optional[str]
    description: Optional[str]


class PostmanCollection(BaseModel):
    info: Info
    item: List[Item]
    event: Optional[List[Event]]
    variable: Optional[List[Variable]]


class ResponseOutput(BaseModel):
    data: PostmanCollection

controller = Controller(output_model=ResponseOutput)

# Define the async function that will run the agent
async def run_agent(task: str):
    agent = Agent(
        task=task,
        llm=ChatOpenAI(model="gpt-4o")
    )
    history = await agent.run()
    return history.final_result()

# Create the route
@app.post("/scrapDocAndUploadToTechDoc")
async def scrap_and_upload(request: TaskRequest):
    # Run the agent and wait for the result
    return {'data' : await run_agent(request.prompt), 'success':"true"}

