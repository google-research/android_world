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

import os
from unittest import mock

from absl.testing import absltest
from android_env import env_interface
from android_world.env import adb_utils
from android_world.env import tools
from android_world.env.setup_device import apps
from android_world.env.setup_device import setup
from android_world.utils import app_snapshot
from android_world.utils import file_utils


class SetupTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_issue_generic_request = self.enter_context(
        mock.patch.object(adb_utils, 'issue_generic_request')
    )

  @mock.patch.object(file_utils, 'tmp_file_from_cns')
  @mock.patch.object(adb_utils, 'install_apk')
  def test_install_apk(
      self,
      mock_install_apk,
      mock_tmp_file_from_cns,
  ):
    env = mock.create_autospec(env_interface.AndroidEnvInterface)
    apk = 'example.apk'

    tmp_apk_file = '/tmp/example.apk'
    mock_tmp_file_from_cns.return_value.__enter__.return_value = tmp_apk_file
    setup._download_and_install_apk(apk, env)

    mock_tmp_file_from_cns.assert_called_once_with(
        os.path.join(apps.APP_DATA, apk),
    )
    mock_install_apk.assert_called_once_with(tmp_apk_file, env)

  @mock.patch.object(tools, 'AndroidToolController')
  @mock.patch.object(setup, '_download_and_install_apk')
  @mock.patch.object(app_snapshot, 'save_snapshot')
  def test_setup_apps(self, mock_save_snapshot, mock_install_apk, unused_tools):
    env = mock.create_autospec(env_interface.AndroidEnvInterface)
    mock_app_setups = {
        app_class: mock.patch.object(app_class, 'setup').start()
        for app_class in setup._APPS
    }

    setup.setup_apps(env)

    for app_class in setup._APPS:
      if app_class.apk_name:  # 1P apps do not have APKs.
        mock_install_apk.assert_any_call(app_class.apk_name, env)
      mock_app_setups[app_class].assert_any_call(env)
      mock_save_snapshot.assert_any_call(app_class.app_name, env)


if __name__ == '__main__':
  absltest.main()