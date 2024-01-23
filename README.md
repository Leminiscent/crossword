# Crossword Puzzle Generator

This Python project provides a tool to generate crossword puzzles using constraint satisfaction programming. It includes two main components: a script to generate the crossword (`generate.py`) and a module defining the necessary classes and structures (`crossword.py`).

## Features

- **Constraint Satisfaction Approach:** Utilizes the principles of Constraint Satisfaction Problems (CSP) to efficiently fill crossword grids.
- **Customizable Crossword Structures:** Ability to define custom crossword structures through input files.
- **Word List Integration:** Supports custom word lists to populate the crossword.
- **Solution Output:** The generated crossword can be printed to the terminal and optionally saved as an image.

## Installation

No specific installation is required apart from having Python installed on your system. The script uses standard Python libraries and the PIL (Python Imaging Library) for image generation.

## Usage

### `generate.py`

This script reads the crossword structure and word list from files, creates a Crossword and CrosswordCreator object, and then attempts to solve the crossword.

#### Command Line Arguments

- `structure`: A file defining the structure of the crossword.
- `words`: A file containing a list of words to use in the crossword.
- `output` (optional): Specifies the name of the file to save the crossword image.

#### Usage Example

```bash
python generate.py structure.txt words.txt output.png
```

### `crossword.py`

This module contains the classes and structures for representing a crossword puzzle. It includes the Variable class for potential words in the crossword and the Crossword class for the structure of the crossword, managing variables and their overlaps.

#### Note:

This module is not intended to be run as a standalone script. It should be imported and used by generate.py.

## Components

### `CrosswordCreator Class`

Handles the creation of the crossword puzzle using CSP. Methods include initializing the puzzle, printing the solution, saving the solution as an image, and the solving process itself.

### `Crossword Class`

Represents the structure of a crossword puzzle, including the grid, set of words, and variables (potential words).

### `Variable Class`

Represents a variable (a potential word) in the crossword puzzle, defined by its position, direction, and length.

## Requirements

- Python 3.x
- PIL (Python Imaging Library) for saving crosswords as images