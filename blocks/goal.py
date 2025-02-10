"""Objective/goal"""

from __future__ import annotations
import random
from blocks.block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> list[Goal]:
    """Return a randomly generated list of goals with length <num_goals>.

    Each goal must be randomly selected from the two types of Goals provided
    and must have a different randomly generated colour from COLOUR_LIST.
    No two goals can have the same colour.

    Preconditions:
    - num_goals <= len(COLOUR_LIST)
    """
    colours = COLOUR_LIST.copy()
    final = []
    for _ in range(0, num_goals):
        colour = random.choice(colours)
        colours.remove(colour)
        # 1 = BlobGoal
        # 2 = PerimeterGoal
        goal_type = random.randint(1, 2)
        if goal_type == 1:
            final.append(BlobGoal(colour))
        else:
            final.append(PerimeterGoal(colour))
    return final


def flatten(block: Block) -> list[list[tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j].

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    final = []
    size = 2 ** (block.max_depth - block.level)
    unit_size = block.size // size
    for _ in range(size):
        final.append([None] * size)

    if block.colour is not None:
        for i in range(size):
            for j in range(size):
                final[j][i] = block.colour
        return final

    for child in block.children:
        temp = flatten(child)
        for i in range(len(temp)):
            for j in range(len(temp)):
                x = (child.position[0] - block.position[0]) // unit_size + j
                y = (child.position[1] - block.position[1]) // unit_size + i
                final[x][y] = temp[j][i]
    return final


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    Instance Attributes:
    - colour: The target colour for this goal, that is the colour to which
              this goal applies.
    """
    colour: tuple[int, int, int]

    def __init__(self, target_colour: tuple[int, int, int]) -> None:
        """Initialize this goal to have the given <target_colour>.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given <board>.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal to maximize the presence of this goal's target colour
    on the board's perimeter.
    """

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.

        The score for a PerimeterGoal is defined to be the number of unit cells
        on the perimeter whose colour is this goal's target colour. Corner cells
        count twice toward the score.
        """
        grid = flatten(board)
        count = 0
        for i in range(len(grid)):
            if grid[0][i] == self.colour:
                count += 1
            if grid[i][0] == self.colour:
                count += 1
            if grid[i][len(grid) - 1] == self.colour:
                count += 1
            if grid[len(grid) - 1][i] == self.colour:
                count += 1

        return count

    def description(self) -> str:
        """Return a description of this goal.
        """

        return ('Maximize the presence of ' + colour_name(
            self.colour) + " on the board's perimeter")


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.

        The score for a BlobGoal is defined to be the total number of
        unit cells in the largest connected blob within this Block.
        """
        grid = flatten(board)
        final = []
        visited = []
        for _ in range(len(grid)):
            visited.append([-1] * len(grid))

        for i in range(len(grid)):
            for j in range(len(grid)):
                final.append(
                    self._undiscovered_blob_size((i, j), grid, visited))

        return max(final)

    def _undiscovered_blob_size(self, pos: tuple[int, int],
                                board: list[list[tuple[int, int, int]]],
                                visited: list[list[int]]) -> int:
        """Return the size of the largest connected blob in <board> that (a) is
        of this Goal's target <colour>, (b) includes the cell at <pos>, and (c)
        involves only cells that are not in <visited>.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure (to <board>) that, in each cell,
        contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.

        If <pos> is out of bounds for <board>, return 0.
        """
        if \
                pos[0] < 0 or pos[0] >= len(board) or pos[1] < 0 or pos[
                    1] >= len(board):
            return 0

        colour = board[pos[0]][pos[1]]
        count = 0
        if visited[pos[0]][pos[1]] != -1:
            return 0
        if colour != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0
        else:
            visited[pos[0]][pos[1]] = 1
            count += self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                  board, visited)
            count += self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                  board, visited)
            count += self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                  board, visited)
            count += self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                  board, visited)
        return count + 1

    def description(self) -> str:
        """Return a description of this goal.
        """

        return ('Create the largest connected blob of ' + colour_name(
            self.colour) + " anywhere within the Block")


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
