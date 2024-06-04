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

"""Utils for testing database logic."""

import os
import sqlite3
import tempfile

from android_world.env import device_constants
from android_world.task_evals.utils import sqlite_schema_utils


def setup_test_db() -> str:
  """Setup test database."""
  # Create a temporary directory
  temp_dir = tempfile.mkdtemp()

  # Path for the new database
  db_path = os.path.join(temp_dir, 'events.db')

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  cursor.execute('DROP TABLE IF EXISTS events')
  cursor.execute("""
  CREATE TABLE `events` (
      `id` INTEGER PRIMARY KEY AUTOINCREMENT,
      `start_ts` INTEGER NOT NULL,
      `end_ts` INTEGER NOT NULL,
      `title` TEXT NOT NULL,
      `location` TEXT NOT NULL,
      `description` TEXT NOT NULL,
      `reminder_1_minutes` INTEGER NOT NULL,
      `reminder_2_minutes` INTEGER NOT NULL,
      `reminder_3_minutes` INTEGER NOT NULL,
      `reminder_1_type` INTEGER NOT NULL,
      `reminder_2_type` INTEGER NOT NULL,
      `reminder_3_type` INTEGER NOT NULL,
      `repeat_interval` INTEGER NOT NULL,
      `repeat_rule` INTEGER NOT NULL,
      `repeat_limit` INTEGER NOT NULL,
      `repetition_exceptions` TEXT NOT NULL,
      `attendees` TEXT NOT NULL,
      `import_id` TEXT NOT NULL,
      `time_zone` TEXT NOT NULL,
      `flags` INTEGER NOT NULL,
      `event_type` INTEGER NOT NULL,
      `parent_id` INTEGER NOT NULL,
      `last_updated` INTEGER NOT NULL,
      `source` TEXT NOT NULL,
      `availability` INTEGER NOT NULL,
      `color` INTEGER NOT NULL,
      `type` INTEGER NOT NULL
  )
  """)

  events = [
      (
          1,
          1672621200,
          1672624800,
          'Dinner',
          'Soho Bistro',
          '',
          -1,
          -1,
          -1,
          0,
          0,
          0,
          0,
          0,
          0,
          '[]',
          '',
          'b28b0ba9-86f3-41ab-8136-46d6fe7a7059',
          device_constants.TIMEZONE,
          0,
          1,
          0,
          0,
          'imported-ics',
          0,
          0,
          0,
      ),
      (
          2,
          1672686000,
          1672689600,
          'Work Meeting',
          'Office',
          '',
          -1,
          -1,
          -1,
          0,
          0,
          0,
          0,
          0,
          0,
          '[]',
          '',
          'd49db91f-78ef-4f65-9e04-570778345d64',
          device_constants.TIMEZONE,
          0,
          1,
          0,
          0,
          'imported-ics',
          0,
          0,
          0,
      ),
      (
          3,
          1672707600,
          1672714800,
          'Pottery Class',
          'Pottery Studio in Brooklyn',
          '',
          -1,
          -1,
          -1,
          0,
          0,
          0,
          0,
          0,
          0,
          '[]',
          '',
          'a70b701a-49ad-4d91-b8a2-b7b36a6bf2bf',
          device_constants.TIMEZONE,
          0,
          1,
          0,
          0,
          'imported-ics',
          0,
          0,
          0,
      ),
      (
          4,
          1672704000,
          1672711200,
          'Pottery Class',
          'Pottery Studio in Brooklyn',
          '',
          -1,
          -1,
          -1,
          0,
          0,
          0,
          0,
          0,
          0,
          '[]',
          '',
          '819ca499-9af7-4a3f-8f9e-27b79eb77872',
          device_constants.TIMEZONE,
          0,
          1,
          0,
          0,
          'imported-ics',
          0,
          0,
          0,
      ),
      (
          5,
          1672794000,
          1672797600,
          'Dinner',
          'East Village Restaurant',
          '',
          -1,
          -1,
          -1,
          0,
          0,
          0,
          0,
          0,
          0,
          '[]',
          '',
          '2a65cbd7-a261-42c5-995d-5522ec0a7803',
          device_constants.TIMEZONE,
          0,
          1,
          0,
          0,
          'imported-ics',
          0,
          0,
          0,
      ),
  ]
  cursor.executemany(
      'INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,'
      ' ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      events,
  )

  # Commit the changes and close the connection
  conn.commit()
  conn.close()
  return db_path


