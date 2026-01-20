import tkinter as tk
from tkinter import messagebox
import time

#maximum of 40 terms to prevent performance issues
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
    "node_color": "#42a5f5",
    "highlighted": "#66bb6a",
    "current": "#ffa726",
    "text": "#ffffff",
    "arrow": "#ffeb3b",
    "sequence_bg": "#ff6b6b",
    "grid_line": "#555555"
}


class FibonacciVisualizer:
    """Visualize Fibonacci sequence with GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Fibonacci Sequence Visualizer")
        self.root.geometry("1400x850")
        self.root.configure(bg=COLORS["bg_dark"])
        
        self.sequence = []
        self.current_index = 0
        self.animation_speed = 1000
        self.is_animating = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Title
        if USE_CTK:
            title = ctk.CTkLabel(
                self.root,
                text="Fibonacci Sequence Visualizer",
                font=("Arial", 28, "bold"),
                text_color=COLORS["text"]
            )
        else:
            title = tk.Label(
                self.root,
                text="Fibonacci Sequence Visualizer",
                font=("Arial", 28, "bold"),
                bg=COLORS["bg_dark"],
                fg=COLORS["text"]
            )
        title.pack(pady=20)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        input_frame.pack(pady=10)
        
        if USE_CTK:
            tk.Label(input_frame, text="Enter term number:", font=("Arial", 14),
                    bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
            self.input_entry = ctk.CTkEntry(input_frame, width=100, font=("Arial", 14))
            self.input_entry.pack(side=tk.LEFT, padx=5)
            self.input_entry.insert(0, "10")
            
            ctk.CTkButton(input_frame, text="Generate", command=self.start_sequence,
                         font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
            ctk.CTkButton(input_frame, text="Reset", command=self.reset,
                         font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(input_frame, text="Enter term number:", font=("Arial", 14),
                    bg=COLORS["bg_dark"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
            self.input_entry = tk.Entry(input_frame, width=10, font=("Arial", 14))
            self.input_entry.pack(side=tk.LEFT, padx=5)
            self.input_entry.insert(0, "10")
            
            tk.Button(input_frame, text="Generate", command=self.start_sequence,
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
            from tkinter import ttk
            speed_menu = ttk.Combobox(speed_frame, values=speeds,
                                     textvariable=self.speed_var,
                                     state="readonly", width=10)
            speed_menu.bind("<<ComboboxSelected>>", lambda e: self.update_speed(self.speed_var.get()))
        speed_menu.pack(side=tk.LEFT, padx=5)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas for sequence visualization
        canvas_frame = tk.Frame(content_frame, bg=COLORS["bg_medium"])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(canvas_frame, text="Fibonacci Sequence Visualization",
                font=("Arial", 16, "bold"), bg=COLORS["bg_medium"],
                fg=COLORS["text"]).pack(pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg=COLORS["bg_light"],
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info panel
        info_frame = tk.Frame(content_frame, bg=COLORS["bg_medium"])
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(info_frame, text="Sequence Information",
                font=("Arial", 16, "bold"), bg=COLORS["bg_medium"],
                fg=COLORS["text"]).pack(pady=10)
        
        self.info_text = tk.Text(info_frame, bg=COLORS["bg_light"],
                                fg=COLORS["text"], font=("Courier", 12),
                                wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags
        self.info_text.tag_config("title", foreground=COLORS["sequence_bg"],
                                 font=("Courier", 13, "bold"))
        self.info_text.tag_config("number", foreground=COLORS["current"])
        self.info_text.tag_config("calculation", foreground=COLORS["highlighted"])
        
        # Result label
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"),
                                    bg=COLORS["bg_dark"], fg=COLORS["sequence_bg"])
        self.result_label.pack(pady=10)
        
    def update_speed(self, choice):
        """Update animation speed"""
        speed_map = {"Slow": 1500, "Medium": 800, "Fast": 400}
        self.animation_speed = speed_map.get(choice, 800)
        
    def add_info(self, text, tag=None):
        """Add text to the info area"""
        self.info_text.config(state=tk.NORMAL)
        if tag:
            self.info_text.insert(tk.END, text, tag)
        else:
            self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
        
    def reset(self):
        """Reset the visualization"""
        self.sequence = []
        self.current_index = 0
        self.is_animating = False
        self.canvas.delete("all")
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.result_label.config(text="")
        
    def start_sequence(self):
        """Start generating the Fibonacci sequence"""
        if self.is_animating:
            messagebox.showwarning("Warning", "Animation already in progress!")
            return
            
        try:
            n = int(self.input_entry.get())
            
            # Validate input
            if n <= 0:
                messagebox.showerror("Error", "Please enter a positive integer!")
                return
            
            # Set maximum limit to prevent performance issues
            MAX_TERMS = 40
            if n > MAX_TERMS:
                response = messagebox.askyesno(
                    "Large Number Warning",
                    f"You entered {n} terms, but the maximum recommended is {MAX_TERMS}.\n\n"
                    f"Generating {n} terms may take a very long time and use significant memory.\n\n"
                    f"Do you want to continue?"
                )
                if not response:
                    return
            
            # Additional warning for very large numbers
            if n > 50:
                messagebox.showwarning(
                    "Extreme Value Warning",
                    f"Generating {n} terms could freeze the application.\n"
                    f"Please consider using a smaller number (≤ 40)."
                )
            
            self.reset()
            self.is_animating = True
            
            # Generate sequence with progress indicator
            self.sequence = []
            try:
                a, b = 0, 1
                for i in range(n):
                    self.sequence.append(a)
                    a, b = b, a + b
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate sequence: {str(e)}")
                self.is_animating = False
                return
                
            self.add_info("Fibonacci Sequence Generator\n", "title")
            self.add_info("═" * 40 + "\n\n", None)
            self.add_info(f"Total Terms: {n}\n", "calculation")
            self.add_info(f"Maximum Value: {self.sequence[-1]}\n\n", "calculation")
            
            # Start animation
            self.current_index = 0
            self.animate_sequence()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer!")
            self.is_animating = False
        except MemoryError:
            messagebox.showerror("Error", "Not enough memory to generate this sequence!")
            self.is_animating = False
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.is_animating = False
            
    def animate_sequence(self):
        """Animate the sequence generation"""
        if self.current_index >= len(self.sequence):
            self.is_animating = False
            # Show final sequence
            self.add_info("\n" + "═" * 40 + "\n", None)
            self.add_info("COMPLETE SEQUENCE:\n", "title")
            sequence_str = ", ".join(map(str, self.sequence))
            self.add_info(sequence_str, "calculation")
            
            total = sum(self.sequence)
            self.add_info(f"\n\nSum of all terms: {total}", "calculation")
            self.result_label.config(
                text=f"Generated {len(self.sequence)} terms | Final: {self.sequence[-1]}"
            )
            return
            
        # Draw current state
        self.draw_sequence()
        
        # Add current term info
        term_num = self.current_index + 1
        term_value = self.sequence[self.current_index]
        
        if self.current_index < 2:
            self.add_info(f"Term {term_num}: {term_value} (Starting value)\n", "number")
        else:
            prev1 = self.sequence[self.current_index - 1]
            prev2 = self.sequence[self.current_index - 2]
            self.add_info(
                f"Term {term_num}: {prev2} + {prev1} = {term_value}\n",
                "number"
            )
            
        self.current_index += 1
        self.root.after(self.animation_speed, self.animate_sequence)
        
    def draw_sequence(self):
        """Draw the current sequence on canvas"""
        self.canvas.delete("all")
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
            
        # Calculate display parameters
        padding = 40
        available_width = canvas_width - 2 * padding
        available_height = canvas_height - 2 * padding
        
        # Draw background grid
        self.canvas.create_line(padding, canvas_height - padding,
                              canvas_width - padding, canvas_height - padding,
                              fill=COLORS["grid_line"], width=2)
        self.canvas.create_line(padding, padding,
                              padding, canvas_height - padding,
                              fill=COLORS["grid_line"], width=2)
        
        # Draw axis labels
        self.canvas.create_text(canvas_width - padding + 20, canvas_height - padding,
                              text="Term", fill=COLORS["text"], font=("Arial", 10))
        self.canvas.create_text(padding - 20, padding - 20,
                              text="Value", fill=COLORS["text"], font=("Arial", 10))
        
        if not self.sequence:
            return
            
        # Calculate bar width and spacing
        current_terms = min(self.current_index + 1, len(self.sequence))
        bar_width = available_width / max(current_terms + 1, 2)
        
        # Find max value for scaling
        max_value = max(self.sequence[:current_terms]) if current_terms > 0 else 1
        max_value = max(max_value, 1)  # Avoid division by zero
        
        # Draw bars for each term
        for i in range(current_terms):
            value = self.sequence[i]
            
            # Calculate bar height
            bar_height = (value / max_value) * available_height * 0.8
            
            # Calculate positions
            x = padding + (i + 1) * bar_width
            y_top = canvas_height - padding - bar_height
            y_bottom = canvas_height - padding
            
            # Determine color (highlight current, normal for previous)
            if i == self.current_index:
                color = COLORS["current"]
            elif i < self.current_index:
                color = COLORS["highlighted"]
            else:
                color = COLORS["node_color"]
                
            # Draw bar
            self.canvas.create_rectangle(x - bar_width * 0.4, y_top,
                                        x + bar_width * 0.4, y_bottom,
                                        fill=color, outline="white", width=2)
            
            # Draw value text on top of bar
            self.canvas.create_text(x, y_top - 15,
                                  text=str(value),
                                  fill="white",
                                  font=("Arial", 11, "bold"))
            
            # Draw term number below bar
            self.canvas.create_text(x, y_bottom + 15,
                                  text=f"T{i+1}",
                                  fill=COLORS["text"],
                                  font=("Arial", 10))


def main():
    """Main function to run the visualizer"""
    if USE_CTK:
        root = ctk.CTk()
    else:
        root = tk.Tk()
        
    app = FibonacciVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()