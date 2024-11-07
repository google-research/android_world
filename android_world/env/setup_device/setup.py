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
from typing import Type

from absl import logging
from android_env import env_interface
from android_env.components import errors
from android_world.env import adb_utils
from android_world.env import interface
from android_world.env.setup_device import apps
from android_world.utils import app_snapshot

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


def get_app_mapping(app_name: str) -> Type[apps.AppSetup]:
  mapping = {app.app_name: app for app in _APPS}
  return mapping[app_name]


def download_and_install_apk(
    apk: str, raw_env: env_interface.AndroidEnvInterface
) -> None:
  """Downloads APK from remote location and installs it."""
  path = apps.download_app_data(apk)
  adb_utils.install_apk(path, raw_env)


def setup_app(app: Type[apps.AppSetup], env: interface.AsyncEnv) -> None:
  """Sets up a single app."""
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
  app_snapshot.save_snapshot(app.app_name, env.controller)


def maybe_install_app(
    app: Type[apps.AppSetup], env: interface.AsyncEnv
) -> None:
  """Installs all APKs for Android World."""
  if not app.apk_names:  # Ignore 1p apps that don't have an APK.
    return
  print(f"Installing app: {app.app_name}.")
  apk_installed = False
  for apk_name in app.apk_names:
    try:
      download_and_install_apk(apk_name, env.controller.env)
      apk_installed = True
      break
    except errors.AdbControllerError:
      # Try apk compiled for a different architecture, e.g., Mac M1.
      continue
  if not apk_installed:
    raise RuntimeError(f"Failed to download and install APK for {app.app_name}")


def setup_apps(env: interface.AsyncEnv) -> None:
  """Sets up apps for Android World.

  Args:
    env: The Android environment.

  Raises:
    RuntimeError: If cannot install APK.
  """
  # Make sure quick-settings are not displayed, which can override foreground
  # apps, and impede UI navigation required for setting up.
  adb_utils.press_home_button(env.controller)
  adb_utils.set_root_if_needed(env.controller)

  print(
      "Installing and setting up applications on Android device. Please do not"
      " interact with device while installation is running."
  )
  for app in _APPS:
    maybe_install_app(app, env)
    setup_app(app, env)
