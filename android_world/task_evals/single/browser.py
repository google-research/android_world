# Copyright 2025 The android_world Authors.
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

"""Tasks that require interacting with a browser."""

import random
import time
from typing import Any
from android_world.env import adb_utils
from android_world.env import device_constants
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.utils import user_data_generation
from android_world.utils import datetime_utils
from android_world.utils import file_utils


class BrowserTask(task_eval.TaskEval):
  """Base class for browser tasks."""

  app_names = ['chrome']
  complexity = 2
  schema = {
      'type': 'object',
      'properties': {
          'browser_task_seed': {'type': 'number'},
      },
      'required': ['browser_task_seed'],
  }
  template = ''
  HTML = ''  # Implementation overrides.

  preamble = (
      'Open the file task.html in Downloads in the file manager; when prompted'
      ' open it with Chrome.'
  )

  def initialize_device_time(self, env: interface.AsyncEnv) -> None:
    """Initializes the device time."""
    datetime_utils.toggle_auto_settings(
        env.controller, datetime_utils.Toggle.ON
    )
    time.sleep(1.0)

  def initialize_task(self, env: interface.AsyncEnv):
    super().initialize_task(env)
    user_data_generation.clear_device_storage(env)
    chrome_activity = adb_utils.extract_package_name(
        adb_utils.get_adb_activity('chrome')
    )

    adb_utils.clear_app_data(
        chrome_activity,
        env.controller,
    )
    adb_utils.grant_permissions(
        chrome_activity,
        'android.permission.POST_NOTIFICATIONS',
        env.controller,
    )

    html = self.HTML.replace('%%SEED%%', str(self.params['browser_task_seed']))
    task_html_path = file_utils.convert_to_posix_path(
        file_utils.get_local_tmp_directory(), 'task.html'
    )
    with open(task_html_path, 'w') as f:
      f.write(html)
    file_utils.copy_data_to_device(
        task_html_path,
        file_utils.convert_to_posix_path(
            device_constants.DOWNLOAD_DATA, 'task.html'
        ),
        env.controller,
    )

  def tear_down(self, env: interface.AsyncEnv):
    super().tear_down(env)
    user_data_generation.clear_device_storage(env)
    adb_utils.clear_app_data(
        adb_utils.extract_package_name(adb_utils.get_adb_activity('chrome')),
        env.controller,
    )
    datetime_utils.toggle_auto_settings(
        env.controller, datetime_utils.Toggle.OFF
    )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    package_name = adb_utils.extract_package_name(
        adb_utils.get_current_activity(env.controller)[0]
    )
    if package_name != 'com.android.chrome':
      return 0.0

    for element in state.ui_elements:
      if element.text == 'Success!':
        return 1.0
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'browser_task_seed': random.randint(0, 2**32 - 1)}


class BrowserMaze(BrowserTask):
  """Task to create a maze game."""

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then navigate the X to the bottom-right cell, by using the'
        ' direction buttons.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Maze Puzzle</title>
  <style>
    .row {
      display: flex;
    }

    .cell {
      width: 110px;
      height: 110px;
      border: 1px solid black;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 56px;
    }

    .wall {
      background-color: black;
    }

    .character {
      color: black;
    }

    .goal {
      background-color: green;
    }

    .controls {
      margin-top: 10px;
    }

    .controls button {
      margin-right: 5px;
      padding: 15px 28px;
      font-size: 30px;
    }
  </style>
