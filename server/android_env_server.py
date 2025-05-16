from contextlib import asynccontextmanager
from typing import Annotated, Any

import uvicorn
from android_world.env import interface, json_action
from android_world.env.env_launcher import load_and_setup_env
from android_world.registry import TaskRegistry
from android_world.suite_utils import Suite, create_suite
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.app_android_env = load_and_setup_env(
        console_port=5554,
        emulator_setup=False,
        adb_path="/opt/android/platform-tools/adb",
    )
    task_registry = TaskRegistry()
    aw_registry = task_registry.get_registry(task_registry.ANDROID_WORLD_FAMILY)
    suite = create_suite(
        task_registry=aw_registry,
        n_task_combinations=2,
        seed=42,  # Optional: for reproducibility
    )
    app.state.suite = suite
    yield
    # Shutdown
    if app.state.app_android_env is not None:
        app.state.app_android_env.close()


app = FastAPI(lifespan=lifespan)


class StateResponse(BaseModel):
    pixels: list
    ui_elements: list


def get_app_android_env(request: Request) -> interface.AsyncEnv:
    return request.app.state.app_android_env


def get_app_suite(request: Request) -> Suite:
    return request.app.state.suite


AndroidEnv = Annotated[interface.AsyncEnv, Depends(get_app_android_env)]
AndroidSuite = Annotated[Suite, Depends(get_app_suite)]


@app.post("/reset")
async def reset(go_home: bool, app_android_env: AndroidEnv):
    app_android_env.reset(go_home=go_home)
    return {"status": "success"}


@app.get("/screenshot")
async def get_screenshot(wait_to_stabilize: bool, app_android_env: AndroidEnv):
    state = app_android_env.get_state(wait_to_stabilize=wait_to_stabilize)
    return {"pixels": state.pixels.tolist()}


@app.post("/execute_action")
async def execute_action(action_dict: dict[str, Any], app_android_env: AndroidEnv):
    action = json_action.JSONAction(**action_dict)
    app_android_env.execute_action(action)
    return {"status": "success"}


@app.get("/suite_task_list")
async def suite_task_list(max_index: int, app_suite: AndroidSuite):
    if max_index > len(app_suite) or max_index < 0:
        return {"task_list": list(app_suite.keys())}
    return {"task_list": list(app_suite.keys())[:max_index]}


@app.get("/suite_task_length")
async def suite_task_length(task_type: str, app_suite: AndroidSuite):
    return {"length": len(app_suite[task_type])}


@app.post("/initialize_task")
async def initialize_task(task_type: str, task_idx: int, app_android_env: AndroidEnv, app_suite: AndroidSuite):
    app_suite[task_type][task_idx].initialize_task(app_android_env)
    return {"status": "success"}


@app.get("/task_score")
async def get_task_score(task_type: str, task_idx: int, app_android_env: AndroidEnv, app_suite: AndroidSuite):
    return {"score": app_suite[task_type][task_idx].is_successful(app_android_env)}


@app.get("/task_goal")
async def get_task_goal(task_type: str, task_idx: int, app_suite: AndroidSuite):
    return {"goal": app_suite[task_type][task_idx].goal}


@app.get("/task_template")
async def get_task_template(task_type: str, task_idx: int, app_suite: AndroidSuite):
    return {"template": app_suite[task_type][task_idx].template}


@app.post("/close")
async def close(app_android_env: AndroidEnv):
    app_android_env.close()
    return {"status": "success"}


@app.get("/health")
async def health(app_android_env: AndroidEnv):
    if isinstance(app_android_env, interface.AsyncEnv):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Environment not initialized")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
