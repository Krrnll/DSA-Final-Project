import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from collections import deque
import sys
import os
import importlib.util

# Try to import customtkinter, fallback to tkinter if not available
try:
    import customtkinter as ctk
    USE_CTK = True
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    USE_CTK = False
    print("CustomTkinter not found. Using standard tkinter instead.")
    print("To install CustomTkinter, run: pip install customtkinter")


# Constants
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 600
NODE_RADIUS = 20
X_SPACING = 40  # Reduced for narrower tree
Y_SPACING = 60  # Reduced for more compact vertical spacing
CANVAS_PADDING = 50
HIGHLIGHT_DURATION = 2000  # milliseconds

# Colors - Professional Dark Theme
COLORS = {
    "bg_dark": "#121212",        # Base dark background (avoid pure black)
    "bg_medium": "#1E1E1E",      # Elevated surface
    "bg_light": "#2A2A2A",       # Further elevated surface
    "text_primary": "#E0E0E0",   # High emphasis text (off-white)
    "text_secondary": "#B0B0B0", # Secondary text (60% opacity equivalent)
    "node_fill": "#42A5F5",      # Primary blue for nodes
    "node_outline": "#1E88E5",   # Darker blue outline
    "edge": "#64B5F6",           # Soft blue for edges
    "highlight_fill": "#FF6B6B", # Muted red for highlights
    "highlight_outline": "#FF5252",
    "accent_primary": "#BB86FC", # Purple accent for primary actions
    "accent_secondary": "#FFD700",# Gold for secondary highlights
    "success": "#4CAF50",        # Green for success states
    "text": "#E0E0E0"            # Default text color
}


class TreeNode:
    """Node class for binary tree"""
    def __init__(self, value: int):
        self.value = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None
        self.x = 0  # x coordinate for drawing
        self.y = 0  # y coordinate for drawing


