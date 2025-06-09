import ast
import re
import json
from typing import Any, Optional

def extract_json(s: str) -> dict[str, Any] | None:
  """Extracts JSON from string.

  Tries conversion with ast and json modules. If special_fill_form is True,
  will attempt to parse fill_form actions with nested lists more robustly.

  Args:
    s: A string with a JSON in it.
    special_fill_form: If True, use a more robust parser for fill_form actions.

  Returns:
    JSON object.
  """
  if '"action_type": "fill_form"' in s:
    # Try to extract the JSON object using a greedy match for the outermost braces
    first = s.find('{')
    last = s.rfind('}')
    if first != -1 and last != -1:
      json_str = s[first:last+1]
      try:
        return json.loads(json_str)
      except Exception as error:
        print(f'Cannot extract fill_form JSON, error: {error}')
        return None
  # Default behavior
  pattern = r'\{.*?\}'
  match = re.search(pattern, s)
  if match:
    try:
      return ast.literal_eval(match.group())
    except (SyntaxError, ValueError) as error:
      try:
        return json.loads(match.group())
      except (SyntaxError, ValueError) as error2:
        print(
            'Cannot extract JSON, skipping due to errors %s and %s',
            error,
            error2,
        )
        return None
  else:
    return None

s = '{"action_type": "fill_form", "form": [{"text": "Grace", "index": 7}, {"text": "Taylor", "index": 8}, {"text": "799-802-1530", "index": 10}, {"text": "Work", "index": 11}]}'
new_string = extract_json(s, special_fill_form=True)
print(new_string.get('action_type', []))