</head>
<body>

  <div id="maze"></div>

  <div class="controls">
    <button onclick="moveCharacter('up')">Up</button>
    <button onclick="moveCharacter('down')">Down</button>
    <button onclick="moveCharacter('left')">Left</button>
    <button onclick="moveCharacter('right')">Right</button>
  </div>

  <script>
    const mazeSize = 4;
    let mazeLayout = [];
    let characterPosition = { row: 0, col: 0 };

    class SeededRNG {
    constructor(seed) {
        this.seed = seed;
    }

    random() {
        const a = 1664525;
        const c = 1013904223;
        const m = 2 ** 32;

        this.seed = (a * this.seed + c) % m;
        return this.seed / m;
    }
    }

    rng = new SeededRNG(%%SEED%%)
    function generateMaze() {
      mazeLayout = [];
      for (let row = 0; row < mazeSize; row++) {
        const currentRow = [];
        for (let col = 0; col < mazeSize; col++) {
          currentRow.push('#');
        }
        mazeLayout.push(currentRow);
      }

      // Create a path from start to goal
      const stack = [{ row: 0, col: 0 }];
      const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];

      while (stack.length > 0) {
        const { row, col } = stack.pop();
        mazeLayout[row][col] = ' ';

        if (row === mazeSize - 1 && col === mazeSize - 1) {
          break;
        }

        // Shuffle the order of directions
        for (let i = directions.length - 1; i > 0; i--) {
          const j = Math.floor(rng.random() * (i + 1));
          [directions[i], directions[j]] = [directions[j], directions[i]];
        }

        for (const [dx, dy] of directions) {
          const newRow = row + dx;
          const newCol = col + dy;
          if (
            newRow >= 0 &&
            newRow < mazeSize &&
            newCol >= 0 &&
            newCol < mazeSize &&
            mazeLayout[newRow][newCol] === '#'
          ) {
            stack.push({ row: newRow, col: newCol });
          }
        }
      }

      mazeLayout[0][0] = ' ';
      mazeLayout[mazeSize - 1][mazeSize - 1] = '$';
      characterPosition = { row: 0, col: 0 };
    }

    function renderMaze() {
      const mazeElement = document.getElementById('maze');
      mazeElement.innerHTML = '';

      for (let row = 0; row < mazeLayout.length; row++) {
        const rowElement = document.createElement('div');
        rowElement.className = 'row';

        for (let col = 0; col < mazeLayout[row].length; col++) {
          const cellElement = document.createElement('div');
          cellElement.className = 'cell';

          if (mazeLayout[row][col] === '#') {
            cellElement.classList.add('wall');
          } else if (row === characterPosition.row && col === characterPosition.col) {
            cellElement.classList.add('character');
            cellElement.innerHTML = 'X';
          } else if (mazeLayout[row][col] === '$') {
            cellElement.classList.add('goal');
          }

          rowElement.appendChild(cellElement);
        }

        mazeElement.appendChild(rowElement);
      }
    }

    function moveCharacter(direction) {
      const newPosition = { ...characterPosition };

      switch (direction) {
        case 'up':
          newPosition.row--;
          break;
        case 'down':
          newPosition.row++;
          break;
        case 'left':
          newPosition.col--;
          break;
        case 'right':
          newPosition.col++;
          break;
      }

      if (isValidMove(newPosition)) {
        characterPosition = newPosition;
        renderMaze();
        checkGoalReached();
      }
    }

    function isValidMove(position) {
      const { row, col } = position;
      if (
        row < 0 ||
        row >= mazeLayout.length ||
        col < 0 ||
        col >= mazeLayout[row].length ||
        mazeLayout[row][col] === '#'
      ) {
        return false;
      }
      return true;
    }

    function checkGoalReached() {
      const { row, col } = characterPosition;
      if (mazeLayout[row][col] === '$') {
        document.body.innerHTML = '<h1>Success!</h1>';
      }
    }

    generateMaze();
    renderMaze();
  </script>
</body>
</html>"""


class BrowserMultiply(BrowserTask):
  """Task for multiplying multiple numbers together."""

  complexity = 2.2

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then click the button 5 times, remember the numbers displayed, and'
        ' enter their product in the form.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Memory Task</title>
  <style>
    .container {
      text-align: center;
      margin-top: 50px;
    }

    .number {
      font-size: 48px;
      margin-bottom: 20px;
    }

    .button {
      padding: 10px 20px;
      font-size: 24px;
      margin-bottom: 20px;
    }

    .form {
      margin-top: 20px;
    }

    .form input {
      padding: 5px;
      font-size: 18px;
    }

    .form button {
      padding: 5px 10px;
      font-size: 18px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="number" id="number"></div>
    <button class="button" id="button" onclick="handleButtonClick()">Click Me</button>
    <div class="form" id="form" style="display: none;">
      <input type="number" id="answer" placeholder="Enter the product">
      <button onclick="checkAnswer()">Submit</button>
    </div>
    <div id="result"></div>
  </div>

  <script>
    class SeededRNG {
      constructor(seed) {
        this.seed = seed;
      }

      random() {
        const a = 1664525;
        const c = 1013904223;
        const m = 2 ** 32;
        this.seed = (a * this.seed + c) % m;
        return this.seed / m;
      }
    }

    const rng = new SeededRNG(%%SEED%%);
    const numbers = [];
    let clickCount = 0;

    function generateNumber() {
      const number = Math.floor(rng.random() * 10) + 1;
      numbers.push(number);
      document.getElementById('number').textContent = number;
    }

    function handleButtonClick() {
      clickCount++;
      if (clickCount < 5) {
        generateNumber();
      } else {
        document.getElementById('button').style.display = 'none';
        document.getElementById('number').style.display = 'none';
        document.getElementById('form').style.display = 'block';
      }
    }

    function checkAnswer() {
      const answer = parseInt(document.getElementById('answer').value);
      const product = numbers.reduce((acc, num) => acc * num, 1);
      const result = document.getElementById('result');
      if (answer === product) {
        result.innerHTML = '<h2>Success!</h2>';
      } else {
        result.innerHTML = '<h2></h2>';
      }
    }

    generateNumber();
  </script>
</body>
</html>"""


