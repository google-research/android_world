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
    <div class="tolerance-hint">Must match exactly!</div>
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

      if (currentValue === targetValue) {
        document.body.innerHTML = '<h1>Success!</h1>';
      } else {
        // Show a hint
        const difference = currentValue - targetValue;
        let hint = '';
        if (difference > 0) {
          hint = `Too high! (${currentValue} > ${targetValue})`;
        } else {
          hint = `Too low! (${currentValue} < ${targetValue})`;
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


class BrowserProgressBar(BrowserTask):
  """Task for waiting for a progress bar to complete before proceeding."""

  complexity = 2.3

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then wait for the progress bar to reach 100% and click the'
        ' Continue button that appears.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Loading Progress</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 50px;
      background-color: #f5f5f5;
    }

    h1 {
      font-size: 36px;
      margin-bottom: 20px;
      color: #333;
    }

    .loading-container {
      max-width: 600px;
      margin: 50px auto;
      padding: 40px;
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .status-text {
      font-size: 24px;
      margin-bottom: 30px;
      color: #666;
    }

    .progress-container {
      width: 100%;
      height: 40px;
      background-color: #e0e0e0;
      border-radius: 20px;
      overflow: hidden;
      margin: 30px 0;
      position: relative;
    }

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #4CAF50, #8BC34A);
      border-radius: 20px;
      transition: width 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .progress-text {
      position: absolute;
      width: 100%;
      text-align: center;
      line-height: 40px;
      font-size: 20px;
      font-weight: bold;
      color: #333;
      z-index: 1;
    }

    .continue-button {
      padding: 15px 40px;
      font-size: 22px;
      font-weight: bold;
      background-color: #2196F3;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      margin-top: 30px;
      display: none;
    }

    .continue-button:hover {
      background-color: #0b7dda;
    }

    .spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #4CAF50;
      border-radius: 50%;
      width: 50px;
      height: 50px;
      animation: spin 1s linear infinite;
      margin: 20px auto;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <h1>Loading Content</h1>
  
  <div class="loading-container">
    <div class="status-text" id="status">Please wait while content loads...</div>
    <div class="spinner"></div>
    
    <div class="progress-container">
      <div class="progress-text" id="progress-text">0%</div>
      <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
    </div>

    <button class="continue-button" id="continue-btn" onclick="handleContinue()">
      Continue
    </button>
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
    
    let progress = 0;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const continueBtn = document.getElementById('continue-btn');
    const statusText = document.getElementById('status');

    // Random duration between 3-6 seconds
    const totalDuration = 3000 + Math.floor(rng.random() * 3000);
    const updateInterval = 100; // Update every 100ms
    const totalSteps = totalDuration / updateInterval;
    const progressPerStep = 100 / totalSteps;

    // Add some randomness to progress speed
    let currentProgress = 0;

    function updateProgress() {
      if (currentProgress < 100) {
        // Add slight randomness to progress increment
        const increment = progressPerStep * (0.8 + rng.random() * 0.4);
        currentProgress = Math.min(100, currentProgress + increment);
        
        const displayProgress = Math.floor(currentProgress);
        progressBar.style.width = displayProgress + '%';
        progressText.textContent = displayProgress + '%';

        setTimeout(updateProgress, updateInterval);
      } else {
        // Progress complete
        currentProgress = 100;
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        document.querySelector('.spinner').style.display = 'none';
        statusText.textContent = 'Loading complete!';
        statusText.style.color = '#4CAF50';
        
        // Show continue button after a short delay
        setTimeout(() => {
          continueBtn.style.display = 'inline-block';
        }, 500);
      }
    }

    function handleContinue() {
      document.body.innerHTML = '<h1>Success!</h1>';
    }

    // Start progress after a short delay
    setTimeout(updateProgress, 500);
  </script>
</body>
</html>"""


class BrowserPopupDismiss(BrowserTask):
  """Task for dismissing popup dialogs while completing a form."""

  complexity = 2.8

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then fill in the form with any values and submit. You may need to'
        ' close popup dialogs that appear.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Form with Popups</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 50px;
      background-color: #f5f5f5;
    }

    h1 {
      text-align: center;
      font-size: 36px;
      margin-bottom: 20px;
      color: #333;
    }

    .form-container {
      max-width: 500px;
      margin: 0 auto;
      padding: 30px;
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      margin-bottom: 5px;
      font-size: 18px;
      color: #333;
      font-weight: bold;
    }

    input[type="text"],
    input[type="email"],
    select {
      width: 100%;
      padding: 12px;
      font-size: 16px;
      border: 2px solid #ddd;
      border-radius: 5px;
      box-sizing: border-box;
    }

    input:focus, select:focus {
      border-color: #4CAF50;
      outline: none;
    }

    .submit-button {
      width: 100%;
      padding: 15px;
      font-size: 20px;
      font-weight: bold;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      margin-top: 10px;
    }

    .submit-button:hover {
      background-color: #45a049;
    }

    .popup-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.7);
      z-index: 1000;
      justify-content: center;
      align-items: center;
    }

    .popup {
      background-color: white;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      max-width: 400px;
      text-align: center;
      position: relative;
    }

    .popup h2 {
      font-size: 24px;
      margin-bottom: 15px;
      color: #333;
    }

    .popup p {
      font-size: 16px;
      margin-bottom: 20px;
      color: #666;
    }

    .popup-close {
      padding: 10px 30px;
      font-size: 18px;
      font-weight: bold;
      background-color: #2196F3;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }

    .popup-close:hover {
      background-color: #0b7dda;
    }

    .close-x {
      position: absolute;
      top: 10px;
      right: 15px;
      font-size: 28px;
      font-weight: bold;
      color: #999;
      cursor: pointer;
      line-height: 20px;
    }

    .close-x:hover {
      color: #333;
    }
  </style>
</head>
<body>
  <h1>Registration Form</h1>
  
  <div class="form-container">
    <form id="main-form">
      <div class="form-group">
        <label for="name">Full Name:</label>
        <input type="text" id="name" name="name" required>
      </div>

      <div class="form-group">
        <label for="email">Email Address:</label>
        <input type="email" id="email" name="email" required>
      </div>

      <div class="form-group">
        <label for="country">Country:</label>
        <select id="country" name="country" required>
          <option value="">Select a country</option>
          <option value="us">United States</option>
          <option value="uk">United Kingdom</option>
          <option value="ca">Canada</option>
          <option value="au">Australia</option>
          <option value="other">Other</option>
        </select>
      </div>

      <button type="submit" class="submit-button">Submit</button>
    </form>
  </div>

  <!-- Popup overlays -->
  <div class="popup-overlay" id="popup1">
    <div class="popup">
      <span class="close-x" onclick="closePopup('popup1')">&times;</span>
      <h2>Special Offer!</h2>
      <p>Subscribe to our newsletter for exclusive deals and updates.</p>
      <button class="popup-close" onclick="closePopup('popup1')">Close</button>
    </div>
  </div>

  <div class="popup-overlay" id="popup2">
    <div class="popup">
      <span class="close-x" onclick="closePopup('popup2')">&times;</span>
      <h2>Cookie Notice</h2>
      <p>This website uses cookies to improve your experience. By continuing, you accept our cookie policy.</p>
      <button class="popup-close" onclick="closePopup('popup2')">Accept</button>
    </div>
  </div>

  <div class="popup-overlay" id="popup3">
    <div class="popup">
      <span class="close-x" onclick="closePopup('popup3')">&times;</span>
      <h2>Limited Time Offer</h2>
      <p>Get 20% off your first purchase! Don't miss out on this amazing deal.</p>
      <button class="popup-close" onclick="closePopup('popup3')">No Thanks</button>
    </div>
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
    
    let popupsShown = 0;
    let popupsClosed = 0;
    const popupIds = ['popup1', 'popup2', 'popup3'];
    const totalPopups = 2; // Show 2 random popups

    // Shuffle popup order
    for (let i = popupIds.length - 1; i > 0; i--) {
      const j = Math.floor(rng.random() * (i + 1));
      [popupIds[i], popupIds[j]] = [popupIds[j], popupIds[i]];
    }

    function showPopup(popupId) {
      const popup = document.getElementById(popupId);
      popup.style.display = 'flex';
      popupsShown++;
    }

    function closePopup(popupId) {
      const popup = document.getElementById(popupId);
      popup.style.display = 'none';
      popupsClosed++;
    }

    // Show first popup after random delay (2-4 seconds)
    setTimeout(() => {
      showPopup(popupIds[0]);
    }, 2000 + Math.floor(rng.random() * 2000));

    // Show second popup after another delay (3-5 seconds after page load)
    setTimeout(() => {
      showPopup(popupIds[1]);
    }, 3000 + Math.floor(rng.random() * 2000));

    // Monitor form interactions to trigger additional popups
    let formInteracted = false;
    document.querySelectorAll('input, select').forEach(element => {
      element.addEventListener('focus', () => {
        if (!formInteracted) {
          formInteracted = true;
        }
      });
    });

    // Handle form submission
    document.getElementById('main-form').addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Check if form is complete
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const country = document.getElementById('country').value;
      
      if (name && email && country) {
        document.body.innerHTML = '<h1>Success!</h1>';
      }
    });

    // Make closePopup available globally
    window.closePopup = closePopup;
  </script>
</body>
</html>"""


class BrowserAdBlock(BrowserTask):
  """Task for closing ad overlays blocking content."""

  complexity = 2.5

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then close the advertisement overlay to reveal the content,'
        ' read the secret code, and enter it in the form.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Article Page</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f5f5f5;
    }

    .article-container {
      max-width: 700px;
      margin: 0 auto;
      padding: 30px;
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    h1 {
      font-size: 32px;
      margin-bottom: 20px;
      color: #333;
    }

    .article-content {
      font-size: 18px;
      line-height: 1.6;
      color: #555;
      margin-bottom: 30px;
    }

    .secret-code-box {
      padding: 20px;
      background-color: #fff3cd;
      border: 2px solid #ffc107;
      border-radius: 8px;
      text-align: center;
      margin: 30px 0;
    }

    .secret-code {
      font-size: 36px;
      font-weight: bold;
      color: #856404;
      letter-spacing: 3px;
      margin: 10px 0;
    }

    .form-group {
      margin: 20px 0;
    }

    label {
      display: block;
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 10px;
      color: #333;
    }

    input[type="text"] {
      width: 100%;
      padding: 12px;
      font-size: 18px;
      border: 2px solid #ddd;
      border-radius: 5px;
      box-sizing: border-box;
    }

    .submit-button {
      width: 100%;
      padding: 15px;
      font-size: 20px;
      font-weight: bold;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      margin-top: 15px;
    }

    .submit-button:hover {
      background-color: #45a049;
    }

    /* Ad overlay styles */
    .ad-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.85);
      z-index: 9999;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .ad-content {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 40px;
      border-radius: 15px;
      max-width: 500px;
      text-align: center;
      color: white;
      position: relative;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }

    .ad-close {
      position: absolute;
      top: 10px;
      right: 15px;
      font-size: 32px;
      font-weight: bold;
      color: white;
      cursor: pointer;
      line-height: 1;
      padding: 5px 10px;
      border-radius: 5px;
      background-color: rgba(255,255,255,0.2);
    }

    .ad-close:hover {
      background-color: rgba(255,255,255,0.3);
    }

    .ad-content h2 {
      font-size: 32px;
      margin-bottom: 15px;
    }

    .ad-content p {
      font-size: 18px;
      margin-bottom: 20px;
      line-height: 1.5;
    }

    .ad-button {
      padding: 15px 40px;
      font-size: 20px;
      font-weight: bold;
      background-color: white;
      color: #667eea;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      margin: 10px;
    }

    .ad-button:hover {
      background-color: #f0f0f0;
    }

    .small-text {
      font-size: 12px;
      margin-top: 20px;
      opacity: 0.8;
    }
  </style>
</head>
<body>
  <div class="article-container">
    <h1>Welcome to Our Article</h1>
    
    <div class="article-content">
      <p>Thank you for visiting our website. To access the exclusive content, 
      you need to enter the secret code displayed below.</p>
      
      <p>This code is required to verify that you can view the content properly.</p>
    </div>

    <div class="secret-code-box">
      <p style="margin: 0; font-size: 16px;">Your Secret Code:</p>
      <div class="secret-code" id="secret-code"></div>
    </div>

    <form id="code-form">
      <div class="form-group">
        <label for="code-input">Enter the Secret Code:</label>
        <input type="text" id="code-input" name="code" required 
               placeholder="Enter the code here">
      </div>
      <button type="submit" class="submit-button">Submit Code</button>
    </form>
  </div>

  <!-- Ad Overlay -->
  <div class="ad-overlay" id="ad-overlay">
    <div class="ad-content">
      <span class="ad-close" id="close-ad">&times;</span>
      <h2>🎁 Special Offer!</h2>
      <p>Get 50% OFF on our premium subscription!</p>
      <p>Limited time offer - Don't miss out!</p>
      <button class="ad-button" onclick="closeAd()">Learn More</button>
      <button class="ad-button" onclick="closeAd()">No Thanks</button>
      <p class="small-text">Click the × button or any option to close</p>
    </div>
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
    
    // Generate random secret code (4 characters: letters and numbers)
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let secretCode = '';
    for (let i = 0; i < 4; i++) {
      secretCode += chars.charAt(Math.floor(rng.random() * chars.length));
    }
    
    document.getElementById('secret-code').textContent = secretCode;

    function closeAd() {
      document.getElementById('ad-overlay').style.display = 'none';
    }

    // Close button functionality
    document.getElementById('close-ad').addEventListener('click', closeAd);

    // Handle form submission
    document.getElementById('code-form').addEventListener('submit', function(e) {
      e.preventDefault();
      
      const enteredCode = document.getElementById('code-input').value.toUpperCase();
      
      if (enteredCode === secretCode) {
        document.body.innerHTML = '<h1>Success!</h1>';
      } else {
        // Show error message
        alert('Incorrect code. Please try again.');
      }
    });
  </script>
</body>
</html>"""


class BrowserMultiStepForm(BrowserTask):
  """Task for completing a multi-step registration form."""

  complexity = 3.0

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then complete the 3-step registration form by filling in all'
        ' required fields and clicking Next/Submit on each step.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Multi-Step Registration</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
    }

    .form-container {
      max-width: 600px;
      margin: 30px auto;
      padding: 40px;
      background-color: white;
      border-radius: 15px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }

    h1 {
      text-align: center;
      font-size: 32px;
      margin-bottom: 10px;
      color: #333;
    }

    .progress-bar {
      display: flex;
      justify-content: space-between;
      margin: 30px 0;
      position: relative;
    }

    .progress-step {
      flex: 1;
      text-align: center;
      position: relative;
    }

    .progress-circle {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background-color: #ddd;
      color: #999;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 18px;
      margin-bottom: 5px;
      position: relative;
      z-index: 2;
    }

    .progress-circle.active {
      background-color: #4CAF50;
      color: white;
    }

    .progress-circle.completed {
      background-color: #2196F3;
      color: white;
    }

    .progress-label {
      font-size: 14px;
      color: #666;
    }

    .progress-line {
      position: absolute;
      top: 20px;
      left: 0;
      right: 0;
      height: 3px;
      background-color: #ddd;
      z-index: 1;
    }

    .progress-line-fill {
      height: 100%;
      background-color: #2196F3;
      transition: width 0.3s ease;
    }

    .form-step {
      display: none;
    }

    .form-step.active {
      display: block;
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      margin-bottom: 8px;
      font-size: 16px;
      font-weight: bold;
      color: #333;
    }

    input[type="text"],
    input[type="email"],
    input[type="tel"],
    select {
      width: 100%;
      padding: 12px;
      font-size: 16px;
      border: 2px solid #ddd;
      border-radius: 5px;
      box-sizing: border-box;
    }

    input:focus, select:focus {
      border-color: #667eea;
      outline: none;
    }

    .required {
      color: red;
    }

    .button-group {
      display: flex;
      justify-content: space-between;
      margin-top: 30px;
    }

    .btn {
      padding: 12px 30px;
      font-size: 18px;
      font-weight: bold;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    .btn-next, .btn-submit {
      background-color: #4CAF50;
      color: white;
    }

    .btn-next:hover, .btn-submit:hover {
      background-color: #45a049;
    }

    .btn-prev {
      background-color: #999;
      color: white;
    }

    .btn-prev:hover {
      background-color: #777;
    }

    .error-message {
      color: red;
      font-size: 14px;
      margin-top: 5px;
      display: none;
    }
  </style>
</head>
<body>
  <div class="form-container">
    <h1>Create Account</h1>
    
    <div class="progress-bar">
      <div class="progress-line">
        <div class="progress-line-fill" id="progress-fill"></div>
      </div>
      <div class="progress-step">
        <div class="progress-circle active" id="circle-1">1</div>
        <div class="progress-label">Personal Info</div>
      </div>
      <div class="progress-step">
        <div class="progress-circle" id="circle-2">2</div>
        <div class="progress-label">Contact</div>
      </div>
      <div class="progress-step">
        <div class="progress-circle" id="circle-3">3</div>
        <div class="progress-label">Preferences</div>
      </div>
    </div>

    <form id="registration-form">
      <!-- Step 1: Personal Information -->
      <div class="form-step active" id="step-1">
        <h2>Step 1: Personal Information</h2>
        <div class="form-group">
          <label>First Name <span class="required">*</span></label>
          <input type="text" id="first-name" required>
        </div>
        <div class="form-group">
          <label>Last Name <span class="required">*</span></label>
          <input type="text" id="last-name" required>
        </div>
        <div class="form-group">
          <label>Date of Birth <span class="required">*</span></label>
          <input type="text" id="dob" placeholder="MM/DD/YYYY" required>
        </div>
        <div class="button-group">
          <div></div>
          <button type="button" class="btn btn-next" onclick="nextStep(1)">Next</button>
        </div>
      </div>

      <!-- Step 2: Contact Information -->
      <div class="form-step" id="step-2">
        <h2>Step 2: Contact Information</h2>
        <div class="form-group">
          <label>Email Address <span class="required">*</span></label>
          <input type="email" id="email" required>
        </div>
        <div class="form-group">
          <label>Phone Number <span class="required">*</span></label>
          <input type="tel" id="phone" placeholder="(123) 456-7890" required>
        </div>
        <div class="form-group">
          <label>City <span class="required">*</span></label>
          <input type="text" id="city" required>
        </div>
        <div class="button-group">
          <button type="button" class="btn btn-prev" onclick="prevStep(2)">Previous</button>
          <button type="button" class="btn btn-next" onclick="nextStep(2)">Next</button>
        </div>
      </div>

      <!-- Step 3: Preferences -->
      <div class="form-step" id="step-3">
        <h2>Step 3: Preferences</h2>
        <div class="form-group">
          <label>Username <span class="required">*</span></label>
          <input type="text" id="username" required>
        </div>
        <div class="form-group">
          <label>Preferred Language <span class="required">*</span></label>
          <select id="language" required>
            <option value="">Select a language</option>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="zh">Chinese</option>
          </select>
        </div>
        <div class="form-group">
          <label>Newsletter Preference <span class="required">*</span></label>
          <select id="newsletter" required>
            <option value="">Select preference</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="never">Never</option>
          </select>
        </div>
        <div class="button-group">
          <button type="button" class="btn btn-prev" onclick="prevStep(3)">Previous</button>
          <button type="submit" class="btn btn-submit">Submit</button>
        </div>
      </div>
    </form>
  </div>

  <script>
    let currentStep = 1;

    function updateProgress() {
      // Update progress bar
      const progressFill = document.getElementById('progress-fill');
      progressFill.style.width = ((currentStep - 1) / 2) * 100 + '%';

      // Update circles
      for (let i = 1; i <= 3; i++) {
        const circle = document.getElementById(`circle-${i}`);
        circle.classList.remove('active', 'completed');
        if (i < currentStep) {
          circle.classList.add('completed');
        } else if (i === currentStep) {
          circle.classList.add('active');
        }
      }
    }

    function validateStep(step) {
      let isValid = true;
      const inputs = document.querySelectorAll(`#step-${step} input[required], #step-${step} select[required]`);
      
      inputs.forEach(input => {
        if (!input.value.trim()) {
          isValid = false;
          input.style.borderColor = 'red';
        } else {
          input.style.borderColor = '#ddd';
        }
      });

      return isValid;
    }

    function nextStep(step) {
      if (validateStep(step)) {
        document.getElementById(`step-${step}`).classList.remove('active');
        currentStep++;
        document.getElementById(`step-${currentStep}`).classList.add('active');
        updateProgress();
        window.scrollTo(0, 0);
      } else {
        alert('Please fill in all required fields.');
      }
    }

    function prevStep(step) {
      document.getElementById(`step-${step}`).classList.remove('active');
      currentStep--;
      document.getElementById(`step-${currentStep}`).classList.add('active');
      updateProgress();
      window.scrollTo(0, 0);
    }

    document.getElementById('registration-form').addEventListener('submit', function(e) {
      e.preventDefault();
      
      if (validateStep(3)) {
        document.body.innerHTML = '<h1>Success!</h1>';
      } else {
        alert('Please fill in all required fields.');
      }
    });

    // Make functions globally accessible
    window.nextStep = nextStep;
    window.prevStep = prevStep;
  </script>
</body>
</html>"""


class BrowserFileUpload(BrowserTask):
  """Task for simulating file selection and upload."""

  complexity = 2.6

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then select a file from the file list and click Upload to'
        ' complete the task.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>File Upload</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f5f5f5;
    }

    .upload-container {
      max-width: 700px;
      margin: 50px auto;
      padding: 40px;
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    h1 {
      text-align: center;
      font-size: 32px;
      margin-bottom: 10px;
      color: #333;
    }

    .instruction {
      text-align: center;
      font-size: 18px;
      color: #666;
      margin-bottom: 30px;
    }

    .required-file {
      text-align: center;
      padding: 15px;
      background-color: #e3f2fd;
      border: 2px solid #2196F3;
      border-radius: 8px;
      margin-bottom: 30px;
    }

    .required-file-label {
      font-size: 16px;
      color: #666;
      margin-bottom: 5px;
    }

    .required-file-name {
      font-size: 24px;
      font-weight: bold;
      color: #2196F3;
    }

    .file-list {
      border: 2px solid #ddd;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 30px;
      max-height: 400px;
      overflow-y: auto;
    }

    .file-list-title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 15px;
      color: #333;
    }

    .file-item {
      padding: 15px;
      margin: 10px 0;
      border: 2px solid #ddd;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      align-items: center;
    }

    .file-item:hover {
      border-color: #2196F3;
      background-color: #f0f8ff;
    }

    .file-item.selected {
      border-color: #4CAF50;
      background-color: #e8f5e9;
    }

    .file-icon {
      font-size: 30px;
      margin-right: 15px;
    }

    .file-info {
      flex-grow: 1;
    }

    .file-name {
      font-size: 18px;
      font-weight: bold;
      color: #333;
      margin-bottom: 3px;
    }

    .file-size {
      font-size: 14px;
      color: #999;
    }

    .selected-file-display {
      padding: 15px;
      background-color: #f9f9f9;
      border: 2px solid #ddd;
      border-radius: 5px;
      margin-bottom: 20px;
      min-height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .selected-file-display.has-file {
      background-color: #e8f5e9;
      border-color: #4CAF50;
    }

    .selected-text {
      font-size: 16px;
      color: #666;
    }

    .selected-text.has-file {
      color: #2e7d32;
      font-weight: bold;
    }

    .upload-button {
      width: 100%;
      padding: 15px;
      font-size: 20px;
      font-weight: bold;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    .upload-button:hover:not(:disabled) {
      background-color: #45a049;
    }

    .upload-button:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <div class="upload-container">
    <h1>📤 File Upload</h1>
    <p class="instruction">Please select and upload the required file</p>

    <div class="required-file">
      <div class="required-file-label">Required File:</div>
      <div class="required-file-name" id="required-file"></div>
    </div>

    <div class="file-list">
      <div class="file-list-title">📁 Available Files</div>
      <div id="files-container"></div>
    </div>

    <div class="selected-file-display" id="selected-display">
      <span class="selected-text" id="selected-text">No file selected</span>
    </div>

    <button class="upload-button" id="upload-btn" disabled onclick="uploadFile()">
      Upload File
    </button>
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

    // File names pool
    const fileNames = [
      'Project_Report.pdf',
      'Quarterly_Results.xlsx',
      'Meeting_Notes.docx',
      'Budget_2024.pdf',
      'Team_Photo.jpg',
      'Presentation.pptx',
      'Data_Analysis.csv',
      'Contract_Draft.pdf',
      'Invoice_12345.pdf',
      'Product_Specs.docx',
      'Marketing_Plan.pdf',
      'Sales_Report.xlsx',
      'Customer_List.csv',
      'Design_Mockup.png',
      'Training_Video.mp4'
    ];

    const fileIcons = {
      'pdf': '📄',
      'xlsx': '📊',
      'docx': '📝',
      'jpg': '🖼️',
      'png': '🖼️',
      'pptx': '📊',
      'csv': '📋',
      'mp4': '🎥'
    };

    const fileSizes = ['2.3 MB', '1.5 MB', '856 KB', '3.2 MB', '512 KB', '4.1 MB', '1.8 MB'];

    // Shuffle file names
    for (let i = fileNames.length - 1; i > 0; i--) {
      const j = Math.floor(rng.random() * (i + 1));
      [fileNames[i], fileNames[j]] = [fileNames[j], fileNames[i]];
    }

    // Select 8-10 random files to display
    const numFiles = 8 + Math.floor(rng.random() * 3);
    const availableFiles = fileNames.slice(0, numFiles);

    // Select required file (one of the available files)
    const requiredFileIndex = Math.floor(rng.random() * availableFiles.length);
    const requiredFile = availableFiles[requiredFileIndex];

    document.getElementById('required-file').textContent = requiredFile;

    let selectedFile = null;

    // Create file list
    const filesContainer = document.getElementById('files-container');
    availableFiles.forEach((fileName, index) => {
      const fileExt = fileName.split('.').pop();
      const fileIcon = fileIcons[fileExt] || '📄';
      const fileSize = fileSizes[Math.floor(rng.random() * fileSizes.length)];

      const fileItem = document.createElement('div');
      fileItem.className = 'file-item';
      fileItem.setAttribute('data-filename', fileName);
      fileItem.innerHTML = `
        <div class="file-icon">${fileIcon}</div>
        <div class="file-info">
          <div class="file-name">${fileName}</div>
          <div class="file-size">${fileSize}</div>
        </div>
      `;

      fileItem.addEventListener('click', function() {
        // Remove selection from all files
        document.querySelectorAll('.file-item').forEach(item => {
          item.classList.remove('selected');
        });

        // Select this file
        this.classList.add('selected');
        selectedFile = fileName;

        // Update selected display
        const selectedDisplay = document.getElementById('selected-display');
        const selectedText = document.getElementById('selected-text');
        selectedDisplay.classList.add('has-file');
        selectedText.classList.add('has-file');
        selectedText.textContent = `Selected: ${fileName}`;

        // Enable upload button
        document.getElementById('upload-btn').disabled = false;
      });

      filesContainer.appendChild(fileItem);
    });

    function uploadFile() {
      if (selectedFile === requiredFile) {
        document.body.innerHTML = '<h1>Success!</h1>';
      } else {
        alert(`Wrong file! Please select "${requiredFile}"`);
      }
    }

    // Make uploadFile globally accessible
    window.uploadFile = uploadFile;
  </script>
</body>
</html>"""


class BrowserRetry(BrowserTask):
  """Task for handling submission failure and retry logic."""

  complexity = 2.7

  @property
  def goal(self) -> str:
    return (
        self.preamble
        + ' Then fill in the survey form and submit. The first submission may'
        ' fail - if so, click Retry to resubmit.'
    )

  HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>Survey Form</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f5f5f5;
    }

    .survey-container {
      max-width: 600px;
      margin: 50px auto;
      padding: 40px;
      background-color: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    h1 {
      text-align: center;
      font-size: 32px;
      margin-bottom: 10px;
      color: #333;
    }

    .subtitle {
      text-align: center;
      font-size: 16px;
      color: #666;
      margin-bottom: 30px;
    }

    .form-group {
      margin-bottom: 25px;
    }

    label {
      display: block;
      margin-bottom: 8px;
      font-size: 16px;
      font-weight: bold;
      color: #333;
    }

    input[type="text"],
    input[type="email"],
    textarea,
    select {
      width: 100%;
      padding: 12px;
      font-size: 16px;
      border: 2px solid #ddd;
      border-radius: 5px;
      box-sizing: border-box;
      font-family: Arial, sans-serif;
    }

    textarea {
      resize: vertical;
      min-height: 100px;
    }

    input:focus, textarea:focus, select:focus {
      border-color: #2196F3;
      outline: none;
    }

    .required {
      color: red;
    }

    .rating-group {
      display: flex;
      gap: 10px;
      margin-top: 8px;
    }

    .rating-btn {
      flex: 1;
      padding: 10px;
      font-size: 16px;
      font-weight: bold;
      background-color: #f0f0f0;
      border: 2px solid #ddd;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.3s;
    }

    .rating-btn:hover {
      border-color: #2196F3;
      background-color: #e3f2fd;
    }

    .rating-btn.selected {
      background-color: #4CAF50;
      border-color: #4CAF50;
      color: white;
    }

    .submit-button {
      width: 100%;
      padding: 15px;
      font-size: 20px;
      font-weight: bold;
      background-color: #2196F3;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      margin-top: 20px;
      transition: background-color 0.3s;
    }

    .submit-button:hover:not(:disabled) {
      background-color: #0b7dda;
    }

    .submit-button:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }

    .error-message {
      background-color: #ffebee;
      border: 2px solid #f44336;
      border-radius: 8px;
      padding: 20px;
      margin: 20px 0;
      display: none;
    }

    .error-message.show {
      display: block;
    }

    .error-title {
      font-size: 20px;
      font-weight: bold;
      color: #c62828;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .error-text {
      font-size: 16px;
      color: #d32f2f;
      margin-bottom: 15px;
    }

    .retry-button {
      padding: 12px 30px;
      font-size: 18px;
      font-weight: bold;
      background-color: #ff9800;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    .retry-button:hover {
      background-color: #f57c00;
    }

    .loading {
      text-align: center;
      padding: 20px;
      font-size: 18px;
      color: #666;
    }

    .spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #2196F3;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 20px auto;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="survey-container">
    <h1>Customer Survey</h1>
    <p class="subtitle">Help us improve our service</p>

    <form id="survey-form">
      <div class="form-group">
        <label>Name <span class="required">*</span></label>
        <input type="text" id="name" required>
      </div>

      <div class="form-group">
        <label>Email <span class="required">*</span></label>
        <input type="email" id="email" required>
      </div>

      <div class="form-group">
        <label>How satisfied are you with our service? <span class="required">*</span></label>
        <div class="rating-group">
          <button type="button" class="rating-btn" data-rating="1" onclick="selectRating(1)">1</button>
          <button type="button" class="rating-btn" data-rating="2" onclick="selectRating(2)">2</button>
          <button type="button" class="rating-btn" data-rating="3" onclick="selectRating(3)">3</button>
          <button type="button" class="rating-btn" data-rating="4" onclick="selectRating(4)">4</button>
          <button type="button" class="rating-btn" data-rating="5" onclick="selectRating(5)">5</button>
        </div>
        <input type="hidden" id="rating" required>
      </div>

      <div class="form-group">
        <label>Additional Comments</label>
        <textarea id="comments" placeholder="Tell us more about your experience..."></textarea>
      </div>

      <button type="submit" class="submit-button" id="submit-btn">Submit Survey</button>
    </form>

    <div class="error-message" id="error-message">
      <div class="error-title">⚠️ Submission Failed</div>
      <div class="error-text">We encountered a temporary network error. Please try again.</div>
      <button class="retry-button" onclick="retrySubmission()">Retry Submission</button>
    </div>

    <div class="loading" id="loading" style="display: none;">
      <div class="spinner"></div>
      <div>Submitting your response...</div>
    </div>
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
    
    let selectedRating = null;
    let attemptCount = 0;
    let formData = null;

    function selectRating(rating) {
      // Remove selection from all buttons
      document.querySelectorAll('.rating-btn').forEach(btn => {
        btn.classList.remove('selected');
      });

      // Select clicked button
      document.querySelector(`[data-rating="${rating}"]`).classList.add('selected');
      selectedRating = rating;
      document.getElementById('rating').value = rating;
    }

    function validateForm() {
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const rating = document.getElementById('rating').value;

      if (!name || !email || !rating) {
        alert('Please fill in all required fields');
        return false;
      }

      return true;
    }

    function simulateSubmission() {
      attemptCount++;

      // Show loading
      document.getElementById('loading').style.display = 'block';
      document.getElementById('survey-form').style.display = 'none';
      document.getElementById('error-message').classList.remove('show');

      setTimeout(() => {
        document.getElementById('loading').style.display = 'none';

        // First attempt always fails, subsequent attempts succeed
        if (attemptCount === 1) {
          // Show error message
          document.getElementById('error-message').classList.add('show');
        } else {
          // Success
          document.body.innerHTML = '<h1>Success!</h1>';
        }
      }, 1500 + Math.floor(rng.random() * 1000));
    }

    document.getElementById('survey-form').addEventListener('submit', function(e) {
      e.preventDefault();

      if (validateForm()) {
        // Store form data
        formData = {
          name: document.getElementById('name').value,
          email: document.getElementById('email').value,
          rating: document.getElementById('rating').value,
          comments: document.getElementById('comments').value
        };

        simulateSubmission();
      }
    });

    function retrySubmission() {
      simulateSubmission();
    }

    // Make functions globally accessible
    window.selectRating = selectRating;
    window.retrySubmission = retrySubmission;
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