class BinaryTree:
    """Basic Binary Tree implementation"""
    def __init__(self):
        self.root: Optional[TreeNode] = None
    
    def insert(self, value: int) -> bool:
        """Insert value into binary tree (level-order insertion)"""
        if self.root is None:
            self.root = TreeNode(value)
            return True
        
        # Level-order insertion using deque for better performance
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            
            if node.left is None:
                node.left = TreeNode(value)
                return True
            elif node.right is None:
                node.right = TreeNode(value)
                return True
            else:
                queue.append(node.left)
                queue.append(node.right)
        return False
    
    def delete(self, value: int) -> bool:
        """Delete a node from binary tree"""
        if self.root is None:
            return False
        
        # Find the node and the deepest node
        node_to_delete = None
        deepest_node = None
        parent_of_deepest = None
        
        # Find node to delete using deque for better performance
        queue = deque([(self.root, None)])
        while queue:
            node, parent = queue.popleft()
            if node.value == value:
                node_to_delete = node
            if node.left or node.right:
                if node.left:
                    queue.append((node.left, node))
                if node.right:
                    queue.append((node.right, node))
            else:
                deepest_node = node
                parent_of_deepest = parent
        
        if node_to_delete is None:
            return False
        
        # Replace node_to_delete with deepest_node
        if deepest_node and node_to_delete != deepest_node:
            node_to_delete.value = deepest_node.value
            if parent_of_deepest.left == deepest_node:
                parent_of_deepest.left = None
            else:
                parent_of_deepest.right = None
        elif node_to_delete == self.root:
            self.root = None
        
        return True
    
    def search(self, value: int) -> bool:
        """Search for a value in binary tree"""
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node: Optional[TreeNode], value: int) -> bool:
        if node is None:
            return False
        if node.value == value:
            return True
        return self._search_recursive(node.left, value) or self._search_recursive(node.right, value)
    
    def get_height(self, node: Optional[TreeNode] = None) -> int:
        """Get height of the tree"""
        if node is None:
            node = self.root
        if node is None:
            return 0
        return 1 + max(self.get_height(node.left), self.get_height(node.right))
    
    def inorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Inorder traversal (iterative to avoid stack overflow)"""
        if self.root is None:
            return []
        
        result = []
        stack = []
        current = self.root
        
        while current or stack:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            result.append(current.value)
            current = current.right
        
        return result
    
    def preorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Preorder traversal (iterative to avoid stack overflow)"""
        if self.root is None:
            return []
        
        result = []
        stack = [self.root]
        
        while stack:
            current = stack.pop()
            result.append(current.value)
            if current.right:
                stack.append(current.right)
            if current.left:
                stack.append(current.left)
        
        return result
    
    def postorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Postorder traversal (iterative to avoid stack overflow)"""
        if self.root is None:
            return []
        
        result = []
        stack1 = [self.root]
        stack2 = []
        
        while stack1:
            current = stack1.pop()
            stack2.append(current)
            if current.left:
                stack1.append(current.left)
            if current.right:
                stack1.append(current.right)
        
        while stack2:
            result.append(stack2.pop().value)
        
        return result


class BinarySearchTree(BinaryTree):
    """Binary Search Tree implementation"""
    def insert(self, value: int) -> bool:
        """Insert value into BST following BST property"""
        if self.root is None:
            self.root = TreeNode(value)
            return True
        return self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node: TreeNode, value: int) -> bool:
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
                return True
            return self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = TreeNode(value)
                return True
            return self._insert_recursive(node.right, value)
        else:
            # Value already exists
            return False
    
    def delete(self, value: int) -> bool:
        """Delete a node from BST maintaining BST property"""
        # Check if node exists before deletion
        if not self.search(value):
            return False
        self.root = self._delete_recursive(self.root, value)
        return True
    
    def _delete_recursive(self, node: Optional[TreeNode], value: int) -> Optional[TreeNode]:
        if node is None:
            return None
        
        if value < node.value:
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            node.right = self._delete_recursive(node.right, value)
        else:
            # Node to delete found
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Node has two children - find inorder successor
                min_node = self._find_min(node.right)
                node.value = min_node.value
                node.right = self._delete_recursive(node.right, min_node.value)
        return node
    
    def _find_min(self, node: TreeNode) -> TreeNode:
        """Find minimum value node"""
        while node.left:
            node = node.left
        return node
    
    def search(self, value: int) -> bool:
        """Search for a value in BST"""
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node: Optional[TreeNode], value: int) -> bool:
        if node is None:
            return False
        if node.value == value:
            return True
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)


class TreeVisualizer:
    """Visual representation of binary tree using customtkinter or tkinter"""
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Tree & BST Visualization")
        self.root.geometry("1200x800")
        if USE_CTK:
            self.root.configure(bg=COLORS["bg_dark"])
        else:
            self.root.configure(bg="gray20")
        
        self.tree_type = "Binary Tree"
        self.tree: BinaryTree = BinaryTree()
        self.use_ctk = USE_CTK
        self.current_traversal = ""  # Store current traversal for display
        
        self.setup_ui()
        
        # Initial display update
        self.root.after(100, self.update_display)
        
        # Bind mouse wheel for scrolling (will be bound after canvas is created)
        self.root.after(200, self._bind_scroll_events)
    
    def _bind_scroll_events(self):
        """Bind mouse wheel scrolling events"""
        # Windows and Mac
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        # Also bind to canvas container for better scrolling
        canvas_container = self.canvas.master
        canvas_container.bind("<MouseWheel>", self._on_mousewheel)
        canvas_container.bind("<Button-4>", self._on_mousewheel)
        canvas_container.bind("<Button-5>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Check if shift is held for horizontal scrolling
        if event.state & 0x1:  # Shift key
            if event.delta:
                self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 4:
                    self.canvas.xview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.xview_scroll(1, "units")
        else:  # Vertical scrolling
            if event.delta:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = self._create_frame(self.root, fill="both", expand=True, padx=10, pady=10)
        
        # Traversal Output Panel (always visible at top)
        traversal_panel = self._create_frame(main_frame, fill="x", pady=(0, 10), bg="gray25")
        tk.Label(traversal_panel, text="Traversal Results (TLR/Preorder | LTR/Inorder | LRT/Postorder):", 
                font=("Arial", 10, "bold"), bg="gray25", fg="white").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.traversal_text = tk.Text(traversal_panel, height=3, bg=COLORS["bg_medium"], 
                                      fg=COLORS["text"], font=("Courier", 9), relief=tk.FLAT)
        self.traversal_text.pack(fill="x", padx=10, pady=5)
        self.traversal_text.config(state=tk.DISABLED)
        
        # Control panel
        control_frame = self._create_frame(main_frame, fill="x", pady=(0, 10), bg="gray25")
        self._setup_control_panel(control_frame)
        
        # Canvas frame
        canvas_frame = self._create_frame(main_frame, fill="both", expand=True, bg="gray20")
        self._setup_canvas(canvas_frame)
        
        # Information panel
        info_frame = self._create_frame(main_frame, fill="x", pady=(10, 0), bg="gray25")
        self._setup_info_panel(info_frame)
    
    def _create_frame(self, parent, **kwargs):
        """Helper method to create frames (CTK or standard)"""
        bg = kwargs.pop("bg", None)
        if self.use_ctk and not bg:
            frame = ctk.CTkFrame(parent)
        else:
            bg = bg or "gray20"
            frame = tk.Frame(parent, bg=bg)
        frame.pack(**kwargs)
        return frame
    
    def _setup_control_panel(self, control_frame):
        """Setup control panel with buttons and input"""
        # Tree type selection
        self._create_label(control_frame, "Tree Type:", 0, 0)
        
        self.type_var = tk.StringVar(value="Binary Tree")
        if self.use_ctk:
            type_menu = ctk.CTkOptionMenu(
                control_frame,
                values=["Binary Tree", "Binary Search Tree"],
                variable=self.type_var,
                command=self.change_tree_type
            )
            type_menu.grid(row=0, column=1, padx=10, pady=10)
        else:
            type_menu = ttk.Combobox(
                control_frame,
                textvariable=self.type_var,
                values=["Binary Tree", "Binary Search Tree"],
                state="readonly",
                width=18
            )
            type_menu.grid(row=0, column=1, padx=10, pady=10)
            type_menu.bind("<<ComboboxSelected>>", lambda e: self.change_tree_type(self.type_var.get()))
        
        # Input field
        self._create_label(control_frame, "Value:", 0, 2)
        
        if self.use_ctk:
            self.input_entry = ctk.CTkEntry(control_frame, width=100, font=("Arial", 14))
        else:
            self.input_entry = tk.Entry(control_frame, width=12, font=("Arial", 12))
        self.input_entry.grid(row=0, column=3, padx=10, pady=10)
        self.input_entry.bind("<Return>", lambda e: self.insert_node())
        
        # Buttons
        button_configs = [
            ("Insert", self.insert_node, "#4CAF50", 4),
            ("Delete", self.delete_node, "#f44336", 5),
            ("Search", self.search_node, "#2196F3", 6),
            ("Bulk Insert", self.bulk_insert, "#9C27B0", 7),
            ("Clear Tree", self.clear_tree, "#d32f2f", 8)
        ]
        
        for text, command, color, col in button_configs:
            if self.use_ctk:
                btn = ctk.CTkButton(
                    control_frame,
                    text=text,
                    command=command,
                    width=100 if text != "Clear Tree" else 120,
                    font=("Arial", 12),
                    fg_color=color if text == "Clear Tree" else None,
                    hover_color="darkred" if text == "Clear Tree" else None
                )
            else:
                btn = tk.Button(
                    control_frame,
                    text=text,
                    command=command,
                    width=10 if text != "Clear Tree" else 12,
                    font=("Arial", 10),
                    bg=color,
                    fg="white",
                    relief=tk.RAISED
                )
            btn.grid(row=0, column=col, padx=5, pady=10)
    
    def _create_label(self, parent, text, row, col, font_size=14):
        """Helper to create labels"""
        if self.use_ctk:
            label = ctk.CTkLabel(parent, text=text, font=("Arial", font_size))
        else:
            label = tk.Label(parent, text=text, font=("Arial", font_size-2), bg="gray25", fg="white")
        label.grid(row=row, column=col, padx=10, pady=10)
    
    def _setup_canvas(self, canvas_frame):
        """Setup canvas with scrollbars"""
        canvas_container = tk.Frame(canvas_frame, bg=COLORS["bg_medium"])
        canvas_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas
        self.canvas = tk.Canvas(
            canvas_container,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=COLORS["bg_medium"],
            highlightthickness=0,
            scrollregion=(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        )
        
        # Create scrollbars
        if self.use_ctk:
            self.scrollbar_y = ctk.CTkScrollbar(canvas_container, orientation="vertical", command=self.canvas.yview)
            self.scrollbar_x = ctk.CTkScrollbar(canvas_container, orientation="horizontal", command=self.canvas.xview)
        else:
            self.scrollbar_y = tk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
            self.scrollbar_x = tk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # Make canvas focusable for keyboard scrolling
        self.canvas.focus_set()
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)
    
    def _setup_info_panel(self, info_frame):
        """Setup information and traversal panel"""
        if self.use_ctk:
            self.info_label = ctk.CTkLabel(
                info_frame,
                text="Tree Information: No nodes",
                font=("Arial", 12),
                anchor="w"
            )
            self.info_label.pack(side="left", padx=10, pady=10)
            
            traversal_frame = ctk.CTkFrame(info_frame)
            traversal_frame.pack(side="right", padx=10, pady=10)
        else:
            self.info_label = tk.Label(
                info_frame,
                text="Tree Information: No nodes",
                font=("Arial", 11),
                anchor="w",
                bg="gray25",
                fg="white"
            )
            self.info_label.pack(side="left", padx=10, pady=10)
            
            traversal_frame = tk.Frame(info_frame, bg="gray25")
            traversal_frame.pack(side="right", padx=10, pady=10)
        
        # Traversal buttons
        for traversal_type in ["Inorder", "Preorder", "Postorder"]:
            if self.use_ctk:
                btn = ctk.CTkButton(
                    traversal_frame,
                    text=traversal_type,
                    command=lambda t=traversal_type: self.show_traversal(t),
                    width=80,
                    font=("Arial", 10)
                )
            else:
                btn = tk.Button(
                    traversal_frame,
                    text=traversal_type,
                    command=lambda t=traversal_type: self.show_traversal(t),
                    width=10,
                    font=("Arial", 9),
                    bg="#607D8B",
                    fg="white",
                    relief=tk.RAISED
                )
            btn.pack(side="left", padx=2)
    
    def change_tree_type(self, choice: str):
        """Change between Binary Tree and BST"""
        self.tree_type = choice
        if choice == "Binary Search Tree":
            self.tree = BinarySearchTree()
        else:
            self.tree = BinaryTree()
        self.current_traversal = ""
        self.update_display()
    
    def insert_node(self):
        """Insert a node into the tree"""
        try:
            value = int(self.input_entry.get())
            if self.tree.insert(value):
                self.update_display()
                self.input_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Insert Failed", f"Could not insert {value} (may already exist in BST)")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer")
    
    def bulk_insert(self):
        """Insert multiple values separated by spaces or commas"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Bulk Insert")
        dialog.geometry("400x150")
        if self.use_ctk:
            dialog.configure(bg=COLORS["bg_dark"])
        else:
            dialog.configure(bg="gray25")
        
        label_text = "Enter values (space or comma separated):"
        if self.use_ctk:
            label = ctk.CTkLabel(dialog, text=label_text, font=("Arial", 12))
            label.pack(pady=10)
            entry = ctk.CTkEntry(dialog, width=300, font=("Arial", 12))
        else:
            label = tk.Label(dialog, text=label_text, font=("Arial", 11), bg="gray25", fg="white")
            label.pack(pady=10)
            entry = tk.Entry(dialog, width=40, font=("Arial", 11))
        entry.pack(pady=10)
        entry.focus()
        
        def do_insert():
            try:
                text = entry.get()
                # Split by comma or space
                values = [int(v.strip()) for v in text.replace(",", " ").split() if v.strip()]
                if not values:
                    messagebox.showwarning("No Values", "Please enter at least one value")
                    return
                
                inserted = 0
                for value in values:
                    if self.tree.insert(value):
                        inserted += 1
                
                dialog.destroy()
                self.update_display()
                if inserted < len(values):
                    messagebox.showinfo("Bulk Insert Complete", 
                                      f"Inserted {inserted} out of {len(values)} values")
                else:
                    messagebox.showinfo("Bulk Insert Complete", 
                                      f"Successfully inserted {inserted} values")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter only integers separated by spaces or commas")
        
        if self.use_ctk:
            btn = ctk.CTkButton(dialog, text="Insert", command=do_insert)
        else:
            btn = tk.Button(dialog, text="Insert", command=do_insert, bg="#4CAF50", fg="white")
        btn.pack(pady=10)
        entry.bind("<Return>", lambda e: do_insert())
    
    def delete_node(self):
        """Delete a node from the tree"""
        try:
            value = int(self.input_entry.get())
            if self.tree.delete(value):
                self.update_display()
                self.input_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Delete Failed", f"Value {value} not found in tree")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer")
    
    def search_node(self):
        """Search for a node in the tree"""
        try:
            value = int(self.input_entry.get())
            if self.tree.search(value):
                messagebox.showinfo("Search Result", f"Value {value} found in tree!")
                self.highlight_node(value)
            else:
                messagebox.showinfo("Search Result", f"Value {value} not found in tree")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer")
    
    def clear_tree(self):
        """Clear the entire tree"""
        if messagebox.askyesno("Clear Tree", "Are you sure you want to clear the entire tree?"):
            if self.tree_type == "Binary Search Tree":
                self.tree = BinarySearchTree()
            else:
                self.tree = BinaryTree()
            self.current_traversal = ""
            self.update_display()
    
    def highlight_node(self, value: int):
        """Highlight a specific node during search"""
        self.update_display()
        self._highlight_recursive(self.tree.root, value)
        self.root.after(HIGHLIGHT_DURATION, self.update_display)
    
    def _highlight_recursive(self, node: Optional[TreeNode], value: int):
        """Recursively find and highlight node"""
        if node is None:
            return
        if node.value == value:
            x, y = node.x, node.y
            self.canvas.create_oval(
                x - NODE_RADIUS, y - NODE_RADIUS,
                x + NODE_RADIUS, y + NODE_RADIUS,
                fill=COLORS["highlight_fill"],
                outline=COLORS["highlight_outline"],
                width=3
            )
            self.canvas.create_text(x, y, text=str(value), font=("Arial", 14, "bold"), fill=COLORS["text"])
        else:
            if self.tree_type == "Binary Search Tree":
                if value < node.value:
                    self._highlight_recursive(node.left, value)
                else:
                    self._highlight_recursive(node.right, value)
            else:
                self._highlight_recursive(node.left, value)
                self._highlight_recursive(node.right, value)
    
    def show_traversal(self, traversal_type: str):
        """Show tree traversal result"""
        if self.tree.root is None:
            messagebox.showinfo("Empty Tree", "Tree is empty")
            self.current_traversal = ""
            return
        
        if traversal_type == "Inorder":
            result = self.tree.inorder_traversal()
        elif traversal_type == "Preorder":
            result = self.tree.preorder_traversal()
        else:  # Postorder
            result = self.tree.postorder_traversal()
        
        self.current_traversal = f"{traversal_type}: " + " → ".join(map(str, result))
        self.update_display()
        messagebox.showinfo(f"{traversal_type} Traversal", " → ".join(map(str, result)))
    
    def update_display(self):
        """Update the tree visualization"""
        self.canvas.delete("all")
        
        if self.tree.root is None:
            info_text = "Tree Information: No nodes"
            if self.current_traversal:
                info_text += f" | {self.current_traversal}"
            self.info_label.configure(text=info_text)
            return
        
        # Calculate positions for all nodes
        self._calculate_positions()
        
        # Draw edges first
        self._draw_edges(self.tree.root)
        
        # Draw nodes
        self._draw_nodes(self.tree.root)
        
        # Update traversal display with all three traversals
        if hasattr(self, 'traversal_text'):
            self.traversal_text.config(state=tk.NORMAL)
            self.traversal_text.delete(1.0, tk.END)
            
            if self.tree.root is not None:
                preorder = self.tree.preorder_traversal()
                inorder = self.tree.inorder_traversal()
                postorder = self.tree.postorder_traversal()
                
                traversal_output = (
                    f"TLR (Preorder):    {' → '.join(map(str, preorder))}\n"
                    f"LTR (Inorder):     {' → '.join(map(str, inorder))}\n"
                    f"LRT (Postorder):   {' → '.join(map(str, postorder))}"
                )
                self.traversal_text.insert(tk.END, traversal_output)
            
            self.traversal_text.config(state=tk.DISABLED)
        
        # Update info label
        height = self.tree.get_height()
        node_count = self._count_nodes(self.tree.root)
        info_text = f"Tree Type: {self.tree_type} | Nodes: {node_count} | Height: {height}"
        if self.current_traversal:
            info_text += f" | {self.current_traversal}"
        self.info_label.configure(text=info_text)
        
        # Update scroll region with padding
        bbox = self.canvas.bbox("all")
        if bbox:
            scroll_left = bbox[0] - CANVAS_PADDING
            scroll_top = bbox[1] - CANVAS_PADDING
            scroll_right = max(bbox[2] + CANVAS_PADDING, CANVAS_WIDTH)
            scroll_bottom = max(bbox[3] + CANVAS_PADDING, CANVAS_HEIGHT)
            # Ensure scroll region is at least as large as canvas
            scroll_right = max(scroll_right, CANVAS_WIDTH)
            scroll_bottom = max(scroll_bottom, CANVAS_HEIGHT)
            self.canvas.configure(scrollregion=(scroll_left, scroll_top, scroll_right, scroll_bottom))
        else:
            self.canvas.configure(scrollregion=(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT))
        
        # Update scrollbars visibility
        self._update_scrollbars()
    
    def _calculate_positions(self):
        """Calculate x, y positions for all nodes using recursive algorithm with centering"""
        if self.tree.root is None:
            return
        
        def position_node(node, x, y, level):
            """Recursively position nodes"""
            if node is None:
                return
            
            node.x = x
            node.y = y
            
            if node.left is not None or node.right is not None:
                left_width = self._calculate_subtree_width(node.left, X_SPACING)
                right_width = self._calculate_subtree_width(node.right, X_SPACING)
                
                if node.left:
                    left_x = x - (right_width + X_SPACING / 2)
                    position_node(node.left, left_x, y + Y_SPACING, level + 1)
                
                if node.right:
                    right_x = x + (left_width + X_SPACING / 2)
                    position_node(node.right, right_x, y + Y_SPACING, level + 1)
        
        # First pass: calculate positions relative to root at (0, 0)
        position_node(self.tree.root, 0, 0, 0)
        
        # Find bounds
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        def find_bounds(node):
            nonlocal min_x, max_x, min_y, max_y
            if node is None:
                return
            min_x = min(min_x, node.x)
            max_x = max(max_x, node.x)
            min_y = min(min_y, node.y)
            max_y = max(max_y, node.y)
            find_bounds(node.left)
            find_bounds(node.right)
        
        find_bounds(self.tree.root)
        
        # Center the tree both horizontally and vertically
        tree_width = max_x - min_x if max_x > min_x else 0
        tree_height = max_y - min_y if max_y > min_y else 0
        
        # Get actual canvas dimensions for proper centering in fullscreen
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else CANVAS_WIDTH
        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else CANVAS_HEIGHT
        
        # Center horizontally
        center_offset_x = (canvas_width - tree_width) / 2 - min_x
        # Center vertically, moved up more for better positioning
        center_offset_y = (canvas_height - tree_height) / 3 - min_y
        
        # Second pass: adjust positions
        def adjust_positions(node):
            if node is None:
                return
            node.x += center_offset_x
            node.y += center_offset_y
            adjust_positions(node.left)
            adjust_positions(node.right)
        
        adjust_positions(self.tree.root)
    
    def _calculate_subtree_width(self, node, spacing):
        """Calculate the width needed for a subtree"""
        if node is None:
            return 0
        
        if node.left is None and node.right is None:
            return spacing / 2
        
        left_width = self._calculate_subtree_width(node.left, spacing)
        right_width = self._calculate_subtree_width(node.right, spacing)
        
        return max(left_width, right_width) * 2 + spacing
    
    def _draw_edges(self, node: Optional[TreeNode]):
        """Draw edges connecting nodes"""
        if node is None:
            return
        
        if node.left:
            self.canvas.create_line(
                node.x, node.y, node.left.x, node.left.y,
                fill=COLORS["edge"], width=2
            )
            self._draw_edges(node.left)
        
        if node.right:
            self.canvas.create_line(
                node.x, node.y, node.right.x, node.right.y,
                fill=COLORS["edge"], width=2
            )
            self._draw_edges(node.right)
    
    def _draw_nodes(self, node: Optional[TreeNode]):
        """Draw nodes with their values"""
        if node is None:
            return
        
        # Draw circle
        self.canvas.create_oval(
            node.x - NODE_RADIUS, node.y - NODE_RADIUS,
            node.x + NODE_RADIUS, node.y + NODE_RADIUS,
            fill=COLORS["node_fill"],
            outline=COLORS["node_outline"],
            width=2
        )
        
        # Draw value text
        self.canvas.create_text(
            node.x, node.y,
            text=str(node.value),
            font=("Arial", 12, "bold"),
            fill=COLORS["text"]
        )
        
        # Draw children recursively
        self._draw_nodes(node.left)
        self._draw_nodes(node.right)
    
    def _update_scrollbars(self):
        """Update scrollbar visibility based on content size"""
        bbox = self.canvas.bbox("all")
        if bbox:
            content_width = bbox[2] - bbox[0]
            content_height = bbox[3] - bbox[1]
            
            # Show/hide scrollbars based on content size
            if content_width > CANVAS_WIDTH:
                self.scrollbar_x.grid(row=1, column=0, sticky="ew")
            else:
                self.scrollbar_x.grid_remove()
            
            if content_height > CANVAS_HEIGHT:
                self.scrollbar_y.grid(row=0, column=1, sticky="ns")
            else:
                self.scrollbar_y.grid_remove()
        else:
            self.scrollbar_x.grid_remove()
            self.scrollbar_y.grid_remove()
    
    def _count_nodes(self, node: Optional[TreeNode]) -> int:
        """Count total number of nodes"""
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)


