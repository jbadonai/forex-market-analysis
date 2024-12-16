import tkinter as tk
from tkinter import ttk
import os
import subprocess


class TerminalFrame(ttk.Frame):
    def __init__(self, parent, script_path):
        super().__init__(parent)
        self.script_path = script_path
        self.terminal = tk.Text(self, wrap='word', height=10, width=40)
        self.terminal.pack(expand=True, fill='both')
        self.run_script()

    def run_script(self):
        process = subprocess.Popen(['python', self.script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, b''):
            self.terminal.insert(tk.END, line.decode('utf-8'))
        process.stdout.close()
        process.wait()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Embedded Terminal GUI")
        self.geometry("800x600")

        script_path = os.path.join(os.getcwd(), 'market_analysis.py')

        # Create a 2x2 grid of terminal frames
        for row in range(2):
            for col in range(2):
                frame = TerminalFrame(self, script_path)
                frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        # Configure grid weights
        for i in range(2):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
