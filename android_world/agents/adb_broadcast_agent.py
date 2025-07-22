import json
import time

from android_world.agents import base_agent
from android_world.env import adb_utils
from android_world.env import interface
from android_world.utils import file_utils


class AdbBroadcastAgent(base_agent.EnvironmentInteractingAgent):
    """Agent that delegates execution to an external Android process via adb."""

    BROADCAST_ACTION = "com.example.intent.TRIGGER_WORLD_STEP_REASONING"
    BROADCAST_RECEIVER = (
        "com.example.iotcore/com.example.adbinterface.receiver.WorldStepReasoningReceiver"
    )
    LOG_TAG = "AgentResult"
    RESULT_REMOTE_PATH = (
        "/storage/emulated/0/Documents/NodeInfoResponse/action_result.json"
    )

    def __init__(self, env: interface.AsyncEnv, timeout: float = 30.0):
        super().__init__(env, name="AdbBroadcastAgent")
        self._timeout = timeout

    def _broadcast_goal(self, goal: str) -> None:
        """Sends the goal to the device via an explicit broadcast."""
        adb_utils.issue_generic_request(
            [
                "shell",
                "am",
                "broadcast",
                "-a",
                self.BROADCAST_ACTION,
                "-n",
                self.BROADCAST_RECEIVER,
                "--es",
                "goal",
                f'"{goal}"',
            ],
            self.env.controller,
        )

    def _wait_for_result(self) -> dict | None:
        adb_utils.issue_generic_request(["shell", "logcat", "-c"], self.env.controller)
        start = time.time()
        while time.time() - start < self._timeout:
            response = adb_utils.issue_generic_request(
                ["shell", "logcat", "-d", "-s", f"{self.LOG_TAG}:I", "*:S"],
                self.env.controller,
            )
            output = response.generic.output
            if output and self.LOG_TAG in output:
                try:
                    with file_utils.tmp_file_from_device(
                        self.RESULT_REMOTE_PATH, self.env.controller
                    ) as local_file:
                        with open(local_file, "r", encoding="utf-8") as f:
                            return json.load(f)
                except Exception as e:  # pylint: disable=broad-except
                    return {"error": str(e)}
            time.sleep(1.0)
        return None

    def step(self, goal: str) -> base_agent.AgentInteractionResult:
        self._broadcast_goal(goal)
        result = self._wait_for_result()
        done = result is not None
        step_data = {"result": result}
        return base_agent.AgentInteractionResult(done, step_data)