class DSAMainMenu:
    """Main menu for selecting different DSA visualizers"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DSA Visualization Suite")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS["bg_dark"])
        
        self.module_window = None
        self.setup_main_menu()
    
    def setup_main_menu(self):
        """Setup the main menu interface"""
        main_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        if USE_CTK:
            title = ctk.CTkLabel(
                main_frame,
                text="Data Structures and Algorithms",
                font=("Arial", 40, "bold"),
                text_color=COLORS["accent_primary"]
            )
        else:
            title = tk.Label(
                main_frame,
                text="Data Structures and Algorithms",
                font=("Arial", 40, "bold"),
                bg=COLORS["bg_dark"],
                fg=COLORS["accent_primary"]
            )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            main_frame,
            text="Interactive Visualization & Learning Suite",
            font=("Arial", 15, "italic"),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_secondary"]
        )
        subtitle.pack(pady=8)
        
        # Group Members Info with enhanced styling
        group_frame = tk.Frame(main_frame, bg=COLORS["bg_medium"], relief=tk.RIDGE, bd=2)
        group_frame.pack(pady=20, padx=30, fill=tk.X)
        
        group_title = tk.Label(
            group_frame,
            text="👥 Group Members",
            font=("Arial", 13, "bold"),
            bg=COLORS["bg_medium"],
            fg="#FFD700"
        )
        group_title.pack(pady=(10, 5))
        
        members_text = tk.Label(
            group_frame,
            text="""Bangcasan, Angel Grace — Recursion
