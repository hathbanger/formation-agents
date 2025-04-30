# agent_api_server.py
import time
import logging
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union

logger = logging.getLogger(__name__)

class TaskVariable(BaseModel):
    value: Union[str, Dict[str, Any], List[Dict[str, Any]]]
    mime_type: Optional[str] = None
    name: Optional[str] = None

class TaskInput(BaseModel):
    variables: Dict[str, TaskVariable] = Field(default_factory=dict)

class TaskOutput(BaseModel):
    variables: Dict[str, TaskVariable] = Field(default_factory=dict)
    error: Optional[str] = None

class RunTaskRequest(BaseModel):
    agent_id: str
    task_id: str
    inputs: TaskInput
    conversation_id: Optional[str] = None
    allow_trace: Optional[bool] = False
    allow_retry: Optional[bool] = False
    trace_id: Optional[str] = None
    task_retry_id: Optional[str] = None
    timeout_ms: Optional[int] = None
    response_format: Optional[str] = None
    max_scan_size: Optional[int] = None

class RunTaskResponse(BaseModel):
    agent_id: str
    task_id: str
    trace_id: Optional[str] = None
    state: str = "completed"
    outputs: TaskOutput
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float

def create_agent_api(agent_id: str, workflow_runner):
    start_time = time.time()
    app = FastAPI(
        title=f"{agent_id} API",
        description=f"API for {agent_id} agent",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(
            status="ok",
            version="1.0.0",
            uptime=time.time() - start_time
        )

    @app.post("/run-task", response_model=RunTaskResponse)
    async def run_task(request: RunTaskRequest = Body(...)):
        try:
            logger.info(f"Received task request for agent: {request.agent_id}, task: {request.task_id}")
            # Extract query/topic from input variables
            topic = request.inputs.variables.get("query", None)
            if not topic:
                raise HTTPException(status_code=400, detail="Missing 'query' variable in inputs")
            topic = topic.value

            # Run the workflow (assume it returns a string or markdown)
            response_content = workflow_runner(topic)
            task_output = TaskOutput(
                variables={
                    "response": TaskVariable(
                        value=response_content,
                        mime_type="text/markdown"
                    )
                }
            )
            return RunTaskResponse(
                agent_id=request.agent_id,
                task_id=request.task_id,
                trace_id=request.trace_id or f"trace_{time.time()}",
                outputs=task_output
            )
        except Exception as e:
            logger.error(f"Error processing task request: {e}")
            return RunTaskResponse(
                agent_id=request.agent_id,
                task_id=request.task_id,
                trace_id=request.trace_id,
                state="failed",
                outputs=TaskOutput(),
                error=str(e)
            )
    return app