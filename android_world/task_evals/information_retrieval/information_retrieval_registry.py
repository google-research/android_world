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

"""Information retrieval registry; it dynamically creates tasks.

Information retrieval tasks are defined in a textproto file. For each task in
the proto,
we dynamically create a new task with the name of the task in the class name.
"""

import os
import random
from typing import Any
from android_world.task_evals.information_retrieval import information_retrieval
from android_world.task_evals.information_retrieval.proto import task_pb2
from google.protobuf import text_format

TASK_REGISTRY = {}


def _read_tasks() -> task_pb2.Tasks:
  proto = task_pb2.Tasks()
  script_dir = os.path.dirname(os.path.abspath(__file__))
  local_path = os.path.join(script_dir, 'proto', 'tasks.textproto')
  with open(local_path, 'r') as f:
    textproto_content = f.read()
  text_format.Merge(textproto_content, proto)
  return proto

_RAW_TASKS = _read_tasks()


def _build_task_class(
    task_proto: task_pb2.Task,
) -> information_retrieval.InformationRetrieval:
  """Dynamically builds and returns a new subclass of InformationRetrieval.

  This function creates a subclass of InformationRetrieval from the task.

  Args:
    task_proto: The task proto defining the class to be created.

  Returns:
    A subclass of InformationRetrieval that is dynamically created.
  """

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:  # pylint:disable=unused-argument
    params = {}
    for task_param in task_proto.task_params:
      params[task_param.name] = random.choice(list(task_param.possible_values))
    return params

  @property
  def task_template(self) -> task_pb2.Task:  # pylint:disable=unused-argument
    return task_proto

  return type(
      task_proto.name,
      (information_retrieval.InformationRetrieval,),
      {
          'generate_random_params': generate_random_params,
          'task_template': task_template,
      },
  )


for raw_task in _RAW_TASKS.tasks:
  task_class = _build_task_class(raw_task)
  TASK_REGISTRY[raw_task.name] = task_class