Basco, Kris Rainiell — Binary Tree & Binary Search
Mercado, Lorens Aron D. — Queue and Stack
Nuyda, Karen — Recursion""",
            font=("Arial", 11),
            bg=COLORS["bg_medium"],
            fg=COLORS["text_primary"],
            justify=tk.CENTER
        )
        members_text.pack(pady=(5, 10))
        
        # Menu frame with elevated surface
        menu_frame = tk.Frame(main_frame, bg=COLORS["bg_medium"], relief=tk.FLAT, bd=0)
        menu_frame.pack(pady=20, padx=50, fill=tk.X)
        menu_frame.configure(highlightbackground=COLORS["bg_light"], highlightthickness=1)
        
        # Dropdown menu label
        tk.Label(menu_frame, text="Choose Option:", font=("Arial", 13, "bold"),
                bg=COLORS["bg_medium"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=15, pady=15)
        
        self.menu_var = tk.StringVar(value="Select an Option")
        options = [
            "Binary Tree",
            "Binary Search Tree",
            "Stack",
            "Queue",
            "Factorial Recursion",
            "Fibonacci Sequence",
            "Tower of Hanoi"
        ]
        
        if USE_CTK:
            menu = ctk.CTkOptionMenu(
                menu_frame,
                values=options,
                variable=self.menu_var,
                command=self.launch_module,
                font=("Arial", 14),
                width=300
            )
        else:
            menu = ttk.Combobox(
                menu_frame,
                textvariable=self.menu_var,
                values=options,
                state="readonly",
                font=("Arial", 12),
                width=30
            )
            menu.bind("<<ComboboxSelected>>", lambda e: self.launch_module(self.menu_var.get()))
        
        menu.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Launch button with modern styling and hover effects
        if USE_CTK:
            launch_btn = ctk.CTkButton(
                menu_frame,
                text="🚀 Launch",
                command=lambda: self.launch_module(self.menu_var.get()),
                font=("Arial", 13, "bold"),
                width=100,
                fg_color=COLORS["accent_primary"],
                hover_color="#9B66DC"
            )
        else:
            launch_btn = tk.Button(
                menu_frame,
                text="🚀 Launch",
                command=lambda: self.launch_module(self.menu_var.get()),
                font=("Arial", 12, "bold"),
                bg=COLORS["accent_primary"],
                fg=COLORS["bg_dark"],
                padx=20,
                pady=8,
                relief=tk.FLAT,
                cursor="hand2",
                activebackground="#9B66DC",
                activeforeground=COLORS["bg_dark"]
            )
        launch_btn.pack(side=tk.LEFT, padx=12, pady=15)
        
        # Info panel with elevated background and better text contrast
        info_frame = tk.Frame(main_frame, bg=COLORS["bg_medium"], relief=tk.FLAT, bd=0)
        info_frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)
        info_frame.configure(highlightbackground=COLORS["bg_light"], highlightthickness=1)
        
        if USE_CTK:
            info_title = ctk.CTkLabel(
                info_frame,
                text="📚 Available Modules",
                font=("Arial", 15, "bold"),
                text_color=COLORS["accent_primary"]
            )
        else:
            info_title = tk.Label(
                info_frame,
                text="📚 Available Modules",
                font=("Arial", 15, "bold"),
                bg=COLORS["bg_medium"],
                fg=COLORS["accent_primary"]
            )
        info_title.pack(pady=12)
        
        info_text = tk.Text(
            info_frame,
            height=14,
            width=80,
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            font=("Courier", 10),
            state=tk.DISABLED,
            insertbackground=COLORS["accent_primary"]
        )
        info_text.pack(padx=12, pady=10)

        # Add info
        info_text.config(state=tk.NORMAL)
        info_text.insert(tk.END, """
  1. STACK (LIFO - Last In First Out)
      - Push and pop operations with visual animation
      - Parking Garage LIFO simulation
      - Demonstrates real-world stack applications

  2. QUEUE (FIFO - First In First Out)
      - Enqueue and dequeue operations with visualization
      - Parking Game FIFO simulation
      - Shows sequential process management

  3. BINARY TREE
      - Insert, delete, and search nodes
      - All three traversal methods (Preorder/TLR, Inorder/LTR, Postorder/LRT)
      - Real-time tree visualization and analysis

  4. BINARY SEARCH TREE (BST)
      - Maintains BST property during insertions/deletions
      - Efficient searching and automatic balancing
      - Ordered tree traversal and analysis

  5. FACTORIAL RECURSION
      - Visualizes recursive calls with animated call stack
      - Shows recursion depth and function parameters
      - Step-by-step execution with detailed explanation

  6. FIBONACCI SEQUENCE
      - Generates and displays Fibonacci numbers dynamically
      - Visual bar chart representation of sequence
      - Animated term-by-term calculation with formula display

  7. TOWER OF HANOI
      - Classic recursive problem with disk movement animation
      - Visual representation of all three pegs
      - Move counter and solution tracking (2^n - 1 moves)
        """)
        info_text.config(state=tk.DISABLED)
    
    def launch_module(self, module_name):
        """Launch the selected DSA module"""
        if module_name == "Select an Option":
            messagebox.showwarning("Warning", "Please select a module to launch!")
            return
        
        try:
            if module_name == "Binary Tree":
                self.launch_tree_visualizer("Binary Tree")
            elif module_name == "Binary Search Tree":
                self.launch_tree_visualizer("Binary Search Tree")
            elif module_name == "Stack":
                self.launch_stack()
            elif module_name == "Queue":
                self.launch_queue()
            elif module_name == "Factorial Recursion":
                self.launch_factorial()
            elif module_name == "Fibonacci Sequence":
                self.launch_fibonacci()
            elif module_name == "Tower of Hanoi":
                self.launch_hanoi()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch: {str(e)}")

    def _import_class_from_candidates(self, dir_candidates, module_filename, class_name):
        """Import a class from the first matching directory using sys.path import.

        This approach ensures that relative imports inside the target module
        (e.g., `from .stack_logic import ...` or `from stack_logic import ...`)
        work by temporarily adding the target directory to `sys.path` before import.
        """
        base_dir = os.path.dirname(__file__)
        mod_name = module_filename[:-3]  # strip .py -> e.g., 'queue_ui'
        last_error = None
        for d in dir_candidates:
            dir_path = os.path.join(base_dir, d)
            candidate_path = os.path.join(dir_path, module_filename)
            if os.path.isfile(candidate_path):
                # Ensure directory is on sys.path for direct module import
                added = False
                if dir_path not in sys.path:
                    sys.path.insert(0, dir_path)
                    added = True
                try:
                    # Preload peer logic module to satisfy absolute imports inside the UI module
                    logic_map = {
                        'stack_ui.py': 'stack_logic.py',
                        'queue_ui.py': 'queue_logic.py'
                    }
                    logic_filename = logic_map.get(module_filename)
                    if logic_filename:
                        logic_path = os.path.join(dir_path, logic_filename)
                        if os.path.isfile(logic_path):
                            logic_modname = logic_filename[:-3]
                            if logic_modname not in sys.modules:
                                spec_logic = importlib.util.spec_from_file_location(logic_modname, logic_path)
                                mod_logic = importlib.util.module_from_spec(spec_logic)
                                spec_logic.loader.exec_module(mod_logic)
                                sys.modules[logic_modname] = mod_logic
                    module = importlib.import_module(mod_name)
                    return getattr(module, class_name)
                except Exception as e:
                    last_error = e
                finally:
                    # Keep sys.path entry to allow sub-imports later (safe for this app)
                    # If needed, we could remove it by:
                    # if added: sys.path.remove(dir_path)
                    pass
        if last_error:
            raise ImportError(f"Failed loading {class_name} from candidates {dir_candidates}: {last_error}")
        raise ImportError(f"No module file '{module_filename}' found in {dir_candidates}")
    
    def launch_tree_visualizer(self, tree_type):
        """Launch the tree visualizer"""
        if self.module_window:
            try:
                self.module_window.destroy()
            except:
                pass
        
        self.module_window = tk.Toplevel(self.root)
        self.module_window.geometry("1200x800")
        self.module_window.title(f"{tree_type} Visualizer")
        
        app = TreeVisualizer(self.module_window)
        app.tree_type = tree_type
        if tree_type == "Binary Search Tree":
            app.tree = BinarySearchTree()
        else:
            app.tree = BinaryTree()
    
    def launch_stack(self):
        """Launch stack visualizer"""
        if self.module_window:
            try:
                self.module_window.destroy()
            except:
                pass
        
        self.module_window = tk.Toplevel(self.root)
        self.module_window.geometry("680x760")
        self.module_window.title("Parking Garage - Stack")
        
        try:
            StackUI = self._import_class_from_candidates([
                'my_stack', 'stack'
            ], 'stack_ui.py', 'StackUI')
            app = StackUI(self.module_window, max_size=5)
            app.pack(fill="both", expand=True, padx=12, pady=12)
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Stack: {str(e)}")
    
    def launch_queue(self):
        """Launch queue visualizer"""
        if self.module_window:
            try:
                self.module_window.destroy()
            except:
                pass
        
        self.module_window = tk.Toplevel(self.root)
        self.module_window.geometry("1200x680")
        self.module_window.title("Parking Game - Queue")
        
        try:
            QueueUI = self._import_class_from_candidates([
                'my_queue', 'queue'
            ], 'queue_ui.py', 'QueueUI')
            app = QueueUI(self.module_window, max_size=10)
            app.pack(fill="both", expand=True, padx=12, pady=12)
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Queue: {str(e)}")
    
    def launch_factorial(self):
        """Launch factorial recursion visualizer"""
        if self.module_window:
            try:
                self.module_window.destroy()
            except:
                pass
        
        self.module_window = tk.Toplevel(self.root)
        self.module_window.geometry("1200x800")
        self.module_window.title("Factorial Recursion Visualizer")
        
        try:
            from recursion.factorial import FactorialVisualizer
            app = FactorialVisualizer(self.module_window)
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Factorial: {str(e)}")
    
    def launch_fibonacci(self):
        """Launch Fibonacci sequence visualizer"""
        if self.module_window:
            try:
                self.module_window.destroy()
            except:
                pass
        
        self.module_window = tk.Toplevel(self.root)
        self.module_window.geometry("1400x850")
        self.module_window.title("Fibonacci Sequence Visualizer")
        
        try:
            from recursion.fibonacci import FibonacciVisualizer
            app = FibonacciVisualizer(self.module_window)
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Fibonacci: {str(e)}")
    
    def launch_hanoi(self):
        """Launch Tower of Hanoi visualizer"""
        if self.module_window:
            try:
                self.module_window.destroy()
            except:
                pass
        
        self.module_window = tk.Toplevel(self.root)
        self.module_window.geometry("900x800")
        self.module_window.title("Tower of Hanoi Visualizer")
        
        try:
            from recursion.hanoi import TowerOfHanoi
            app = TowerOfHanoi(self.module_window, num_disks=5)
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Tower of Hanoi: {str(e)}")


def main():
    """Main function to run the application"""
    if USE_CTK:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    app = DSAMainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()