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
    "call_color": "#42a5f5",
    "return_color": "#66bb6a",
    "base_case": "#ffa726",
    "text": "#ffffff",
    "arrow": "#ffeb3b",
    "highlight": "#ff6b6b"
}


class FactorialVisualizer:
    """Visualize factorial recursion with GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Factorial Recursion Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS["bg_dark"])
        
        self.call_stack = []
        self.current_step = 0
        self.animation_speed = 1000  # milliseconds
        self.is_animating = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Title
        if USE_CTK:
            title = ctk.CTkLabel(
                self.root, 
                text="Factorial Recursion Visualizer",
                font=("Arial", 24, "bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                self.root,
                text="Factorial Recursion Visualizer",
                font=("Arial", 24, "bold"),
                bg=COLORS["bg_dark"],
                fg=COLORS["text"]
            )
        title.pack(pady=20)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        input_frame.pack(pady=10)
        
        if USE_CTK:
            tk.Label(input_frame, text="Enter number:", font=("Arial", 14),
                    bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
            self.input_entry = ctk.CTkEntry(input_frame, width=100, font=("Arial", 14))
            self.input_entry.pack(side=tk.LEFT, padx=5)
            
            ctk.CTkButton(input_frame, text="Calculate", command=self.start_calculation,
                         font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
            ctk.CTkButton(input_frame, text="Reset", command=self.reset,
                         font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(input_frame, text="Enter number:", font=("Arial", 14),
                    bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
            self.input_entry = tk.Entry(input_frame, width=10, font=("Arial", 14))
            self.input_entry.pack(side=tk.LEFT, padx=5)
            
            tk.Button(input_frame, text="Calculate", command=self.start_calculation,
                     font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
            tk.Button(input_frame, text="Reset", command=self.reset,
                     font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Animation Speed:", font=("Arial", 12),
                bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.StringVar(value="Medium")
        speeds = ["Slow", "Medium", "Fast"]
        if USE_CTK:
            speed_menu = ctk.CTkOptionMenu(speed_frame, values=speeds,
                                          variable=self.speed_var,
                                          command=self.update_speed)
        else:
            speed_menu = ttk.Combobox(speed_frame, values=speeds,
                                     textvariable=self.speed_var,
                                     state="readonly", width=10)
            speed_menu.bind("<<ComboboxSelected>>", lambda e: self.update_speed(self.speed_var.get()))
        speed_menu.pack(side=tk.LEFT, padx=5)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas for call stack visualization
        canvas_frame = tk.Frame(content_frame, bg=COLORS["bg_medium"])
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(canvas_frame, text="Call Stack Visualization",
                font=("Arial", 16, "bold"), bg=COLORS["bg_medium"],
                fg=COLORS["text"]).pack(pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg=COLORS["bg_light"],
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text area for step-by-step explanation
        text_frame = tk.Frame(content_frame, bg=COLORS["bg_medium"])
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(text_frame, text="Step-by-Step Calculation",
                font=("Arial", 16, "bold"), bg=COLORS["bg_medium"],
                fg=COLORS["text"]).pack(pady=10)
        
        self.text_area = tk.Text(text_frame, bg=COLORS["bg_light"],
                                fg=COLORS["text"], font=("Courier", 11),
                                wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for color coding
        self.text_area.tag_config("call", foreground=COLORS["call_color"])
        self.text_area.tag_config("return", foreground=COLORS["return_color"])
        self.text_area.tag_config("base", foreground=COLORS["base_case"])
        self.text_area.tag_config("result", foreground=COLORS["highlight"],
                                 font=("Courier", 12, "bold"))
        
        # Result label
        self.result_label = tk.Label(self.root, text="", font=("Arial", 16, "bold"),
                                    bg=COLORS["bg_dark"], fg=COLORS["highlight"])
        self.result_label.pack(pady=10)
        
    def update_speed(self, choice):
        """Update animation speed"""
        speed_map = {"Slow": 1500, "Medium": 1000, "Fast": 500}
        self.animation_speed = speed_map.get(choice, 1000)
        
    def add_text(self, text, tag=None):
        """Add text to the text area"""
        self.text_area.config(state=tk.NORMAL)
        if tag:
            self.text_area.insert(tk.END, text + "\n", tag)
        else:
            self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
    def reset(self):
        """Reset the visualization"""
        self.call_stack = []
        self.current_step = 0
        self.is_animating = False
        self.canvas.delete("all")
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.result_label.config(text="")
        
    def start_calculation(self):
        """Start the factorial calculation"""
        if self.is_animating:
            messagebox.showwarning("Warning", "Animation already in progress!")
            return
            
        try:
            n = int(self.input_entry.get())
            if n < 0:
                messagebox.showerror("Error", "Please enter a non-negative integer!")
                return
            if n > 15:
                messagebox.showwarning("Warning", "Large numbers may take time to visualize!")
                
            self.reset()
            self.is_animating = True
            self.add_text(f"═══════════════════════════════════════", None)
            self.add_text(f"Calculating factorial of {n}...", "call")
            self.add_text(f"═══════════════════════════════════════\n", None)
            
            # Build call stack first
            self.build_call_stack(n, 0)
            
            # Start animation
            self.animate_step()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer!")
            
    def build_call_stack(self, n, depth):
        """Build the complete call stack"""
        self.call_stack.append({
            'type': 'call',
            'n': n,
            'depth': depth,
            'explanation': f"Calling factorial({n})"
        })
        
        if n == 0 or n == 1:
            self.call_stack.append({
                'type': 'base',
                'n': n,
                'depth': depth,
                'result': 1,
                'explanation': f"Base case reached! factorial({n}) = 1"
            })
        else:
            self.build_call_stack(n - 1, depth + 1)
            result = n * self.call_stack[-1]['result']
            self.call_stack.append({
                'type': 'return',
                'n': n,
                'depth': depth,
                'result': result,
                'explanation': f"Returning: {n} × factorial({n-1}) = {n} × {result//n} = {result}"
            })
            
    def animate_step(self):
        """Animate one step of the recursion"""
        if self.current_step >= len(self.call_stack):
            self.is_animating = False
            final_result = self.call_stack[-1]['result']
            self.result_label.config(text=f"Final Result: {final_result}")
            self.add_text(f"\n{'='*50}", None)
            self.add_text(f"FINAL ANSWER: {final_result}", "result")
            self.add_text(f"{'='*50}", None)
            return
            
        step = self.call_stack[self.current_step]
        
        # Add explanation
        if step['type'] == 'call':
            self.add_text(f"{'  ' * step['depth']}➤ {step['explanation']}", "call")
        elif step['type'] == 'base':
            self.add_text(f"{'  ' * step['depth']}★ {step['explanation']}", "base")
        elif step['type'] == 'return':
            self.add_text(f"{'  ' * step['depth']}◄ {step['explanation']}", "return")
            
        # Update canvas
        self.draw_call_stack()
        
        self.current_step += 1
        self.root.after(self.animation_speed, self.animate_step)
        
    def draw_call_stack(self):
        """Draw the current state of the call stack"""
        self.canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 500
            
        # Calculate active calls in stack
        active_calls = []
        for i in range(self.current_step + 1):
            if i >= len(self.call_stack):
                break
            step = self.call_stack[i]
            if step['type'] == 'call':
                active_calls.append(step)
            elif step['type'] in ['base', 'return']:
                # Remove the corresponding call
                for j in range(len(active_calls) - 1, -1, -1):
                    if active_calls[j]['n'] == step['n']:
                        active_calls[j]['result'] = step.get('result', 1)
                        active_calls[j]['returning'] = True
                        break
                        
        # Draw stack frames
        box_height = 60
        box_width = 200
        spacing = 10
        start_y = canvas_height - 100
        
        for i, call in enumerate(active_calls):
            y = start_y - i * (box_height + spacing)
            x = canvas_width // 2 - box_width // 2
            
            # Determine color based on state
            if call.get('returning'):
                fill_color = COLORS["return_color"]
            elif call['n'] <= 1:
                fill_color = COLORS["base_case"]
            else:
                fill_color = COLORS["call_color"]
                
            # Draw box
            self.canvas.create_rectangle(x, y, x + box_width, y + box_height,
                                        fill=fill_color, outline="white", width=2)
            
            # Draw text
            text = f"factorial({call['n']})"
            if call.get('returning'):
                text += f"\n= {call['result']}"
                
            self.canvas.create_text(x + box_width // 2, y + box_height // 2,
                                   text=text, fill="white",
                                   font=("Arial", 14, "bold"))
            
            # Draw arrow to next level
            if i < len(active_calls) - 1:
                arrow_start_y = y - spacing // 2
                arrow_end_y = y - spacing - box_height + spacing // 2
                self.canvas.create_line(canvas_width // 2, arrow_start_y,
                                      canvas_width // 2, arrow_end_y,
                                      arrow=tk.LAST, fill=COLORS["arrow"],
                                      width=3)


def main():
    """Main function to run the visualizer"""
    if USE_CTK:
        root = ctk.CTk()
    else:
        root = tk.Tk()
        
    app = FactorialVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
