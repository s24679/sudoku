from customtkinter import CTkFrame, CTkEntry, CENTER
from UI.modules.numberEntry import NumberEntry

class Block(CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        for i in range(0,3):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

        self.cells = []
        for i in range(0,3):
            row = []
            for j in range(0,3):
                cell = NumberEntry(self, justify=CENTER, min_value=1, max_value=9, corner_radius=0, command=master.is_sudoku_solved)
                cell.grid(row=i, column=j, sticky="nsew")
                row.append(cell)
            self.cells.append(row)

    def get_row(self,row):
        return self.cells[row]
    
    def get_col(self, col):
        res = []
        for i in range(0,3):
            res.append(self.cells[i][col])
        return res
    
    def check_block(self, value):
        for i in self.cells:
            for j in i:
                if(j.get_value()==value):
                    return True
        return False