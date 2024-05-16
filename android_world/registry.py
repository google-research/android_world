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

"""Registers the task classes."""

import types
from typing import Any

from android_world.task_evals import task_eval
from android_world.task_evals.composite import markor_sms
from android_world.task_evals.composite import system as system_composite
from android_world.task_evals.information_retrieval import information_retrieval_registry
from android_world.task_evals.miniwob import miniwob_registry
from android_world.task_evals.robustness_study import goal_template_variation
from android_world.task_evals.robustness_study import screen_variation
from android_world.task_evals.single import audio_recorder
from android_world.task_evals.single import browser
from android_world.task_evals.single import camera
from android_world.task_evals.single import clock
from android_world.task_evals.single import contacts
from android_world.task_evals.single import expense
from android_world.task_evals.single import files
from android_world.task_evals.single import markor
from android_world.task_evals.single import osmand
from android_world.task_evals.single import phone
from android_world.task_evals.single import recipe
from android_world.task_evals.single import retro_music
from android_world.task_evals.single import simple_draw_pro
from android_world.task_evals.single import simple_gallery_pro
from android_world.task_evals.single import sms
from android_world.task_evals.single import system
from android_world.task_evals.single import vlc
from android_world.task_evals.single.calendar import calendar

# The AndroidWorld family.
ANDROID_WORLD_FAMILY = 'android_world'  # Entire suite.
ANDROID_FAMILY = 'android'  # Subset.
INFORMATION_RETRIEVAL_FAMILY = 'information_retrieval'  # Subset.

# The MiniWoB family.
MINIWOB_FAMILY = 'miniwob'
MINIWOB_FAMILY_SUBSET = 'miniwob_subset'

# Experiment definitions for robustness experiments.
VARY_TEMPLATE_FAMILY = 'vary_template'
VARY_SCREEN_FAMILY = 'vary_screen'

# Task registries; they contain a mapping from each task name to its class,
# to construct instances of a task.
ANDROID_TASK_REGISTRY = {}
INFORMATION_RETRIEVAL_TASK_REGISTRY = (
    information_retrieval_registry.TASK_REGISTRY
)
MINIWOB_TASK_REGISTRY = miniwob_registry.TASK_REGISTRY
VARY_TEMPLATE_REGISTRY = {}
VARY_SCREEN_REGISTRY = {}


def get_registry(family: str) -> Any:
  """Gets the task registry for the given family.

  Args:
    family: The family.

  Returns:
    Task registry.

  Raises:
    ValueError: If provided family doesn't exist.
  """
  if family == ANDROID_WORLD_FAMILY:
    return {**ANDROID_TASK_REGISTRY, **INFORMATION_RETRIEVAL_TASK_REGISTRY}
  elif family == ANDROID_FAMILY:
    return ANDROID_TASK_REGISTRY
  elif family == VARY_TEMPLATE_FAMILY:
    return VARY_TEMPLATE_REGISTRY
  elif family == MINIWOB_FAMILY:
    return MINIWOB_TASK_REGISTRY
  elif family == MINIWOB_FAMILY_SUBSET:
    return miniwob_registry.TASK_REGISTRY_SUBSET
  elif family == INFORMATION_RETRIEVAL_FAMILY:
    return INFORMATION_RETRIEVAL_TASK_REGISTRY
  elif family == VARY_SCREEN_FAMILY:
    return VARY_SCREEN_REGISTRY
  else:
    raise ValueError(f'Unsupported family: {family}')