class BrowserSudoku(BrowserTask):
  """Task for solving a 4x4 Sudoku puzzle."""

  complexity = 2.5

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then solve the 4x4 Sudoku puzzle by filling in the empty cells.'
        ' Each row, column, and 2x2 box must contain the numbers 1-4.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>4x4 Sudoku</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 20px;
    }

    h1 {
      font-size: 32px;
      margin-bottom: 10px;
    }

    .instructions {
      font-size: 18px;
      margin-bottom: 20px;
      color: #555;
    }

    #sudoku-grid {
      display: inline-block;
      border: 3px solid #000;
      margin: 20px auto;
    }

    .sudoku-row {
      display: flex;
    }

    .sudoku-cell {
      width: 80px;
      height: 80px;
      border: 1px solid #999;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 36px;
      font-weight: bold;
    }

    .sudoku-cell.prefilled {
      background-color: #e8e8e8;
      color: #000;
    }

    .sudoku-cell.empty {
      background-color: #fff;
      cursor: pointer;
    }

    .sudoku-cell.empty:hover {
      background-color: #f0f0f0;
    }

    .sudoku-cell.selected {
      background-color: #cce5ff;
    }

    /* Thicker borders for 2x2 boxes */
    .sudoku-cell:nth-child(2) {
      border-right: 2px solid #000;
    }

    .sudoku-row:nth-child(2) .sudoku-cell {
      border-bottom: 2px solid #000;
    }

    .number-buttons {
      margin: 20px;
    }

    .number-buttons button {
      width: 60px;
      height: 60px;
      margin: 5px;
      font-size: 28px;
      font-weight: bold;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }

    .number-buttons button:hover {
      background-color: #45a049;
    }

    .number-buttons button.clear {
      background-color: #f44336;
    }

    .number-buttons button.clear:hover {
      background-color: #da190b;
    }

    .control-buttons {
      margin: 20px;
    }

    .control-buttons button {
      padding: 15px 30px;
      margin: 5px;
      font-size: 20px;
      font-weight: bold;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }

    .submit-button {
      background-color: #2196F3;
      color: white;
    }

    .submit-button:hover {
      background-color: #0b7dda;
    }

    #message {
      font-size: 24px;
      margin-top: 20px;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <h1>4×4 Sudoku</h1>
  <div class="instructions">
    Fill each row, column, and 2×2 box with numbers 1-4
  </div>

  <div id="sudoku-grid"></div>

  <div class="number-buttons">
    <button onclick="placeNumber(1)">1</button>
    <button onclick="placeNumber(2)">2</button>
    <button onclick="placeNumber(3)">3</button>
    <button onclick="placeNumber(4)">4</button>
    <button class="clear" onclick="placeNumber(0)">Clear</button>
  </div>

  <div class="control-buttons">
    <button class="submit-button" onclick="checkSolution()">Submit</button>
  </div>

  <div id="message"></div>

  <script>
    class SeededRNG {
      constructor(seed) {
        this.seed = seed;
      }

      random() {
        const a = 1664525;
        const c = 1013904223;
        const m = 2 ** 32;
        this.seed = (a * this.seed + c) % m;
        return this.seed / m;
      }
    }

    const rng = new SeededRNG(%%SEED%%);
    let grid = [];
    let solution = [];
    let selectedCell = null;

    // Generate a valid 4x4 Sudoku solution
    function generateSolution() {
      solution = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
      ];

      // Generate a valid solution
      solveSudoku(solution);
      return solution;
    }

    function isValid(board, row, col, num) {
      // Check row
      for (let i = 0; i < 4; i++) {
        if (board[row][i] === num) return false;
      }

      // Check column
      for (let i = 0; i < 4; i++) {
        if (board[i][col] === num) return false;
      }

      // Check 2x2 box
      const boxRow = Math.floor(row / 2) * 2;
      const boxCol = Math.floor(col / 2) * 2;
      for (let i = boxRow; i < boxRow + 2; i++) {
        for (let j = boxCol; j < boxCol + 2; j++) {
          if (board[i][j] === num) return false;
        }
      }

      return true;
    }

    function solveSudoku(board) {
      for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
          if (board[row][col] === 0) {
            const nums = [1, 2, 3, 4];
            // Shuffle numbers for randomness
            for (let i = nums.length - 1; i > 0; i--) {
              const j = Math.floor(rng.random() * (i + 1));
              [nums[i], nums[j]] = [nums[j], nums[i]];
            }

            for (const num of nums) {
              if (isValid(board, row, col, num)) {
                board[row][col] = num;
                if (solveSudoku(board)) {
                  return true;
                }
                board[row][col] = 0;
              }
            }
            return false;
          }
        }
      }
      return true;
    }

    // Generate puzzle by removing numbers from solution
    function generatePuzzle() {
      generateSolution();
      
      // Copy solution to grid
      grid = solution.map(row => [...row]);

      // Remove numbers to create puzzle (keep 6-8 numbers)
      const cellsToRemove = 8 + Math.floor(rng.random() * 3);
      let removed = 0;
      
      while (removed < cellsToRemove) {
        const row = Math.floor(rng.random() * 4);
        const col = Math.floor(rng.random() * 4);
        
        if (grid[row][col] !== 0) {
          grid[row][col] = 0;
          removed++;
        }
      }
    }

    function renderGrid() {
      const gridElement = document.getElementById('sudoku-grid');
      gridElement.innerHTML = '';

      for (let row = 0; row < 4; row++) {
        const rowElement = document.createElement('div');
        rowElement.className = 'sudoku-row';

        for (let col = 0; col < 4; col++) {
          const cellElement = document.createElement('div');
          cellElement.className = 'sudoku-cell';
          cellElement.dataset.row = row;
          cellElement.dataset.col = col;

          if (solution[row][col] !== 0 && grid[row][col] === solution[row][col] && grid[row][col] !== 0) {
            // Prefilled cell
            cellElement.classList.add('prefilled');
            cellElement.textContent = grid[row][col];
          } else {
            // Empty or user-filled cell
            cellElement.classList.add('empty');
            if (grid[row][col] !== 0) {
              cellElement.textContent = grid[row][col];
            }
            cellElement.addEventListener('click', () => selectCell(row, col));
          }

          rowElement.appendChild(cellElement);
        }

        gridElement.appendChild(rowElement);
      }
    }

    function selectCell(row, col) {
      // Remove previous selection
      document.querySelectorAll('.sudoku-cell').forEach(cell => {
        cell.classList.remove('selected');
      });

      // Select new cell
      selectedCell = { row, col };
      const cellElement = document.querySelector(
        `.sudoku-cell[data-row="${row}"][data-col="${col}"]`
      );
      cellElement.classList.add('selected');
    }

    function placeNumber(num) {
      if (!selectedCell) {
        document.getElementById('message').textContent = 'Please select a cell first';
        setTimeout(() => {
          document.getElementById('message').textContent = '';
        }, 2000);
        return;
      }

      const { row, col } = selectedCell;
      grid[row][col] = num;
      renderGrid();

      // Re-select the same cell
      if (num !== 0) {
        selectCell(row, col);
      }
    }

    function checkSolution() {
      // Check if grid matches solution
      for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
          if (grid[row][col] !== solution[row][col]) {
            document.getElementById('message').textContent = '';
            return;
          }
        }
      }

      document.body.innerHTML = '<h1>Success!</h1>';
    }

    // Initialize the game
    generatePuzzle();
    renderGrid();
  </script>
