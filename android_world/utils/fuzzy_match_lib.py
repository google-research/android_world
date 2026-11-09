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


def _preprocess(
    text1: str, text2: str, ignore_case: bool
) -> tuple[str, str] | None:
  """Stringifies and (optionally) lowercases the inputs.

  Args:
    text1: The first text.
    text2: The second text.
    ignore_case: Whether to ignore case during comparison.

  Returns:
    A tuple of the normalized strings, or None if either input is None.
  """
  if text1 is None or text2 is None:
    return None
  text1 = str(text1)
  text2 = str(text2)
  if ignore_case:
    text1 = text1.lower()
    text2 = text2.lower()
  return text1, text2


def _empty_string_result(text1: str, text2: str) -> bool | None:
  """Resolves the empty-string cases, or returns None for non-empty inputs.

  Empty == empty is an exact match: this restores the original difflib
  behavior, where `SequenceMatcher(None, '', '').ratio() == 1.0`. Some
  free-form fields (e.g. recipe `source`, calendar `location`) are empty in
  the reference and correctly left empty by the agent. Empty vs non-empty is a
  mismatch, so a field the agent wrongly leaves blank (or wrongly fills) is
  still rejected.
  """
  if not text1 and not text2:
    return True
  if not text1 or not text2:
    return False
  return None


def fuzzy_match(text1: str, text2: str, ignore_case: bool = True) -> bool:
  """Compares two strings.

  Args:
    text1: The first text.
    text2: The second text.
    ignore_case: Whether to ignore case during comparison.

  Returns:
    Whether the two strings are approximately equal.
  """
  processed = _preprocess(text1, text2, ignore_case)
  if processed is None:
    return False
  text1, text2 = processed
  empty_result = _empty_string_result(text1, text2)
  if empty_result is not None:
    return empty_result
  return fuzz.ratio(text1, text2) >= _MIN_DIFF_SIMILARITY * 100


def fuzzy_match_substring(
    text1: str, text2: str, ignore_case: bool = True
) -> bool:
  """Like `fuzzy_match`, but also accepts a clean substring match.

  `fuzz.partial_ratio` returns 100 whenever one string is a substring of the
  other, which is a false positive for shared fields such as contact names or
  SMS bodies (e.g. "Joanne" vs "Ann"). It is therefore only appropriate where
  the candidate legitimately extends the reference with a short prefix/suffix.
  The motivating use case is ExpenseAddMultipleFromMarkor's note, where the
  reference note is "Urgent" and the agent records "Urgent. Reimbursable.".
  Do not use this for general-purpose matching.

  Args:
    text1: The first text.
    text2: The second text.
    ignore_case: Whether to ignore case during comparison.

  Returns:
    Whether the two strings are approximately equal, allowing a substring
    relationship to count as a match.
  """
  processed = _preprocess(text1, text2, ignore_case)
  if processed is None:
    return False
  text1, text2 = processed
  empty_result = _empty_string_result(text1, text2)
  if empty_result is not None:
    return empty_result
  return max(
      fuzz.ratio(text1, text2), fuzz.partial_ratio(text1, text2)
  ) >= _MIN_DIFF_SIMILARITY * 100
