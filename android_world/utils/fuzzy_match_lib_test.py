# Copyright 2026 The android_world Authors.
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

"""Tests for fuzzy_match_lib."""

from absl.testing import absltest
from absl.testing import parameterized
from android_world.utils import fuzzy_match_lib


class FuzzyMatchTest(parameterized.TestCase):

  @parameterized.parameters(
      ('Joanne', 'Ann'),
      ('Joanne', 'Jo'),
      ('Jonathan', 'Nathan'),
      ('Christopher', 'Chris'),
      ('Dan', 'Daniel'),
  )
  def test_fuzzy_match_rejects_substrings(self, text1: str, text2: str):
    # A substring relationship must not count as a match for shared fields
    # (regression for the PR that scored these via partial_ratio).
    self.assertFalse(fuzzy_match_lib.fuzzy_match(text1, text2))

  def test_fuzzy_match_accepts_equal(self):
    self.assertTrue(fuzzy_match_lib.fuzzy_match('Urgent', 'Urgent'))

  def test_fuzzy_match_ignores_case(self):
    self.assertTrue(fuzzy_match_lib.fuzzy_match('Hi', 'hi'))

  def test_fuzzy_match_rejects_different(self):
    self.assertFalse(fuzzy_match_lib.fuzzy_match('Coffee', 'Lunch'))

  def test_fuzzy_match_empty_strings(self):
    # Empty == empty restores the original difflib behavior.
    self.assertTrue(fuzzy_match_lib.fuzzy_match('', ''))
    self.assertFalse(fuzzy_match_lib.fuzzy_match('', 'x'))
    self.assertFalse(fuzzy_match_lib.fuzzy_match('x', ''))

  def test_fuzzy_match_none(self):
    self.assertFalse(fuzzy_match_lib.fuzzy_match(None, 'x'))
    self.assertFalse(fuzzy_match_lib.fuzzy_match('x', None))
    self.assertFalse(fuzzy_match_lib.fuzzy_match(None, None))


class FuzzyMatchSubstringTest(parameterized.TestCase):

  def test_fuzzy_match_substring_accepts_suffix(self):
    # Expense note where the agent appends the ". Reimbursable." marker.
    self.assertTrue(
        fuzzy_match_lib.fuzzy_match_substring('Urgent', 'Urgent. Reimbursable.')
    )

  def test_fuzzy_match_substring_accepts_equal(self):
    self.assertTrue(fuzzy_match_lib.fuzzy_match_substring('Urgent', 'Urgent'))

  def test_fuzzy_match_substring_ignores_case(self):
    self.assertTrue(fuzzy_match_lib.fuzzy_match_substring('Hi', 'hi'))

  def test_fuzzy_match_substring_empty_strings(self):
    self.assertTrue(fuzzy_match_lib.fuzzy_match_substring('', ''))
    self.assertFalse(fuzzy_match_lib.fuzzy_match_substring('', 'x'))
    self.assertFalse(fuzzy_match_lib.fuzzy_match_substring('x', ''))


if __name__ == '__main__':
  absltest.main()
