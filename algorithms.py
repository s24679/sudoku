import copy
from math import floor
from random import shuffle


number_list = [1,2,3,4,5,6,7,8,9]

class VBoard():
    def __init__(self, board=None):
        self.board = board or [[None for _ in range(9)] for _ in range(9)]
    
    def check_row(self, row, value):
        return value in self.board[row]
    
    def check_col(self, col, value):
        return value in [r[col] for r in self.board]

    def check_block(self, i, j, value):
        start_row = i*3
        start_col = j*3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if self.board[i][j] == value:
                    return True
        return False

class SudokuGenerator:
    def __init__(self, difficulty='medium'):
        self.difficulty_levels = {
            'debug': 79,
            'easy': 36,
            'medium': 32,
            'hard': 28,
            'expert': 24,
        }
        self.clues = self.difficulty_levels.get(difficulty, 32)

    def generate(self):
        vb = VBoard()
        self._backtracking_solver(vb)

        full_solution = copy.deepcopy(vb.board)

        puzzle = copy.deepcopy(full_solution)
        self._remove_numbers(puzzle)

        return puzzle, full_solution

    def _backtracking_solver(self, vb: VBoard):
        for i in range(9):
            for j in range(9):
                if vb.board[i][j] is None:
                    nums = number_list[:]
                    shuffle(nums)
                    for value in nums:
                        if (not(vb.check_row(i, value) or
                            vb.check_col(j, value) or
                            vb.check_block(floor(i / 3), floor(j / 3), value))):
                            vb.board[i][j] = value
                            if self._backtracking_solver(vb):
                                return True
                            vb.board[i][j] = None
                    return False
        return True

    def _count_solutions(self, vb: VBoard, limit=2, count=0):
        for i in range(9):
            for j in range(9):
                if vb.board[i][j] is None:
                    for value in range(1, 10):
                        if (not(vb.check_row(i, value) or
                            vb.check_col(j, value) or
                            vb.check_block(floor(i / 3), floor(j / 3), value))):
                            vb.board[i][j] = value
                            count = self._count_solutions(vb, limit, count)
                            vb.board[i][j] = None
                            if count >= limit:
                                return count
                    return count
        return count + 1

    def _remove_numbers(self, board):
        positions = [(i, j) for i in range(9) for j in range(9)]
        shuffle(positions)
        removed = 0
        total_to_remove = 81 - self.clues

        for i, j in positions:
            if removed >= total_to_remove:
                break
            backup = board[i][j]
            board[i][j] = None

            vb_copy = VBoard(copy.deepcopy(board))
            if self._count_solutions(vb_copy) != 1:
                board[i][j] = backup
            else:
                removed += 1

def create_board():
    board = VBoard()
    backtracking_solver(board)
    return board.board


def backtracking_solver(vb: VBoard):
    for i in range(0,9):
        for j in range(0,9):
            if(vb.board[i][j]== None):
                nums = number_list[:]
                shuffle(nums)
                for value in nums:
                    if(not vb.check_row(i, value)):
                        if(not vb.check_col(j, value)):
                            if(not vb.check_block(floor(i/3),floor(j/3),value)):
                                vb.board[i][j] = value
                                if (backtracking_solver(vb)):
                                    return True
                                vb.board[i][j] = None
                return False
    return True

def count_solutions(vb: VBoard, limit=2, count=0):
    for i in range(9):
        for j in range(9):
            if vb.board[i][j] is None:
                for value in range(1, 10):
                    if (vb.check_row(i, value) and
                        vb.check_col(j, value) and
                        vb.check_block(floor(i/3), floor(j/3), value)):
                        vb.board[i][j] = value
                        count = count_solutions(vb, limit, count)
                        vb.board[i][j] = None
                        if count >= limit:
                            return count
                return count
    return count + 1