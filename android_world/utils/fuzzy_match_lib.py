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

"""Utility functions for fuzzy matching."""

from thefuzz import fuzz


# Threshold for determining if two strings are equal.
_MIN_DIFF_SIMILARITY = 0.9


def fuzzy_match(text1: str, text2: str, ignore_case: bool = True) -> bool:
  """Compares two strings.

  Args:
    text1: The first text.
    text2: The second text.
    ignore_case: Whether to ignore case during comparison.

  Returns:
    Whether the two strings are approximately equal.
  """
  if text1 is None or text2 is None:
    return False
  text1 = str(text1)
  text2 = str(text2)

  if ignore_case:
    text1 = text1.lower()
    text2 = text2.lower()

  if not text1 or not text2:
    return False

  # Take the best of full-string and substring similarity. `ratio()` alone is
  # sensitive to length differences, so a value carrying a short suffix/prefix
  # (e.g. "Urgent" vs "Urgent. Reimbursable.") falls below the threshold even
  # though the core text is a clean substring; `partial_ratio()` returns 100 for
  # that pair. `partial_ratio()` alone, conversely, undershoots a mid-string
  # insertion ("Elm St" vs "Elm Street"). The max is substring-friendly without
  # regressing existing matches.
  return max(
      fuzz.ratio(text1, text2), fuzz.partial_ratio(text1, text2)
  ) >= _MIN_DIFF_SIMILARITY * 100
