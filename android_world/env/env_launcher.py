# Copyright 2024 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Launches the environment used in the benchmark."""


from android_world.env import adb_utils
from android_world.env import interface
from android_world.env import ui_tree_wrapper
from android_world.env.setup_device import setup
from android_world.utils import datetime_utils


# AndroidWorld is tested and developed on Pixel 6 with API 33. Other
# configurations may be supported, but are not yet tested.
_ANDROID_WORLD_API_LEVEL = 33


def _get_env(console_port: int, adb_path: str) -> interface.AsyncEnv:
  """Creates an AsyncEnv by connecting to an existing Android environment."""
  wrapped = ui_tree_wrapper.get_wrapped(console_port, adb_path)
  return interface.AsyncAndroidEnv(wrapped)


def verify_api_level(env: interface.AsyncEnv) -> None:
  """Verifies that the emulator's API level is expected."""
  level = adb_utils.get_api_level(env.base_env)
  if level != _ANDROID_WORLD_API_LEVEL:
    raise ValueError(
        f'Emulator API level must be {_ANDROID_WORLD_API_LEVEL}, but found'
        f' {level}.'
    )


def load_and_setup_env(
    console_port: int = 5554,
    emulator_setup: bool = False,
    freeze_datetime: bool = True,
    adb_path: str = ui_tree_wrapper.DEFAULT_ADB_PATH,
) -> interface.AsyncEnv:
  """Create environment with `get_env()` and perform env setup and validation.

  Before running this, an emulator must be launched. For example:

  ```
  AVD_NAME=Pixel_6_API_33  # First create an AVD in Android Studio.
  ~/Android/Sdk/emulator/emulator -avd $AVD_NAME -no-snapshot -grpc 8554
  ```

  Args:
    console_port: The console port of the existing device. This can usually be
      retrieved by looking at the output of `adb devices`. In general, the first
      connected device is port 5554, the second is 5556, and so on.
    emulator_setup: Perform first-time app setup on the environment if True.
    freeze_datetime: Whether to freeze the datetime to a fixed time, October
      2023, to ensure consistent benchmarking.
    adb_path: The location of the adb binary.

  Returns:
    An interactable Android environment.
  """
  env = _get_env(console_port, adb_path)
  if emulator_setup:
    setup.setup_apps(env.base_env)
  if freeze_datetime:
    datetime_utils.setup_datetime(env.base_env)
  return env
