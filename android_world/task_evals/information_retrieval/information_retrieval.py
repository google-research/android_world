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

"""Evaluators for information retrieval tasks."""

import abc
from typing import Any
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.information_retrieval import activity_app_utils
from android_world.task_evals.information_retrieval import calendar_utils as calendar_utils_ir
from android_world.task_evals.information_retrieval import datetime_utils as datetime_utils_ir
from android_world.task_evals.information_retrieval import joplin_app_utils
from android_world.task_evals.information_retrieval import proto_utils
from android_world.task_evals.information_retrieval import task_app_utils
from android_world.task_evals.information_retrieval.proto import task_pb2
from android_world.task_evals.single.calendar import calendar_utils


class InformationRetrieval(task_eval.TaskEval, abc.ABC):
  """Task for information retrieval.

  Each information retrieval task is dynamically generated using the task
  parameters and success criteria are tailored to the specific requirements of
  the task. The class supports initializing tasks with app-specific states and
  handling conditional task logic based on the initial state's app context,
  particularly for apps like SimpleCalendarProApp.
  """

  template = ''
  complexity = 1
  schema = {}
  app_names = ()

  @property
  @abc.abstractmethod
  def task_template(self) -> task_pb2.Task:
    """The Task proto defining this Information Retrieval task."""

  @property
  def task(self) -> task_pb2.Task:
    return self._task

  def __init__(
      self,
      params: dict[str, Any],
  ):
    super().__init__(params)
    task = task_pb2.Task()
    task.CopyFrom(self.task_template)
    if task.relevant_state.state.HasField('calendar'):
      self.app_names = (task.relevant_state.state.calendar.app_name,)
    if task.relevant_state.state.HasField('tasks_app'):
      self.app_names = ('tasks',)
    if task.relevant_state.state.HasField('sports_activity_app'):
      self.app_names = ('open tracks sports tracker',)
    if task.relevant_state.state.HasField('notes_app'):
      self.app_names = ('joplin',)

  def initialize_task(
      self,
      env: interface.AsyncEnv,
  ) -> None:
    super().initialize_task(env)
    # Need to make a copy of the task template so that future runs aren't
    # affected.
    self._task = task_pb2.Task()
    self._task.CopyFrom(self.task_template)
    self.template = self._task.prompt
    self.complexity = self._task.complexity
    proto_utils.initialize_proto(self._task, self.params)
    _maybe_replace_date(self.params)
    if (
        self._task.relevant_state.state.HasField('calendar')
        and self._task.relevant_state.state.calendar.app_name
        == 'simple calendar pro'
    ):
      calendar_utils_ir.setup_task_state(
          self._task.relevant_state.state.calendar,
          list(self._task.relevant_state.exclusion_conditions),
          env.base_env,
      )
    if self._task.relevant_state.state.HasField('tasks_app'):
      task_app_utils.setup_task_state(
          self._task.relevant_state.state.tasks_app,
          list(self._task.relevant_state.exclusion_conditions),
          env.base_env,
      )
    if self._task.relevant_state.state.HasField('sports_activity_app'):
      activity_app_utils.setup_task_state(
          self._task.relevant_state.state.sports_activity_app,
          list(self._task.relevant_state.exclusion_conditions),
          env.base_env,
      )
    if self._task.relevant_state.state.HasField('notes_app'):
      joplin_app_utils.setup_task_state(
          self._task.relevant_state.state.notes_app,
          list(self._task.relevant_state.exclusion_conditions),
          env.base_env,
      )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    if not env.interaction_cache:
      return 0.0

    try:
      answers_are_equal = proto_utils.check_agent_answer(
          env.interaction_cache, self._task
      )
      return 1.0 if answers_are_equal else 0.0
    except ValueError:
      return 0.0

  def tear_down(self, env: interface.AsyncEnv) -> None:
    calendar_utils.clear_calendar_db(env.base_env)
    task_app_utils.clear_task_db(env.base_env)
    activity_app_utils.clear_db(env.base_env)
    joplin_app_utils.clear_dbs(env.base_env)
    super().tear_down(env)


def _maybe_replace_date(params: dict[str, Any]) -> None:
  """Maybe replaces date parameters with a natural language equivalent."""
  for param_name, param_value in params.items():
    if param_name == 'seed':
      continue
    try:
      if not param_value:
        continue
      params[param_name] = datetime_utils_ir.generate_reworded_date(param_value)
    except ValueError:
      pass  # Skip if there's no date parameter.
