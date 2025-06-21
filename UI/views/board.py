from customtkinter import CTkFrame
from UI.modules.block import Block
from math import floor
from random import shuffle

from typing import TYPE_CHECKING

from algorithms import SudokuGenerator, create_board
if TYPE_CHECKING:
    from UI.modules.numberEntry import NumberEntry

class Board(CTkFrame):
    blocks: list[list[Block]]
    board: list[list['NumberEntry']]
    def __init__(self, master, on_solved, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_solved = on_solved
        for i in range(0,3):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

        self.blocks = []
        for i in range(0,3):
            row = []
            for j in range(0,3):
                block = Block(self)
                block.grid(row=i, column=j, sticky="nsew", padx=3, pady=3)
                row.append(block)
            self.blocks.append(row)
        
        self.board = self.get_board()
        #generator = SudokuGenerator('debug')
        #board, _ = generator.generate()
        #self.set_board(board)

    def get_row(self, row) -> list['NumberEntry']:
        res = []
        for i in range(0,3):
            res.extend(self.blocks[floor(row/3)][i].get_row(row%3))
        return res
            
    def get_col(self, col) -> list['NumberEntry']:
        res = []
        for i in range(0,3):
            res.extend(self.blocks[i][floor(col/3)].get_col(col%3))
        return res
    
    def get_board(self) -> list[list['NumberEntry']]:
        res = []
        for i in range(0,9):
            row = self.get_row(i)
            res.append(row)
        return res

    def set_board(self, board):
        for i in range(9):
            for j in range(9):
                self.board[i][j].set_value(board[i][j])
                self.board[i][j].configure(state="disabled" if board[i][j] != None else "normal")
                self.board[i][j].configure(text_color=("#0f0f0f","#c7c7c7") if board[i][j] != None else ("#000000","#fcfcfc"))
    
    def check_row(self, row, value) -> bool:
        return value in [c.get_value() for c in self.get_row(row)]
    
    def check_col(self, col, value) -> bool:
        return value in [c.get_value() for c in self.get_col(col)]
                
    def is_full(self):
        for i in self.blocks:
            for j in i:
                if(j.check_block(None)):
                    return False
        print("Board full")
        return True

    def is_sudoku_solved(self, var, index,mode):
        board = []
        for i in range(0,9):
            board.append([r.get() for r in self.get_row(i)])

        def is_valid_group(group):
            return sorted(group) == [str(e) for e in list(range(1, 10))]

        for row in board:
            if not is_valid_group(row):
                #print(f"Row check failed r:{row}")
                return False

        for col in range(9):
            column = []
            for row in range(9):
                column.append(board[row][col])
            if not is_valid_group(column):
                #print(f"Column check failed c:{col}")
                return False

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = []
                for r in range(3):
                    for c in range(3):
                        box.append(board[box_row + r][box_col + c])
                if not is_valid_group(box):
                    #print(f"Box check failed r:{box_row} c:{box_col}")
                    return False

        print("SOLVED")
        self.on_solved()
        return True
