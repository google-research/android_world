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

import datetime
import os
import shutil
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from android_env.proto import adb_pb2
from android_world.env import adb_utils
from android_world.utils import file_utils


class FilesTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_issue_generic_request = mock.patch.object(
        adb_utils, 'issue_generic_request'
    ).start()
    self.mock_env = mock.MagicMock()

  def tearDown(self):
    super().tearDown()
    mock.patch.stopall()

  def test_check_directory_exists(self):
    self.mock_issue_generic_request.return_value.generic.output.decode.return_value = (
        'Exists'
    )
    result = file_utils.check_directory_exists('/existing/path', self.mock_env)
    self.assertTrue(result)

    # Test case where directory does not exist
    self.mock_issue_generic_request.return_value.generic.output.decode.return_value = (
        'Does not exist'
    )
    result = file_utils.check_directory_exists(
        '/non/existing/path', self.mock_env
    )
    self.assertFalse(result)

  @mock.patch.object(os.path, 'exists')
  @mock.patch.object(file_utils, 'check_directory_exists')
  @mock.patch.object(shutil, 'rmtree')
  def test_tmp_directory_from_device(
      self, mock_rmtree, mock_check_directory_exists, mock_path_exists
  ):
    """Test if tmp_directory_from_device correctly copies a directory and handles exceptions."""
    mock_response = adb_pb2.AdbResponse()
    mock_response.status = adb_pb2.AdbResponse.OK
    self.mock_issue_generic_request.return_value = mock_response
    mock_path_exists.return_value = False
    mock_check_directory_exists.return_value = True

    tmp_local_directory = os.path.join(file_utils._TMP_LOCAL_LOCATION, 'dir')
    with file_utils.tmp_directory_from_device(
        '/remote/dir', self.mock_env
    ) as tmp_directory:
      self.assertEqual(tmp_local_directory, tmp_directory)
      self.mock_issue_generic_request.assert_called_with(
          ['pull', '/remote/dir', file_utils._TMP_LOCAL_LOCATION],
          self.mock_env,
          None,
      )
      mock_rmtree.assert_not_called()
    mock_rmtree.assert_called_with(tmp_local_directory)

    # Test FileExistsError
    mock_path_exists.return_value = True
    with self.assertRaises(FileExistsError):
      with file_utils.tmp_directory_from_device('/remote/dir', self.mock_env):
        pass

    # Test FileNotFoundError
    mock_path_exists.return_value = False
    mock_check_directory_exists.return_value = False
    with self.assertRaises(FileNotFoundError):
      with file_utils.tmp_directory_from_device(
          '/nonexistent/dir', self.mock_env
      ):
        pass

    # Test ADB RuntimeError
    mock_check_directory_exists.return_value = True
    self.mock_issue_generic_request.return_value.status = (
        adb_pb2.AdbResponse.ADB_ERROR
    )
    with self.assertRaises(RuntimeError):
      with file_utils.tmp_directory_from_device(
          '/remote/dir',
          self.mock_env,
      ):
        pass

  @mock.patch.object(os, 'path')
  def test_copy_data_to_device(self, mock_path):
    """Test if copy_data_to_device correctly copies data and handles exceptions."""
    mock_response = adb_pb2.AdbResponse()
    self.mock_issue_generic_request.return_value = mock_response
    mock_path.exists.return_value = True

    response = file_utils.copy_data_to_device(
        '/local/file_or_dir', '/remote/dir', self.mock_env
    )
    self.mock_issue_generic_request.assert_called_with(
        ['push', '/local/file_or_dir', '/remote/dir'], self.mock_env, None
    )
    self.assertEqual(response, mock_response)

    # Test FileNotFoundError
    mock_path.exists.return_value = False
    with self.assertRaises(FileNotFoundError):
      file_utils.copy_data_to_device(
          '/nonexistent/path', '/remote/dir', self.mock_env
      )

  @mock.patch.object(file_utils, 'check_directory_exists')
  def test_get_file_list_with_metadata(self, mock_check_directory_exists):
    mock_check_directory_exists.return_value = True
    self.mock_issue_generic_request.return_value = adb_pb2.AdbResponse(
        status=adb_pb2.AdbResponse.Status.OK,
        generic=adb_pb2.AdbResponse.GenericResponse(
            output=bytes(
                '-rw-rw---- 1 u0_a158 media_rw 0 2023-11-28 23:17:43.176000000'
                ' +0000 test.txt',
                'utf-8',
            )
        ),
    )
    file_list = file_utils.get_file_list_with_metadata(
        '/test_path', self.mock_env
    )
    self.mock_issue_generic_request.assert_called_with(
        'shell ls /test_path -ll -au', self.mock_env, None
    )
    self.assertLen(file_list, 1)
    self.assertEqual(file_list[0].file_name, 'test.txt')
    self.assertEqual(file_list[0].full_path, '/test_path/test.txt')
    self.assertEqual(
        file_list[0].change_time,
        datetime.datetime(2023, 11, 28, 23, 17, 43, 176000),
    )

  def test_check_file_content(self):
    self.mock_issue_generic_request.return_value = adb_pb2.AdbResponse(
        status=adb_pb2.AdbResponse.Status.OK,
        generic=adb_pb2.AdbResponse.GenericResponse(
            output=bytes(
                'test content.',
                'utf-8',
            )
        ),
    )

    res = file_utils.check_file_content(
        '/test_path/test_file', 'test content', self.mock_env
    )
    self.mock_issue_generic_request.assert_called_with(
        ['shell', 'cat', '/test_path/test_file'], self.mock_env, None
    )
    self.assertTrue(res)


if __name__ == '__main__':
  absltest.main()
