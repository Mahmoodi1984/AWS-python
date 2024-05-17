import tkinter as tk

class Calculator(tk.Tk) :
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("480x620")
        self.result = tk.Entry(self, font=("Arial", 30))
        self.result.grid(row=0, columspan=4, padx=10,)