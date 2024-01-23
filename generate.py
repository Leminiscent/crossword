"""
This script generates a crossword puzzle using constraint satisfaction programming. It includes a 
main function that reads the crossword structure and word list from files, creates a Crossword 
and CrosswordCreator object, and then attempts to solve the crossword. If a solution is found, 
it is printed to the terminal and optionally saved as an image file.

Usage:
    python generate.py structure words [output]

Where:
    'structure' is a file defining the structure of the crossword,
    'words' is a file containing a list of words to use in the crossword,
    'output' is an optional argument specifying the name of the file to save the crossword image.
"""
import sys

from crossword import *


class CrosswordCreator:
    """
    This class represents a crossword creator for generating crossword puzzles.
    It uses the constraint satisfaction problem (CSP) approach to fill in a crossword grid.
    """

    def __init__(self, crossword):
        """
        Initializes a new CSP crossword generator.

        Args:
        crossword (Crossword): An instance of the Crossword class containing the structure of the crossword.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Converts the crossword assignment into a 2D array of characters.

        Args:
        assignment (dict): A dictionary representing the current assignment of words to variables.

        Returns:
        list of list of str: A 2D array representing the crossword grid filled with assigned words.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Prints the crossword assignment to the terminal in a human-readable format.

        Args:
        assignment (dict): A dictionary representing the current assignment of words to variables.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Saves the crossword assignment as an image file.

        Args:
        assignment (dict): A dictionary representing the current assignment of words to variables.
        filename (str): The path of the file where the crossword image will be saved.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Solves the crossword puzzle using constraint satisfaction methods.

        Returns:
        dict or None: The assignment dictionary if a solution is found; otherwise, None.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Enforces node consistency by eliminating words that do not match the length of the variables.
        """
        for variable in self.domains:
            for word in set(self.domains[variable]):
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Revises the domain of variable x by considering the constraints imposed by variable y.

        Args:
        x (Variable): A variable in the crossword.
        y (Variable): Another variable that imposes constraints on x.

        Returns:
        bool: True if the domain of x is revised, False otherwise.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return revised

        x_index, y_index = overlap
        for x_word in set(self.domains[x]):
            if not any(
                x_word[x_index] == y_word[y_index] for y_word in self.domains[y]
            ):
                self.domains[x].remove(x_word)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Enforces arc consistency on the puzzle's variables.

        Args:
        arcs (list of tuple): A list of arcs (pairs of variables) to be considered for consistency. If None, all arcs are considered.

        Returns:
        bool: True if arc consistency is achieved, False if an inconsistency is found.
        """
        if arcs is None:
            arcs = [(x, y) for x in self.domains for y in self.crossword.neighbors(x)]

        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for neighbor in self.crossword.neighbors(x) - {y}:
                    arcs.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Checks if the crossword assignment is complete.

        Args:
        assignment (dict): The current assignment.

        Returns:
        bool: True if the assignment is complete, False otherwise.
        """
        return all(variable in assignment for variable in self.crossword.variables)

    def consistent(self, assignment):
        """
        Checks if the given assignment is consistent with the crossword constraints.

        Args:
        assignment (dict): The current assignment.

        Returns:
        bool: True if the assignment is consistent, False otherwise.
        """
        if len(set(assignment.values())) < len(assignment):
            return False

        for variable, value in assignment.items():
            if variable.length != len(value):
                return False

            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[variable, neighbor]
                    if value[overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Orders the domain values of a variable based on the number of conflicts they cause with unassigned variables.

        Args:
        var (Variable): The variable whose domain values need to be ordered.
        assignment (dict): The current assignment.

        Returns:
        list: An ordered list of domain values for the variable.
        """

        def count_conflicts(value):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    count += sum(
                        1
                        for word in self.domains[neighbor]
                        if word[overlap[1]] != value[overlap[0]]
                    )
            return count

        return sorted(self.domains[var], key=count_conflicts)

    def select_unassigned_variable(self, assignment):
        """
        Selects the next variable to assign, using the Minimum Remaining Values (MRV) heuristic.

        Args:
        assignment (dict): The current assignment.

        Returns:
        Variable: The selected unassigned variable.
        """

        def mrv(variable):
            return len(self.domains[variable]), -len(self.crossword.neighbors(variable))

        unassigned = [v for v in self.crossword.variables if v not in assignment]
        return min(unassigned, key=mrv)

    def backtrack(self, assignment):
        """
        Backtrack search for solving the crossword puzzle.

        Args:
        assignment (dict): The current assignment.

        Returns:
        dict or None: The complete assignment if a solution is found, or None if there is no solution.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
