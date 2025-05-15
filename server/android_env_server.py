from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from android_world.env import interface, json_action
from android_world.env.env_launcher import load_and_setup_env
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.app_android_env = load_and_setup_env(
        console_port=5554,
        emulator_setup=False,
        adb_path="/opt/android/platform-tools/adb",
    )
    yield
    # Shutdown
    if app.state.app_android_env is not None:
        app.state.app_android_env.close()


app = FastAPI(lifespan=lifespan)


class ActionRequest(BaseModel):
    action_type: str
    x: int | None = None
    y: int | None = None
    text: str | None = None
    direction: str | None = None
    app_name: str | None = None


class StateResponse(BaseModel):
    pixels: list
    ui_elements: list


def get_app_android_env(request: Request) -> interface.AsyncEnv:
    return request.app.state.app_android_env


AndroidEnv = Annotated[interface.AsyncEnv, Depends(get_app_android_env)]


@app.post("/reset")
async def reset(go_home: bool, app_android_env: AndroidEnv):
    app_android_env.reset(go_home=go_home)
    return {"status": "success"}


@app.get("/state")
async def get_state(wait_to_stabilize: bool, app_android_env: AndroidEnv):
    state = app_android_env.get_state(wait_to_stabilize=wait_to_stabilize)
    return {"pixels": state.pixels.tolist()}


@app.post("/execute_action")
async def execute_action(action: ActionRequest, app_android_env: AndroidEnv):
    action_dict = action.model_dump(exclude_none=True)
    json_act = json_action.JSONAction(**action_dict)
    app_android_env.execute_action(json_act)
    return {"status": "success"}


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
