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

from unittest import mock

from absl.testing import absltest
from android_env import env_interface
from android_env import loader
from android_env.components import config_classes
from android_world.env import env_launcher
from android_world.env import interface
from android_world.env import ui_tree_wrapper


class EnvLauncherTest(absltest.TestCase):

  @mock.patch.object(interface, "AsyncAndroidEnv", autospec=True)
  @mock.patch.object(ui_tree_wrapper, "UITreeWrapper", autospec=True)
  @mock.patch.object(loader, "load", autospec=True)
  def test_get_env(
      self,
      mock_loader,
      mock_tree_wrapper,
      mock_async_android_env,
  ):
    mock_android_env = mock.create_autospec(env_interface.AndroidEnvInterface)
    mock_loader.return_value = mock_android_env

    env_launcher._get_env(5556, "some_adb_path")

    mock_loader.assert_called_with(
        config=config_classes.AndroidEnvConfig(
            task=config_classes.FilesystemTaskConfig(
                path=ui_tree_wrapper._TASK_PATH
            ),
            simulator=config_classes.EmulatorConfig(
                emulator_launcher=config_classes.EmulatorLauncherConfig(
                    emulator_console_port=5556, adb_port=5557, grpc_port=8554
                ),
                adb_controller=config_classes.AdbControllerConfig(
                    adb_path="some_adb_path"
                ),
            ),
        )
    )
    mock_tree_wrapper.assert_called_with(mock_android_env)
    mock_async_android_env.assert_called_with(mock_tree_wrapper.return_value)


if __name__ == "__main__":
  absltest.main()
