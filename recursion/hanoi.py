import tkinter as tk
from tkinter import messagebox
import time

# Try to import customtkinter, fallback to tkinter if not available
try:
    import customtkinter as ctk
    USE_CTK = True
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    USE_CTK = False
    print("CustomTkinter not found. Using standard tkinter instead.")

# Colors
COLORS = {
    "bg_dark": "#1a1a1a",
    "bg_medium": "#2b2b2b",
    "bg_light": "#3a3a3a",
    "peg": "#8b4513",
    "disk": "#42a5f5",
    "text": "#ffffff",
    "move_count": "#ffeb3b"
}

class TowerOfHanoi:
    def __init__(self, master, num_disks):
        self.master = master
        self.master.title("Tower of Hanoi - Recursion Visualizer")
        if USE_CTK:
            self.master.geometry("900x800")
            self.master.configure(bg=COLORS["bg_dark"])
        
        self.num_disks = num_disks
        self.canvas_width = 800
        self.canvas_height = 400
        self.peg_width = 10
        self.peg_height = 200
        self.disk_height = 20
        self.peg_positions = [150, 400, 650]
        
        # Control frame
        control_frame = tk.Frame(master, bg=COLORS["bg_dark"])
        control_frame.pack(pady=10)
        
        # Title
        if USE_CTK:
            title = ctk.CTkLabel(
                master,
                text="Tower of Hanoi - Recursive Solution",
                font=("Arial", 24, "bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                master,
                text="Tower of Hanoi - Recursive Solution",
                font=("Arial", 24, "bold"),
                bg=COLORS["bg_dark"],
                fg=COLORS["text"]
            )
        title.pack(pady=15)
        
        # Move counter
        counter_frame = tk.Frame(master, bg=COLORS["bg_dark"])
        counter_frame.pack(pady=5)
        
        tk.Label(counter_frame, text="Moves: ", font=("Arial", 14),
                bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
        
        self.move_label = tk.Label(counter_frame, text="0", font=("Arial", 14, "bold"),
                                   bg=COLORS["bg_dark"], fg=COLORS["move_count"])
        self.move_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(counter_frame, text=f"/ {2**self.num_disks - 1} required", 
                font=("Arial", 14), bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
        
        # Canvas for visualization
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height,
                               bg=COLORS["bg_light"], highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Info label
        self.info_label = tk.Label(master, text="", font=("Arial", 12),
                                  bg=COLORS["bg_dark"], fg=COLORS["text"])
        self.info_label.pack(pady=5)
        
        self.pegs = [[], [], []]  # Each peg holds a list of disks (by size)
        self.disks = []
        self.move_count = 0
        
        self.create_pegs()
        self.create_disks()
        
        # Start solving after a delay
        self.master.after(1000, self.solve_hanoi, self.num_disks, 0, 2, 1)


    def create_pegs(self):
        base_y = self.canvas_height - 50
        for i, x in enumerate(self.peg_positions):
            self.canvas.create_rectangle(x - self.peg_width//2, base_y - self.peg_height,
                                         x + self.peg_width//2, base_y, fill=COLORS["peg"], outline="white", width=2)
            # Add peg labels
            self.canvas.create_text(x, base_y + 25, text=f"Peg {i+1}", fill=COLORS["text"],
                                   font=("Arial", 12, "bold"))

    def create_disks(self):
        base_y = self.canvas_height - 50
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffa502', '#96ceb4', '#dfe6e9']
        
        for i in range(self.num_disks):
            width = 30 + (self.num_disks - i) * 20
            x = self.peg_positions[0]
            y = base_y - (i + 1) * self.disk_height
            color = colors[i % len(colors)]
            
            disk = self.canvas.create_rectangle(x - width//2, y - self.disk_height,
                                                x + width//2, y, fill=color, outline='white', width=2)
            self.pegs[0].append((disk, width))
            self.disks.append(disk)

    def move_disk(self, from_peg, to_peg):
        if not self.pegs[from_peg]:
            return
            
        disk, width = self.pegs[from_peg].pop()
        self.move_count += 1
        self.move_label.config(text=str(self.move_count))
        
        base_y = self.canvas_height - 50
        new_y = base_y - (len(self.pegs[to_peg]) + 1) * self.disk_height
        new_x = self.peg_positions[to_peg]
        
        # Update info label
        peg_names = ["1", "2", "3"]
        self.info_label.config(text=f"Moving disk from Peg {peg_names[from_peg]} to Peg {peg_names[to_peg]}")
        
        # Animate disk moving up
        current_coords = self.canvas.coords(disk)
        current_x = (current_coords[0] + current_coords[2]) / 2
        current_y = current_coords[3]
        
        while current_y > 50:
            self.canvas.move(disk, 0, -5)
            self.canvas.update()
            time.sleep(0.01)
            current_y -= 5
        
        # Animate disk moving horizontally
        while abs(current_x - new_x) > 5:
            step = 5 if new_x > current_x else -5
            self.canvas.move(disk, step, 0)
            self.canvas.update()
            time.sleep(0.01)
            current_x += step
        
        # Animate disk moving down
        while current_y < new_y:
            self.canvas.move(disk, 0, 5)
            self.canvas.update()
            time.sleep(0.01)
            current_y += 5
        
        # Final adjustment to exact position
        final_coords = [new_x - width//2, new_y - self.disk_height, new_x + width//2, new_y]
        self.canvas.coords(disk, *final_coords)
        self.pegs[to_peg].append((disk, width))

    def solve_hanoi(self, n, from_peg, to_peg, aux_peg):
        if n == 1:
            self.move_disk(from_peg, to_peg)
            return
        self.solve_hanoi(n-1, from_peg, aux_peg, to_peg)
        self.move_disk(from_peg, to_peg)
        self.solve_hanoi(n-1, aux_peg, to_peg, from_peg)

if __name__ == "__main__":
    if USE_CTK:
        root = ctk.CTk()
    else:
        root = tk.Tk()
        root.configure(bg=COLORS["bg_dark"])
    
    game = TowerOfHanoi(root, num_disks=5)
    root.mainloop()
