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

"""Setup tool for Android World.

It does the following:

* APK Management: Automates installations of apks needed for Android World.
* Sets up environment: Configures emulator with necessary permissions, using adb
  and basic automation.
"""

import os

from absl import logging
from android_env import env_interface
from android_env.components import errors
from android_world.env import adb_utils
from android_world.env.setup_device import apps
from android_world.utils import app_snapshot
from android_world.utils import file_utils

# APKs required for Android World.
_APPS = (
    # keep-sorted start
    apps.AndroidWorldApp,
    apps.AudioRecorder,
    apps.CameraApp,
    apps.ChromeApp,
    apps.ClipperApp,
    apps.ClockApp,
    apps.ContactsApp,
    apps.DialerApp,
    apps.ExpenseApp,
    apps.FilesApp,
    apps.JoplinApp,
    apps.MarkorApp,
    apps.MiniWobApp,
    apps.OpenTracksApp,
    apps.OsmAndApp,
    apps.RecipeApp,
    apps.RetroMusicApp,
    apps.SettingsApp,
    apps.SimpleCalendarProApp,
    apps.SimpleDrawProApp,
    apps.SimpleGalleryProApp,
    apps.SimpleSMSMessengerApp,
    apps.TasksApp,
    apps.VlcApp,
    # keep-sorted end
)


def _download_and_install_apk(
    apk: str, env: env_interface.AndroidEnvInterface
) -> None:
  """Downloads all APKs from remote location and installs them."""
  path = apps.download_app_data(apk)
  adb_utils.install_apk(path, env)


def _install_all_apks(env: env_interface.AndroidEnvInterface) -> None:
  """Installs all APKs for Android World."""
  print("Downloading app data and installing apps. This make take a few mins.")
  for app in _APPS:
    if not app.apk_names:  # Ignore 1p apps that don't have an APK.
      continue
    apk_installed = False
    for apk_name in app.apk_names:
      try:
        _download_and_install_apk(apk_name, env)
        apk_installed = True
        break
      except errors.AdbControllerError:
        # Try apk compiled for a different architecture, e.g., Mac M1.
        continue
    if not apk_installed:
      raise RuntimeError(
          f"Failed to download and install APK for {app.app_name}"
      )


def setup_apps(env: env_interface.AndroidEnvInterface) -> None:
  """Sets up apps for Android World.

  Args:
    env: The Android environment.

  Raises:
    RuntimeError: If cannot install APK.
  """
  # Make sure quick-settings are not displayed, which can override foreground
  # apps, and impede UI navigation required for setting up.
  adb_utils.press_home_button(env)
  adb_utils.issue_generic_request(["root"], env)

  _install_all_apks(env)

  print(
      "Setting up applications on Android device. Please do not interact with"
      " device while installation is running."
  )
  for app in _APPS:
    try:
      logging.info("Setting up app %s", app.app_name)
      app.setup(env)
    except ValueError as e:
      logging.warning(
          "Failed to automatically setup app %s: %s.\n\nYou will need to"
          " manually setup the app.",
          app.app_name,
          e,
      )
    app_snapshot.save_snapshot(app.app_name, env)
