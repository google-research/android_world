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

"""Checkpointer class."""

import abc
import datetime
import gzip
import io
import os
import pickle
from typing import Any

from absl import logging


Episode = dict[str, Any]


def _gzip_pickle(data: Any) -> bytes:
  """Pickle and gzip compress an object in memory.

  Args:
      data: The data to be pickled and gzipped.

  Returns:
      A bytes object containing the gzipped pickled data.
  """
  pickled_data = io.BytesIO()
  pickle.dump(data, pickled_data)

  pickled_data.seek(0)  # Reset the stream position to the beginning
  compressed_data = io.BytesIO()
  with gzip.GzipFile(
      fileobj=compressed_data, mode='wb', compresslevel=5
  ) as f_out:
    f_out.write(pickled_data.getvalue())

  return compressed_data.getvalue()


def _unzip_and_read_pickle(file_path: str) -> Any:
  """Reads a gzipped pickle file using 'with open', unzips, and unpickles it.

  Args:
      file_path: The path to the gzipped pickle file.

  Returns:
      The original Python object that was pickled and gzipped.
  """
  with open(file_path, 'rb') as f:
    compressed = f.read()

  with gzip.open(io.BytesIO(compressed), 'rb') as f_in:
    return pickle.load(f_in)


class Checkpointer(abc.ABC):
  """Saves and loads the results of an evaluation run."""

  @abc.abstractmethod
  def save_episodes(self, task_episodes: list[Episode], task_name: str) -> None:
    """Saves a task's episodes to disk."""

  @abc.abstractmethod
  def load(self) -> list[Episode]:
    """Loads all episodes from disk."""


class IncrementalCheckpointer(Checkpointer):
  """Saves and loads the results of an evaluation run.

  Designed for incremental saving of episodes for each task, enabling the
  checkpointer to save the results of an evaluation run task by task, rather
  than saving the entire dataset at once.

  Attributes:
      directory: The directory to store the task data.
  """

  def __init__(self, directory: str) -> None:
    self.directory = directory
    os.makedirs(directory, exist_ok=True)

  def save_episodes(self, task_episodes: list[Episode], task_name: str):
    """Saves a task group to disk.

    Args:
        task_episodes: The task's episodes to save.
        task_name: The unique identifier for the task group.
    """
    filename = os.path.join(self.directory, f'{task_name}.pkl.gz')
    with open(filename, 'wb') as f:
      compressed = _gzip_pickle(task_episodes)
      f.write(compressed)
    print(f'Wrote task episodes for {task_name} to {filename}')

  def load(self) -> list[Episode]:
    """Loads all task groups from disk."""
    data = []
    for filename in os.listdir(self.directory):
      if filename.endswith('.pkl.gz'):
        task_group_id = filename[:-7]  # Remove ".pkl.gz" extension
        task_group = self._load_task_group(task_group_id)
        data.extend(task_group)
    return data

  def _load_task_group(self, task_group_id: str) -> list[Episode]:
    """Loads a single task group from disk."""
    filename = os.path.join(self.directory, f'{task_group_id}.pkl.gz')
    try:
      return _unzip_and_read_pickle(filename)
    except FileNotFoundError:
      logging.info(
          'File not readable: %s. It may not exist. Starting from empty state.',
          filename,
      )
      return []


class NullCheckpointer(Checkpointer):
  """Checkpointer that does nothing."""

  def __init__(self) -> None:
    """Constructor."""

  def save_episodes(self, task_episodes: list[Episode], task_name: str):
    pass

  def load(self) -> list[Episode]:
    return []


def create_run_directory(location: str) -> str:
  """Creates the UUID directory name to save run results.

  Args:
    location: Location to write the directory.

  Returns:
    A UUID directory name.
  """
  timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
  return os.path.join(location, f'run_{timestamp}')


class DeprecatedCheckpointer:
  """Saves and loads the results of an evaluation run.

  Attributes:
    filename: The name of the file to write.
  """

  def __init__(self, filename: str) -> None:
    self.filename = filename

  def save(self, data: list[Episode], completed_tasks: list[str]) -> None:
    """Saves the results of an evaluation run.

    Args:
      data: The data for the run.
      completed_tasks: Metadata containing the tuple of completed tasks.
    """
    with open(self.filename, 'wb') as f:
      compressed = _gzip_pickle((data, completed_tasks))
      f.write(compressed)
    print(f'Wrote to {self.filename}')

  def load(
      self,
  ) -> tuple[list[Episode], list[str]]:
    """Loads the results of an evaluation run."""
    try:
      return _unzip_and_read_pickle(self.filename)
    except FileNotFoundError:
      logging.info(
          'File not readable: %s. It may not exist. Starting from empty state.',
          self.filename,
      )
      return [], []
