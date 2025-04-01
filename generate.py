import sys

from PIL.Image import NONE

from crossword import *

# REFERENCE: (just for my learning and future reference):
# Differnce between two sets:
# https://www.w3schools.com/python/ref_set_difference.asp
# any iterable:
# https://stackoverflow.com/questions/19211828/using-any-and-all-to-check-if-a-list-contains-one-set-of-values-or-another/19211875
# https://www.w3schools.com/python/ref_func_any.asp


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
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
        Print crossword assignment to the terminal.
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
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            # Every word in domain
            remove_word = self.domains[var].copy()
            for word in remove_word:
                # If the word is not the right length then remove it
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Revision is false unless x domain was changed
        revision = False

        # Find overlap between two nodes
        overlap = self.crossword.overlaps[x, y]

        # If variables don't overlap then its consistent
        if overlap is None:
            return False

        word_copy = self.domains[x].copy()
        for word in word_copy:
            # Consistency for this word in y domain
            valid_word = False
            for y_word in self.domains[y]:
                if word[overlap[0]] == y_word[overlap[1]]:
                    valid_word = True
                    break
            if not valid_word:
                self.domains[x].remove(word)
                revision = True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initial queue of all arcs
        if arcs is None:
            arcs = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
                if x != y and self.crossword.overlaps[x, y]
            ]

        while len(arcs) > 0:
            x, y = arcs.pop(0)
            # Check for revision
            if self.revise(x, y):
                # If x domain is empty
                if not self.domains[x]:
                    return False

                # Else add neighbors and check for arc consis. from y
                for neighbor in self.crossword.neighbors(x) - {y}:
                    arcs.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # If assignment is not right length
        var = self.crossword.variables
        if len(assignment) != len(var):
            return False

        # If atleast one var is not in the assignment
        for v in var:
            if not assignment[v]:
                return False

        # Else ture
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Duplicates
        if len(list(assignment.values())) != len(set(assignment.values())):
            return False

        # Length
        # for x, word in assign.items, if len(x) != len(word)
        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False

        # Neighbours conflicts
        for var in assignment:
            for neighbour in self.crossword.neighbors(var):
                if neighbour in assignment:
                    x, y = self.crossword.overlaps[var, neighbour]
                    if assignment[var][x] != assignment[neighbour][y]:
                        return False

        # No duplicates, correct length and no conflicts
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # neighbours of given variable
        neighbours = self.crossword.neighbors(var)

        # count of ruled out domain options from neighbour variables
        count = {word: 0 for word in self.domains[var]}

        for val in self.domains[var]:
            for neighbour in neighbours:
                # Ignore assigned variables
                if neighbour not in assignment.keys():
                    overlap = self.crossword.overlaps[var, neighbour]
                    # if two words don't match increase counter
                    for n_val in self.domains[neighbour]:
                        # Ignore assigned values
                        if (
                            n_val not in assignment.values() and
                            val[overlap[0]] == n_val[overlap[1]]
                        ):
                            count[val] += 1

        # sort
        return sorted(self.domains[var], key=lambda value: count[value])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Initialize list of remaining unsassinged variables
        unassigned = list(self.crossword.variables - assignment.keys())

        # Sort the variables
        sort_unassigned = [(len(self.domains[var]), var) for var in unassigned]

        # Remove variable with highest number of neighbours
        min_unassigned = min(sort_unassigned, key=lambda var: var[0])[0]
        for n, var in sort_unassigned:
            if n != min_unassigned:
                unassigned.remove(var)

        # Sort the remaining unassinged by the number of neighbours (degree)
        order_unassigned = [
            (len(self.crossword.neighbors(var)), var) for var in unassigned
        ]
        return max(order_unassigned, key=lambda var: var[0])[1]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Unassigned vairable to choose its word
        var = self.select_unassigned_variable(assignment)

        # Words in the unassignment variable
        for word in self.order_domain_values(var, assignment):
            assignment_copy = assignment.copy()
            assignment_copy[var] = word

            # If the assignment is consistent
            # If consistent then change the assgiment and
            # recursive call backtrack
            if self.consistent(assignment_copy):
                assignment[var] = word
                result = self.backtrack(assignment)

                # Return asssignment that is not none
                if result:
                    return result

        # No assignment, return none
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
