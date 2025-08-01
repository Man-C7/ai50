import sys

from crossword import *


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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for v in self.domains:
            to_remove = set()
            for word in self.domains[v]:
                if len(word) != v.length:
                    to_remove.add(word)
            self.domains[v] -= to_remove

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        if  self.crossword.overlaps[x, y] is not None:
            i, j = self.crossword.overlaps[x, y]
            y_overlapping = set()
            to_remove = set()
            for  word in self.domains[y]:
                y_overlapping.add(word[j])
            for word in self.domains[x]:
                if word[i] not in y_overlapping:
                    to_remove.add(word)
            if to_remove:
                self.domains[x] -= to_remove
                revised = True
            
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = [
                (x,y)
                for x in self.crossword.variables
                for y in self.crossword.variables
                if x != y and self.crossword.overlaps[x,y] is not None
            ]
        else:
            arcs = arcs
        
        while arcs:
            i, j = arcs.pop(0)
            if self.revise(i, j):
                if not self.domains[i]:
                    return False
                else:
                     for k in self.crossword.neighbors(i):
                         if k !=j:
                             arcs.append((k,i))
        return True
        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return set(assignment.keys()) == set(self.crossword.variables) and all(value is not None for value in assignment.values())


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for (x, y) in self.crossword.overlaps:
            overlap = self.crossword.overlaps[x, y]
            if overlap is None:
                continue
            i, j = overlap
            if x in assignment and y in assignment:
                if assignment[x][i] != assignment[y][j]:
                    return False

        for variable, word in assignment.items():
            if len(word) != variable.length:
                return False
            
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ordered = []
        domain = self.domains.get(var)
        if var in assignment:
            domain.discard(assignment[var])

        domain_value_dict = {
            x : 0
            for x in domain
        }

        for x in domain:
            for p in self.crossword.neighbors(var):
                if p in assignment:
                    continue
                i, j = self.crossword.overlaps[var, p]
                for y in self.domains[p]: 
                    if x[i] != y[j]:
                        domain_value_dict[x] += 1

        ordered_domain_value_dict = dict(sorted(domain_value_dict.items(), key=lambda item: item[1]))
        for x in ordered_domain_value_dict.keys():
            ordered.append(x)

        return ordered


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        values_left = {
            x: len(self.domains[x]) for x in self.domains if x not in assignment}
        
        min_values_left = min(values_left.values())

        min_value_vars = [var for var in values_left if values_left[var] == min_values_left]
        
        if len(min_value_vars) == 1:
            return min_value_vars[0]
        
        min_value_degrees = {
            var:len(self.crossword.neighbors(var))
            for var in min_value_vars
        }

        min_value_degrees = sorted(min_value_degrees.items(), key=lambda item: item[1], reverse=True)

        return min_value_degrees[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
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