</body>
</html>"""


class BrowserSlider(BrowserTask):
  """Task for positioning a slider to a target value."""

  complexity = 2.0

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then drag the slider to match the target number shown at the top.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Slider Challenge</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 50px;
      background-color: #f5f5f5;
    }

    h1 {
      font-size: 36px;
      margin-bottom: 10px;
      color: #333;
    }

    .instructions {
      font-size: 20px;
      margin-bottom: 30px;
      color: #666;
    }

    .target-display {
      font-size: 48px;
      font-weight: bold;
      margin: 30px 0;
      padding: 20px;
      background-color: #4CAF50;
      color: white;
      border-radius: 10px;
      display: inline-block;
      min-width: 200px;
    }

    .slider-container {
      margin: 50px auto;
      max-width: 600px;
      padding: 30px;
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .slider-wrapper {
      position: relative;
      margin: 30px 0;
    }

    .slider {
      width: 100%;
      height: 20px;
      -webkit-appearance: none;
      appearance: none;
      background: linear-gradient(to right, #2196F3, #4CAF50, #FFC107, #FF5722);
      outline: none;
      border-radius: 10px;
      cursor: pointer;
    }

    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 40px;
      height: 40px;
      background: #333;
      cursor: pointer;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }

    .slider::-moz-range-thumb {
      width: 40px;
      height: 40px;
      background: #333;
      cursor: pointer;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }

    .value-display {
      font-size: 42px;
      font-weight: bold;
      margin: 20px 0;
      color: #333;
      padding: 15px;
      background-color: #f0f0f0;
      border-radius: 8px;
    }

    .scale {
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
      font-size: 16px;
      color: #666;
    }

    .submit-button {
      margin-top: 30px;
      padding: 15px 40px;
      font-size: 22px;
      font-weight: bold;
      background-color: #2196F3;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    .submit-button:hover {
      background-color: #0b7dda;
    }

    .tolerance-hint {
      font-size: 14px;
      color: #999;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h1>Slider Challenge</h1>
  <div class="instructions">Drag the slider to match the target number</div>

  <div class="target-display">
    Target: <span id="target">50</span>
  </div>

  <div class="slider-container">
    <div class="slider-wrapper">
      <input type="range" min="0" max="100" value="50" class="slider" id="slider">
      <div class="scale">
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </div>

    <div class="value-display">
      Current: <span id="current-value">50</span>
    </div>

    <button class="submit-button" onclick="checkValue()">Submit</button>
    <div class="tolerance-hint">Tolerance: ±2</div>
  </div>

  <script>
    class SeededRNG {
      constructor(seed) {
        this.seed = seed;
      }

      random() {
        const a = 1664525;
        const c = 1013904223;
        const m = 2 ** 32;
        this.seed = (a * this.seed + c) % m;
        return this.seed / m;
      }
    }

    const rng = new SeededRNG(%%SEED%%);
    
    // Generate target value between 10 and 90 (avoiding edges)
    const targetValue = Math.floor(rng.random() * 81) + 10;
    document.getElementById('target').textContent = targetValue;

    const slider = document.getElementById('slider');
    const currentValueDisplay = document.getElementById('current-value');

    // Set initial slider position to a random value away from target
    let initialValue;
    do {
      initialValue = Math.floor(rng.random() * 101);
    } while (Math.abs(initialValue - targetValue) < 15);
    
    slider.value = initialValue;
    currentValueDisplay.textContent = initialValue;

    // Update display when slider moves
    slider.addEventListener('input', function() {
      currentValueDisplay.textContent = this.value;
    });

    function checkValue() {
      const currentValue = parseInt(slider.value);
      const tolerance = 2; // Allow ±2 tolerance

      if (Math.abs(currentValue - targetValue) <= tolerance) {
        document.body.innerHTML = '<h1>Success!</h1>';
      } else {
        // Show a hint
        const difference = currentValue - targetValue;
        let hint = '';
        if (difference > 0) {
          hint = 'Too high! Try moving left.';
        } else {
          hint = 'Too low! Try moving right.';
        }
        
        // Flash hint briefly
        const hintDiv = document.createElement('div');
        hintDiv.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.8); color: white; padding: 20px 40px; border-radius: 10px; font-size: 24px; z-index: 1000;';
        hintDiv.textContent = hint;
        document.body.appendChild(hintDiv);
        
        setTimeout(() => {
          hintDiv.remove();
        }, 1500);
      }
    }
  </script>
</body>
</html>"""


