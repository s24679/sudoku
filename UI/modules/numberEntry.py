from customtkinter import CTkEntry, CTkFont
from tkinter import font, StringVar

class NumberEntry(CTkEntry):
    def __init__(self, master=None, min_value=None, max_value=None, command=None, **kwargs):
        self.var = StringVar()
        if command != None:
            self.var.trace_add("write",command)
        super().__init__(master, textvariable=self.var, **kwargs)

        self.min_value = min_value
        self.max_value = max_value

        self._font = CTkFont(size=12)
        self.configure(font=self._font)

        self.bind('<Configure>', self._resize_font)

        vcmd = (self.register(self._validate), '%P')
        self.configure(validate='key', validatecommand=vcmd)

    def _validate(self, value):

        if(value == ''):
            return True

        try:
            value = int(value)
        except ValueError:
            return False

        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False

        return True

    def get_value(self):
        val = self.var.get()
        if(val == None or val == '' or val == 'None'):
            return None
        return int(val)

    def set_value(self, value):
        if value == None:
            value = ''
        try:
            self.var.set(str(value))
        except Exception as e:
            print(f"[ERROR] Could not set value: {e} to value: {value}")

    def _resize_font(self, event):
        new_size = max(8, int(event.height * 0.5))
        if self._font.cget("size") != new_size:
            self._font.configure(size=new_size)
