"""
This module defines the classes and structures necessary for representing a crossword puzzle. 
It includes the 'Variable' class representing a potential word in the crossword and the 'Crossword' class 
which represents the structure of the crossword and manages the variables and their possible overlaps.

Usage:
    This module is not intended to be run as a standalone script. It should be imported and used by 'generate.py'.
"""


class Variable:
    """
    Represents a variable (a potential word) in the crossword puzzle, defined by its position, direction, and length.
    """

    # Constants for word direction
    ACROSS = "across"
    DOWN = "down"

    def __init__(self, i, j, direction, length):
        """
        Creates a new variable with starting point, direction, and length.

        Args:
        i (int): The row index where the word starts.
        j (int): The column index where the word starts.
        direction (str): The direction of the word ('across' or 'down').
        length (int): The length of the word.
        """
        self.i = i
        self.j = j
        self.direction = direction
        self.length = length
        self.cells = []
        for k in range(self.length):
            self.cells.append(
                (
                    self.i + (k if self.direction == Variable.DOWN else 0),
                    self.j + (k if self.direction == Variable.ACROSS else 0),
                )
            )

    def __hash__(self):
        """
        Generates a hash value for a Variable instance. This is useful for using Variable instances as keys in dictionaries.

        Returns:
        int: The hash value of the variable.
        """
        return hash((self.i, self.j, self.direction, self.length))

    def __eq__(self, other):
        """
        Checks if two Variable instances are equal. Two instances are considered equal if they have the same starting point, direction, and length.

        Args:
        other (Variable): Another Variable instance to compare against.

        Returns:
        bool: True if the variables are equal, False otherwise.
        """
        return (
            (self.i == other.i)
            and (self.j == other.j)
            and (self.direction == other.direction)
            and (self.length == other.length)
        )

    def __str__(self):
        """
        Returns a human-readable string representation of the Variable instance.

        Returns:
        str: A string representing the variable's starting point, direction, and length.
        """
        return f"({self.i}, {self.j}) {self.direction} : {self.length}"

    def __repr__(self):
        """
        Returns a string that would recreate the Variable object if passed to eval().

        Returns:
        str: A string that represents a valid constructor call for recreating the variable.
        """
        direction = repr(self.direction)
        return f"Variable({self.i}, {self.j}, {direction}, {self.length})"


class Crossword:
    """
    Represents the structure of a crossword puzzle, including the grid structure, the set of all words to use, and the variables (potential words).
    """

    def __init__(self, structure_file, words_file):
        """
        Initializes a crossword grid structure and sets up variables based on the structure and word list files.

        Args:
        structure_file (str): File path to the crossword structure file.
        words_file (str): File path to the file containing the list of words.
        """
        # Determine structure of crossword
        with open(structure_file) as f:
            contents = f.read().splitlines()
            self.height = len(contents)
            self.width = max(len(line) for line in contents)

            self.structure = []
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    if j >= len(contents[i]):
                        row.append(False)
                    elif contents[i][j] == "_":
                        row.append(True)
                    else:
                        row.append(False)
                self.structure.append(row)

        # Save vocabulary list
        with open(words_file) as f:
            self.words = set(f.read().upper().splitlines())

        # Determine variable set
        self.variables = set()
        for i in range(self.height):
            for j in range(self.width):
                # Vertical words
                starts_word = self.structure[i][j] and (
                    i == 0 or not self.structure[i - 1][j]
                )
                if starts_word:
                    length = 1
                    for k in range(i + 1, self.height):
                        if self.structure[k][j]:
                            length += 1
                        else:
                            break
                    if length > 1:
                        self.variables.add(
                            Variable(i=i, j=j, direction=Variable.DOWN, length=length)
                        )

                # Horizontal words
                starts_word = self.structure[i][j] and (
                    j == 0 or not self.structure[i][j - 1]
                )
                if starts_word:
                    length = 1
                    for k in range(j + 1, self.width):
                        if self.structure[i][k]:
                            length += 1
                        else:
                            break
                    if length > 1:
                        self.variables.add(
                            Variable(i=i, j=j, direction=Variable.ACROSS, length=length)
                        )

        # Compute overlaps for each word
        # For any pair of variables v1, v2, their overlap is either:
        #    None, if the two variables do not overlap; or
        #    (i, j), where v1's ith character overlaps v2's jth character
        self.overlaps = dict()
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 == v2:
                    continue
                cells1 = v1.cells
                cells2 = v2.cells
                intersection = set(cells1).intersection(cells2)
                if not intersection:
                    self.overlaps[v1, v2] = None
                else:
                    intersection = intersection.pop()
                    self.overlaps[v1, v2] = (
                        cells1.index(intersection),
                        cells2.index(intersection),
                    )

    def neighbors(self, var):
        """
        Returns the set of variables that overlap with the given variable.

        Args:
        var (Variable): A variable in the crossword puzzle.

        Returns:
        set of Variable: A set of variables that overlap with 'var'.
        """
        return set(v for v in self.variables if v != var and self.overlaps[v, var])