class BrowserDraw(BrowserTask):
  """Task for drawing on a canvas."""

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then create a drawing using the three colors shown at the top'
        ' and hit submit.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Color Challenge</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      text-align: center;
      font-size: 14px;
    }
    canvas {
      border: 1px solid black;
      touch-action: none;
    }
    .color-button {
      width: 30px;
      height: 30px;
      margin: 3px;
      border: none;
      cursor: pointer;
    }
    #colorPalette {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      max-width: 300px;
      margin: 0 auto;
    }
    #canvasContainer {
      display: flex;
      justify-content: center;
    }
    #taskColors div {
      width: 30px;
      height: 30px;
      margin: 3px;
      display: inline-block;
    }
    button {
      margin: 5px;
      padding: 5px 10px;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div id="taskColors"></div>
  <div id="canvasContainer">
    <canvas id="canvas" width="300" height="300"></canvas>
  </div>
  <br>
  <p>Available Colors:</p>
  <div id="colorPalette"></div>
  <br>
  <button id="clearButton">Clear</button>
  <button id="submitButton">Submit</button>
  <p id="result"></p>
  <script>
    class SeededRNG {
      constructor(seed) {
        this.seed = seed;
      }

      random() {
        const a = 1664525;
        const c = 1013904223;
        const m = 2 ** 32;
        this.seed = (a * this.seed + c) % m;
        return this.seed / m;
      }
    }

    const rng = new SeededRNG(%%SEED%%);

    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const taskColorsElement = document.getElementById('taskColors');
    const colorPalette = document.getElementById('colorPalette');
    const clearButton = document.getElementById('clearButton');
    const submitButton = document.getElementById('submitButton');
    const resultElement = document.getElementById('result');

    let taskColors = [];

    const availableColors = [
      '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff',
      '#800000', '#008000', '#000080', '#808000', '#800080', '#008080',
      '#ffa500', '#ff1493', '#9932cc', '#20b2aa', '#4b0082', '#00ff7f',
      '#ff6347', '#00ced1', '#9400d3', '#f0e68c', '#ff8c00', '#228b22',
    ];

    function clearCanvas() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    function generateRandomColors(count) {
      const colors = [];
      const remainingColors = [...availableColors];

      for (let i = 0; i < count; i++) {
        if (remainingColors.length === 0) {
          break;
        }

        const randomIndex = Math.floor(rng.random() * remainingColors.length);
        const selectedColor = remainingColors[randomIndex];
        colors.push(selectedColor);
        remainingColors.splice(randomIndex, 1);
      }

      return colors;
    }

    function displayTaskColors() {
      taskColorsElement.innerHTML = '';
      taskColors.forEach(color => {
        const div = document.createElement('div');
        div.style.backgroundColor = color;
        div.style.width = '50px';
        div.style.height = '50px';
        div.style.display = 'inline-block';
        div.style.margin = '5px';
        taskColorsElement.appendChild(div);
      });
    }

    function createColorPalette() {
      colorPalette.innerHTML = '';
      availableColors.forEach(color => {
        const button = document.createElement('button');
        button.style.backgroundColor = color;
        button.classList.add('color-button');
        button.addEventListener('click', () => {
          ctx.strokeStyle = color;
        });
        colorPalette.appendChild(button);
      });
    }

    function submitTask() {
      submitButton.disabled = true;
      evaluateTask();
      submitButton.disabled = false;
    }

    function evaluateTask() {
      const pixelData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      const usedColors = new Set();
      for (let i = 0; i < pixelData.length; i += 4) {
        const r = pixelData[i];
        const g = pixelData[i + 1];
        const b = pixelData[i + 2];
        const color = rgbToHex(r, g, b);
        usedColors.add(color);
      }
      const success = taskColors.every(color => usedColors.has(color));
      showResult(success);
    }

    function rgbToHex(r, g, b) {
      const componentToHex = (c) => {
        const hex = c.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      };
      return '#' + componentToHex(r) + componentToHex(g) + componentToHex(b);
    }

    function showResult(success) {
      if (success) {
        resultElement.textContent = 'Success!';
      } else {
        resultElement.textContent = '';
      }
    }

    function init() {
      taskColors = generateRandomColors(3);
      displayTaskColors();
      createColorPalette();
    }

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);

    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);

    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;

    function startDrawing(e) {
      isDrawing = true;
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = (e.clientX || e.touches[0].clientX) - rect.left;
      const y = (e.clientY || e.touches[0].clientY) - rect.top;
      lastX = x * scaleX;
      lastY = y * scaleY;
    }

    function draw(e) {
      if (!isDrawing) return;
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = (e.clientX || e.touches[0].clientX) - rect.left;
      const y = (e.clientY || e.touches[0].clientY) - rect.top;
      const currentX = x * scaleX;
      const currentY = y * scaleY;
      ctx.beginPath();
      ctx.moveTo(lastX, lastY);
      ctx.lineTo(currentX, currentY);
      ctx.stroke();
      [lastX, lastY] = [currentX, currentY];
    }
    function stopDrawing() {
      isDrawing = false;
    }

    init();
    clearButton.addEventListener('click', clearCanvas);
    submitButton.addEventListener('click', submitTask);
  </script>
</body>
</html>
"""