def get_db_rows() -> list[sqlite_schema_utils.CalendarEvent]:
  """Gets test database rows."""
  return [
      sqlite_schema_utils.CalendarEvent(
          id=1,
          start_ts=1672621200,
          end_ts=1672624800,
          title='Dinner',
          location='Soho Bistro',
          description='',
          reminder_1_minutes=-1,
          reminder_2_minutes=-1,
          reminder_3_minutes=-1,
          reminder_1_type=0,
          reminder_2_type=0,
          reminder_3_type=0,
          repeat_interval=0,
          repeat_rule=0,
          repeat_limit=0,
          repetition_exceptions='[]',
          attendees='',
          import_id='b28b0ba9-86f3-41ab-8136-46d6fe7a7059',
          time_zone=device_constants.TIMEZONE,
          flags=0,
          event_type=1,
          parent_id=0,
          last_updated=0,
          source='imported-ics',
          availability=0,
          color=0,
          type=0,
      ),
      sqlite_schema_utils.CalendarEvent(
          id=2,
          start_ts=1672686000,
          end_ts=1672689600,
          title='Work Meeting',
          location='Office',
          description='',
          reminder_1_minutes=-1,
          reminder_2_minutes=-1,
          reminder_3_minutes=-1,
          reminder_1_type=0,
          reminder_2_type=0,
          reminder_3_type=0,
          repeat_interval=0,
          repeat_rule=0,
          repeat_limit=0,
          repetition_exceptions='[]',
          attendees='',
          import_id='d49db91f-78ef-4f65-9e04-570778345d64',
          time_zone=device_constants.TIMEZONE,
          flags=0,
          event_type=1,
          parent_id=0,
          last_updated=0,
          source='imported-ics',
          availability=0,
          color=0,
          type=0,
      ),
      sqlite_schema_utils.CalendarEvent(
          id=3,
          start_ts=1672707600,
          end_ts=1672714800,
          title='Pottery Class',
          location='Pottery Studio in Brooklyn',
          description='',
          reminder_1_minutes=-1,
          reminder_2_minutes=-1,
          reminder_3_minutes=-1,
          reminder_1_type=0,
          reminder_2_type=0,
          reminder_3_type=0,
          repeat_interval=0,
          repeat_rule=0,
          repeat_limit=0,
          repetition_exceptions='[]',
          attendees='',
          import_id='a70b701a-49ad-4d91-b8a2-b7b36a6bf2bf',
          time_zone=device_constants.TIMEZONE,
          flags=0,
          event_type=1,
          parent_id=0,
          last_updated=0,
          source='imported-ics',
          availability=0,
          color=0,
          type=0,
      ),
      sqlite_schema_utils.CalendarEvent(
          id=4,
          start_ts=1672704000,
          end_ts=1672711200,
          title='Pottery Class',
          location='Pottery Studio in Brooklyn',
          description='',
          reminder_1_minutes=-1,
          reminder_2_minutes=-1,
          reminder_3_minutes=-1,
          reminder_1_type=0,
          reminder_2_type=0,
          reminder_3_type=0,
          repeat_interval=0,
          repeat_rule=0,
          repeat_limit=0,
          repetition_exceptions='[]',
          attendees='',
          import_id='819ca499-9af7-4a3f-8f9e-27b79eb77872',
          time_zone=device_constants.TIMEZONE,
          flags=0,
          event_type=1,
          parent_id=0,
          last_updated=0,
          source='imported-ics',
          availability=0,
          color=0,
          type=0,
      ),
      sqlite_schema_utils.CalendarEvent(
          id=5,
          start_ts=1672794000,
          end_ts=1672797600,
          title='Dinner',
          location='East Village Restaurant',
          description='',
          reminder_1_minutes=-1,
          reminder_2_minutes=-1,
          reminder_3_minutes=-1,
          reminder_1_type=0,
          reminder_2_type=0,
          reminder_3_type=0,
          repeat_interval=0,
          repeat_rule=0,
          repeat_limit=0,
          repetition_exceptions='[]',
          attendees='',
          import_id='2a65cbd7-a261-42c5-995d-5522ec0a7803',
          time_zone=device_constants.TIMEZONE,
          flags=0,
          event_type=1,
          parent_id=0,
          last_updated=0,
          source='imported-ics',
          availability=0,
          color=0,
          type=0,
      ),
  ]