_TASKS = (
    # keep-sorted start
    audio_recorder.AudioRecorderRecordAudio,
    audio_recorder.AudioRecorderRecordAudioWithFileName,
    browser.BrowserDraw,
    browser.BrowserMaze,
    browser.BrowserMultiply,
    calendar.SimpleCalendarAddOneEvent,
    calendar.SimpleCalendarAddOneEventInTwoWeeks,
    calendar.SimpleCalendarAddOneEventRelativeDay,
    calendar.SimpleCalendarAddOneEventTomorrow,
    calendar.SimpleCalendarAddRepeatingEvent,
    calendar.SimpleCalendarDeleteEvents,
    calendar.SimpleCalendarDeleteEventsOnRelativeDay,
    calendar.SimpleCalendarDeleteOneEvent,
    camera.CameraTakePhoto,
    camera.CameraTakeVideo,
    clock.ClockStopWatchPausedVerify,
    clock.ClockStopWatchRunning,
    clock.ClockTimerEntry,
    contacts.ContactsAddContact,
    contacts.ContactsNewContactDraft,
    expense.ExpenseAddMultiple,
    expense.ExpenseAddMultipleFromGallery,
    expense.ExpenseAddMultipleFromMarkor,
    expense.ExpenseAddSingle,
    expense.ExpenseDeleteDuplicates,
    expense.ExpenseDeleteDuplicates2,
    expense.ExpenseDeleteMultiple,
    expense.ExpenseDeleteMultiple2,
    expense.ExpenseDeleteSingle,
    files.FilesDeleteFile,
    files.FilesMoveFile,
    markor.MarkorAddNoteHeader,
    markor.MarkorChangeNoteContent,
    markor.MarkorCreateFolder,
    markor.MarkorCreateNote,
    markor.MarkorCreateNoteFromClipboard,
    markor.MarkorDeleteAllNotes,
    markor.MarkorDeleteNewestNote,
    markor.MarkorDeleteNote,
    markor.MarkorEditNote,
    markor.MarkorMergeNotes,
    markor.MarkorMoveNote,
    markor.MarkorTranscribeReceipt,
    markor.MarkorTranscribeVideo,
    # Markor composite tasks.
    markor_sms.MarkorCreateNoteAndSms,
    # OsmAnd.
    osmand.OsmAndFavorite,
    osmand.OsmAndMarker,
    osmand.OsmAndTrack,
    recipe.RecipeAddMultipleRecipes,
    recipe.RecipeAddMultipleRecipesFromImage,
    recipe.RecipeAddMultipleRecipesFromMarkor,
    recipe.RecipeAddMultipleRecipesFromMarkor2,
    recipe.RecipeAddSingleRecipe,
    recipe.RecipeDeleteDuplicateRecipes,
    recipe.RecipeDeleteDuplicateRecipes2,
    recipe.RecipeDeleteDuplicateRecipes3,
    recipe.RecipeDeleteMultipleRecipes,
    recipe.RecipeDeleteMultipleRecipesWithConstraint,
    recipe.RecipeDeleteMultipleRecipesWithNoise,
    recipe.RecipeDeleteSingleRecipe,
    recipe.RecipeDeleteSingleWithRecipeWithNoise,
    retro_music.RetroCreatePlaylist,
    retro_music.RetroPlayingQueue,
    retro_music.RetroPlaylistDuration,
    retro_music.RetroSavePlaylist,
    simple_draw_pro.SimpleDrawProCreateDrawing,
    simple_gallery_pro.SaveCopyOfReceiptTaskEval,
    sms.SimpleSmsReply,
    sms.SimpleSmsReplyMostRecent,
    sms.SimpleSmsResend,
    sms.SimpleSmsSend,
    sms.SimpleSmsSendClipboardContent,
    sms.SimpleSmsSendReceivedAddress,
    system.OpenAppTaskEval,
    system.SystemBluetoothTurnOff,
    system.SystemBluetoothTurnOffVerify,
    system.SystemBluetoothTurnOn,
    system.SystemBluetoothTurnOnVerify,
    system.SystemBrightnessMax,
    system.SystemBrightnessMaxVerify,
    system.SystemBrightnessMin,
    system.SystemBrightnessMinVerify,
    system.SystemCopyToClipboard,
    system.SystemWifiTurnOff,
    system.SystemWifiTurnOffVerify,
    system.SystemWifiTurnOn,
    system.SystemWifiTurnOnVerify,
    system_composite.TurnOffWifiAndTurnOnBluetooth,
    system_composite.TurnOnWifiAndOpenApp,
    # keep-sorted end
    # VLC media player tasks.
    vlc.VlcCreatePlaylist,
    vlc.VlcCreateTwoPlaylists,
    # Phone operations are flaky and the root cause is not known. Disabling
    # until resolution.
    # phone.MarkorCallApartment,
    # phone.PhoneAnswerCall,
    # phone.PhoneCallTextSender,
    # phone.PhoneMakeCall,
    # phone.PhoneRedialNumber,
    # phone.PhoneReturnMissedCall,
    # sms.SimpleSmsSendAfterCall,
)


def register_task(task_class: type[task_eval.TaskEval]) -> None:
  """Registers the task class.

  Args:
    task_class: The class to register.
  """
  ANDROID_TASK_REGISTRY[task_class.__name__] = task_class


for task in _TASKS:
  register_task(task)


## For robustness experiments. #################################################

_ANDROID_TASKS_SUBSET = (
    calendar.SimpleCalendarAddOneEventRelativeDay,
    calendar.SimpleCalendarDeleteOneEvent,
    expense.ExpenseDeleteDuplicates,
    markor.MarkorCreateNote,
    markor.MarkorDeleteNewestNote,
    phone.MarkorCallApartment,
    osmand.OsmAndMarker,
    simple_gallery_pro.SaveCopyOfReceiptTaskEval,
    sms.SimpleSmsReplyMostRecent,
    sms.SimpleSmsResend,
    sms.SimpleSmsSendReceivedAddress,
    system_composite.TurnOnWifiAndOpenApp,
)


def _create_task_for_goal_variation(
    new_class_name: str,
    base_task: Any,
    template: str,
    params: dict[str, Any],
) -> type[task_eval.TaskEval]:
  return type(
      new_class_name,
      (base_task,),
      {
          'generate_random_params': lambda: params,
          'template': template,
      },
  )


# Register tasks for goal variation robustness experiments.
for task in _ANDROID_TASKS_SUBSET:
  fixed_params = task.generate_random_params()

  for wrapper_name, wrapper_config in screen_variation.SCREEN_MODIFIERS.items():
    temp_task_name = task.__name__ + '_' + wrapper_name

    VARY_SCREEN_REGISTRY[temp_task_name] = (
        screen_variation.generate_screen_variation_wrapper(
            task,
            wrapper_config['width'],
            wrapper_config['height'],
            wrapper_config['orientation'],
            fixed_params,
            wrapper_name,
        )
    )

  if task.__name__ not in goal_template_variation.ADDITIONAL_TASK_TEMPLATES:
    continue

  for i, new_template in enumerate(
      [task.template]
      + goal_template_variation.ADDITIONAL_TASK_TEMPLATES[task.__name__]
  ):
    temp_task_name = task.__name__ + '_' + str(i)

    temp_task = _create_task_for_goal_variation(
        temp_task_name, task, new_template, fixed_params
    )

    VARY_TEMPLATE_REGISTRY[temp_task_name] = temp_task

# Add names with "." notation for autocomplete in Colab.
names = types.SimpleNamespace(**{
    k: k
    for k in {
        **ANDROID_TASK_REGISTRY,
        **VARY_SCREEN_REGISTRY,
        **VARY_TEMPLATE_REGISTRY,
        **INFORMATION_RETRIEVAL_TASK_REGISTRY,
        **MINIWOB_TASK_REGISTRY,
        **MINIWOB_TASK_REGISTRY,
    }
})
