```python
import tkinter as tk
from tkinter import simpledialog, messagebox
import time

class RecursionVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recursion Visualizer")
        self.geometry("900x600")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Buttons to select simulation
        self.btn_fib = tk.Button(self, text="Fibonacci Sequence", command=self.fibonacci_ui, width=20, height=2)
        self.btn_fib.grid(row=0, column=0, padx=10, pady=10)

        self.btn_fact = tk.Button(self, text="Factorial", command=self.factorial_ui, width=20, height=2)
        self.btn_fact.grid(row=0, column=1, padx=10, pady=10)

        self.btn_hanoi = tk.Button(self, text="Towers of Hanoi", command=self.towers_of_hanoi_ui, width=20, height=2)
        self.btn_hanoi.grid(row=0, column=2, padx=10, pady=10)

        # Canvas for drawing
        self.canvas = tk.Canvas(self, width=880, height=500, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Text widget for output
        self.text_output = tk.Text(self, height=8, width=110)
        self.text_output.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.text_output.config(state=tk.DISABLED)

    def clear_all(self):
        self.canvas.delete("all")
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.config(state=tk.DISABLED)

    # ---------------- Fibonacci Sequence ----------------
    def fibonacci_ui(self):
        self.clear_all()
        n = simpledialog.askinteger("Fibonacci Sequence", "Enter the term number (n) to end at (max 30):", minvalue=1, maxvalue=30)
        if n is None:
            return
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, f"Calculating Fibonacci sequence up to term {n}...\n")
        self.text_output.config(state=tk.DISABLED)
        self.fib_sequence = []
        self.fibonacci_visual(n)

    def fibonacci_visual(self, n):
        self.fib_sequence = []
        self.canvas.delete("all")
        self._fib_recursive(n)
        # Draw sequence visually
        self.canvas.delete("all")
        x_start = 20
        y = 250
        radius = 20
        gap = 10
        for i, val in enumerate(self.fib_sequence):
            x = x_start + i * (2*radius + gap)
            self.canvas.create_oval(x, y-radius, x+2*radius, y+radius, fill="lightblue")
            self.canvas.create_text(x+radius, y, text=str(val), font=("Arial", 12, "bold"))
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, f"Fibonacci sequence: {self.fib_sequence}\n")
        self.text_output.config(state=tk.DISABLED)

    def _fib_recursive(self, n):
        # Use memoization to speed up
        memo = {}
        def fib(k):
            if k in memo:
                return memo[k]
            if k == 1 or k == 2:
                memo[k] = 1
                return 1
            memo[k] = fib(k-1) + fib(k-2)
            return memo[k]
        for i in range(1, n+1):
            self.fib_sequence.append(fib(i))

    # ---------------- Factorial ----------------
    def factorial_ui(self):
        self.clear_all()
        n = simpledialog.askinteger("Factorial", "Enter the number to calculate factorial (max 15):", minvalue=0, maxvalue=15)
        if n is None:
            return
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, f"Calculating factorial of {n}...\n")
        self.text_output.config(state=tk.DISABLED)
        self.factorial_steps = []
        self.factorial_visual(n)

    def factorial_visual(self, n):
        self.factorial_steps.clear()
        self.canvas.delete("all")
        result = self._factorial_recursive(n)
        # Visualize recursion stack as boxes
        self.canvas.delete("all")
        box_width = 120
        box_height = 40
        gap = 10
        max_boxes = min(len(self.factorial_steps), 10)
        start_x = 20
        start_y = 250
        # Show last max_boxes calls
        steps_to_show = self.factorial_steps[-max_boxes:]
        for i, (num, res) in enumerate(reversed(steps_to_show)):
            x = start_x + i * (box_width + gap)
            y = start_y
            self.canvas.create_rectangle(x, y, x+box_width, y+box_height, fill="lightgreen")
            self.canvas.create_text(x+box_width/2, y+box_height/2, text=f"fact({num}) = {res}", font=("Arial", 12, "bold"))
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, f"Factorial({n}) = {result}\n")
        self.text_output.config(state=tk.DISABLED)

    def _factorial_recursive(self, n):
        if n == 0 or n == 1:
            self.factorial_steps.append((n, 1))
            return 1
        res = n * self._factorial_recursive(n-1)
        self.factorial_steps.append((n, res))
        return res

    # ---------------- Towers of Hanoi ----------------
    def towers_of_hanoi_ui(self):
        self.clear_all()
        n = simpledialog.askinteger("Towers of Hanoi", "Enter number of disks (max 6):", minvalue=1, maxvalue=6)
        if n is None:
            return
        self.num_disks = n
        self.canvas.delete("all")
        self.hanoi_rods = {'A': [], 'B': [], 'C': []}
        for disk in range(n, 0, -1):
            self.hanoi_rods['A'].append(disk)
        self.draw_hanoi()
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, f"Solving Towers of Hanoi with {n} disks...\n")
        self.text_output.config(state=tk.DISABLED)
        self.after(1000, lambda: self.solve_hanoi(n, 'A', 'C', 'B'))

    def draw_hanoi(self):
        self.canvas.delete("all")
        width = 880
        height = 500
        rod_width = 10
        rod_height = 200
        base_y = 400
        rod_positions = {'A': width//4, 'B': width//2, 'C': 3*width//4}
        disk_height = 20
        max_disk_width = 150
        min_disk_width = 40

        # Draw rods
        for rod in rod_positions:
            x = rod_positions[rod]
            self.canvas.create_rectangle(x-rod_width//2, base_y-rod_height, x+rod_width//2, base_y, fill="brown")
            self.canvas.create_text(x, base_y+20, text=rod, font=("Arial", 14, "bold"))

        # Draw disks on rods
        for rod in 'ABC':
            disks = self.hanoi_rods[rod]
            x = rod_positions[rod]
            for i, disk in enumerate(disks):
                disk_width = min_disk_width + (disk-1)*(max_disk_width - min_disk_width)//(self.num_disks-1 if self.num_disks>1 else 1)
                y = base_y - disk_height*(i+1)
                self.canvas.create_rectangle(x - disk_width//2, y - disk_height + 2, x + disk_width//2, y + 2, fill="skyblue", outline="black")
                self.canvas.create_text(x, y - disk_height//2 + 2, text=str(disk), font=("Arial", 12, "bold"))

    def solve_hanoi(self, n, source, target, auxiliary):
        if n == 1:
            self.move_disk(source, target)
            self.draw_hanoi()
            self.text_output.config(state=tk.NORMAL)
            self.text_output.insert(tk.END, f"Move disk 1 from {source} to {target}\n")
            self.text_output.see(tk.END)
            self.text_output.config(state=tk.DISABLED)
            self.update()
            time.sleep(0.8)
        else:
            self.solve_hanoi(n-1, source, auxiliary, target)
            self.move_disk(source, target)
            self.draw_hanoi()
            self.text_output.config(state=tk.NORMAL)
            self.text_output.insert(tk.END, f"Move disk {n} from {source} to {target}\n")
            self.text_output.see(tk.END)
            self.text_output.config(state=tk.DISABLED)
            self.update()
            time.sleep(0.8)
