import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple

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
        
        # Level-order insertion using queue
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            
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
        
        # Find node to delete
        queue = [(self.root, None)]
        while queue:
            node, parent = queue.pop(0)
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
        """Inorder traversal"""
        if node is None:
            node = self.root
        result = []
        if node:
            result.extend(self.inorder_traversal(node.left))
            result.append(node.value)
            result.extend(self.inorder_traversal(node.right))
        return result
    
    def preorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Preorder traversal"""
        if node is None:
            node = self.root
        result = []
        if node:
            result.append(node.value)
            result.extend(self.preorder_traversal(node.left))
            result.extend(self.preorder_traversal(node.right))
        return result
    
    def postorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Postorder traversal"""
        if node is None:
            node = self.root
        result = []
        if node:
            result.extend(self.postorder_traversal(node.left))
            result.extend(self.postorder_traversal(node.right))
            result.append(node.value)
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
            self.root.configure(bg="#1a1a1a")
        else:
            self.root.configure(bg="gray20")
        
        self.tree_type = "Binary Tree"  # or "Binary Search Tree"
        self.tree: BinaryTree = BinaryTree()
        self.canvas_width = 1000
        self.canvas_height = 600
        self.use_ctk = USE_CTK
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        if self.use_ctk:
            main_frame = ctk.CTkFrame(self.root)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            main_frame = tk.Frame(self.root, bg="gray20")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control panel
        if self.use_ctk:
            control_frame = ctk.CTkFrame(main_frame)
            control_frame.pack(fill="x", pady=(0, 10))
        else:
            control_frame = tk.Frame(main_frame, bg="gray25")
            control_frame.pack(fill="x", pady=(0, 10))
        
        # Tree type selection
        if self.use_ctk:
            type_label = ctk.CTkLabel(control_frame, text="Tree Type:", font=("Arial", 14))
            type_label.grid(row=0, column=0, padx=10, pady=10)
            
            self.type_var = tk.StringVar(value="Binary Tree")
            type_menu = ctk.CTkOptionMenu(
                control_frame,
                values=["Binary Tree", "Binary Search Tree"],
                variable=self.type_var,
                command=self.change_tree_type
            )
            type_menu.grid(row=0, column=1, padx=10, pady=10)
            
            # Input field
            input_label = ctk.CTkLabel(control_frame, text="Value:", font=("Arial", 14))
            input_label.grid(row=0, column=2, padx=10, pady=10)
            
            self.input_entry = ctk.CTkEntry(control_frame, width=100, font=("Arial", 14))
            self.input_entry.grid(row=0, column=3, padx=10, pady=10)
            self.input_entry.bind("<Return>", lambda e: self.insert_node())
            
            # Buttons
            insert_btn = ctk.CTkButton(control_frame, text="Insert", command=self.insert_node, width=100, font=("Arial", 12))
            insert_btn.grid(row=0, column=4, padx=5, pady=10)
            
            delete_btn = ctk.CTkButton(control_frame, text="Delete", command=self.delete_node, width=100, font=("Arial", 12))
            delete_btn.grid(row=0, column=5, padx=5, pady=10)
            
            search_btn = ctk.CTkButton(control_frame, text="Search", command=self.search_node, width=100, font=("Arial", 12))
            search_btn.grid(row=0, column=6, padx=5, pady=10)
            
            clear_btn = ctk.CTkButton(control_frame, text="Clear Tree", command=self.clear_tree, width=120, font=("Arial", 12), fg_color="red", hover_color="darkred")
            clear_btn.grid(row=0, column=7, padx=5, pady=10)
        else:
            type_label = tk.Label(control_frame, text="Tree Type:", font=("Arial", 12), bg="gray25", fg="white")
            type_label.grid(row=0, column=0, padx=10, pady=10)
            
            self.type_var = tk.StringVar(value="Binary Tree")
            type_menu = ttk.Combobox(control_frame, textvariable=self.type_var, values=["Binary Tree", "Binary Search Tree"], state="readonly", width=18)
            type_menu.grid(row=0, column=1, padx=10, pady=10)
            type_menu.bind("<<ComboboxSelected>>", lambda e: self.change_tree_type(self.type_var.get()))
            
            input_label = tk.Label(control_frame, text="Value:", font=("Arial", 12), bg="gray25", fg="white")
            input_label.grid(row=0, column=2, padx=10, pady=10)
            
            self.input_entry = tk.Entry(control_frame, width=12, font=("Arial", 12))
            self.input_entry.grid(row=0, column=3, padx=10, pady=10)
            self.input_entry.bind("<Return>", lambda e: self.insert_node())
            
            insert_btn = tk.Button(control_frame, text="Insert", command=self.insert_node, width=10, font=("Arial", 10), bg="#4CAF50", fg="white", relief=tk.RAISED)
            insert_btn.grid(row=0, column=4, padx=5, pady=10)
            
            delete_btn = tk.Button(control_frame, text="Delete", command=self.delete_node, width=10, font=("Arial", 10), bg="#f44336", fg="white", relief=tk.RAISED)
            delete_btn.grid(row=0, column=5, padx=5, pady=10)
            
            search_btn = tk.Button(control_frame, text="Search", command=self.search_node, width=10, font=("Arial", 10), bg="#2196F3", fg="white", relief=tk.RAISED)
            search_btn.grid(row=0, column=6, padx=5, pady=10)
            
            clear_btn = tk.Button(control_frame, text="Clear Tree", command=self.clear_tree, width=12, font=("Arial", 10), bg="#d32f2f", fg="white", relief=tk.RAISED)
            clear_btn.grid(row=0, column=7, padx=5, pady=10)
        
        # Canvas for drawing tree with scrollbars
        if self.use_ctk:
            canvas_frame = ctk.CTkFrame(main_frame)
            canvas_frame.pack(fill="both", expand=True)
        else:
            canvas_frame = tk.Frame(main_frame, bg="gray20")
            canvas_frame.pack(fill="both", expand=True)
        
        # Create a frame for canvas and scrollbars
        canvas_container = tk.Frame(canvas_frame, bg="#212121" if not self.use_ctk else None)
        canvas_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas with scrollable region
        self.canvas = tk.Canvas(
            canvas_container, 
            width=self.canvas_width, 
            height=self.canvas_height, 
            bg="#212121", 
            highlightthickness=0
        )
        
        # Scrollbars
        if self.use_ctk:
            scrollbar_y = ctk.CTkScrollbar(canvas_container, orientation="vertical", command=self.canvas.yview)
            scrollbar_x = ctk.CTkScrollbar(canvas_container, orientation="horizontal", command=self.canvas.xview)
            self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # Grid layout for canvas and scrollbars
            self.canvas.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0, column=1, sticky="ns")
            scrollbar_x.grid(row=1, column=0, sticky="ew")
            canvas_container.grid_rowconfigure(0, weight=1)
            canvas_container.grid_columnconfigure(0, weight=1)
        else:
            scrollbar_y = tk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
            scrollbar_x = tk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)
            self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # Grid layout for canvas and scrollbars
            self.canvas.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0, column=1, sticky="ns")
            scrollbar_x.grid(row=1, column=0, sticky="ew")
            canvas_container.grid_rowconfigure(0, weight=1)
            canvas_container.grid_columnconfigure(0, weight=1)
        
        # Information panel
        if self.use_ctk:
            info_frame = ctk.CTkFrame(main_frame)
            info_frame.pack(fill="x", pady=(10, 0))
            
            self.info_label = ctk.CTkLabel(info_frame, text="Tree Information: No nodes", font=("Arial", 12), anchor="w")
            self.info_label.pack(side="left", padx=10, pady=10)
            
            traversal_frame = ctk.CTkFrame(info_frame)
            traversal_frame.pack(side="right", padx=10, pady=10)
            
            inorder_btn = ctk.CTkButton(traversal_frame, text="Inorder", command=lambda: self.show_traversal("Inorder"), width=80, font=("Arial", 10))
            inorder_btn.pack(side="left", padx=2)
            
            preorder_btn = ctk.CTkButton(traversal_frame, text="Preorder", command=lambda: self.show_traversal("Preorder"), width=80, font=("Arial", 10))
            preorder_btn.pack(side="left", padx=2)
            
            postorder_btn = ctk.CTkButton(traversal_frame, text="Postorder", command=lambda: self.show_traversal("Postorder"), width=80, font=("Arial", 10))
            postorder_btn.pack(side="left", padx=2)
        else:
            info_frame = tk.Frame(main_frame, bg="gray25")
            info_frame.pack(fill="x", pady=(10, 0))
            
            self.info_label = tk.Label(info_frame, text="Tree Information: No nodes", font=("Arial", 11), anchor="w", bg="gray25", fg="white")
            self.info_label.pack(side="left", padx=10, pady=10)
            
            traversal_frame = tk.Frame(info_frame, bg="gray25")
            traversal_frame.pack(side="right", padx=10, pady=10)
            
            inorder_btn = tk.Button(traversal_frame, text="Inorder", command=lambda: self.show_traversal("Inorder"), width=10, font=("Arial", 9), bg="#607D8B", fg="white", relief=tk.RAISED)
            inorder_btn.pack(side="left", padx=2)
            
            preorder_btn = tk.Button(traversal_frame, text="Preorder", command=lambda: self.show_traversal("Preorder"), width=10, font=("Arial", 9), bg="#607D8B", fg="white", relief=tk.RAISED)
            preorder_btn.pack(side="left", padx=2)
            
            postorder_btn = tk.Button(traversal_frame, text="Postorder", command=lambda: self.show_traversal("Postorder"), width=10, font=("Arial", 9), bg="#607D8B", fg="white", relief=tk.RAISED)
            postorder_btn.pack(side="left", padx=2)
    
    def change_tree_type(self, choice: str):
        """Change between Binary Tree and BST"""
        self.tree_type = choice
        if choice == "Binary Search Tree":
            self.tree = BinarySearchTree()
        else:
            self.tree = BinaryTree()
        self.update_display()
        messagebox.showinfo("Tree Type Changed", f"Switched to {choice}")
    
    def insert_node(self):
        """Insert a node into the tree"""
        try:
            value = int(self.input_entry.get())
            if self.tree.insert(value):
                self.update_display()
                self.input_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Insert Failed", f"Could not insert {value}")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer")
    
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
            self.update_display()
    
    def highlight_node(self, value: int):
        """Highlight a specific node during search"""
        self.update_display()
        # Find and highlight the node
        self._highlight_recursive(self.tree.root, value)
        self.root.after(2000, self.update_display)  # Remove highlight after 2 seconds
    
    def _highlight_recursive(self, node: Optional[TreeNode], value: int):
        """Recursively find and highlight node"""
        if node is None:
            return
        if node.value == value:
            # Draw highlighted circle
            x, y = node.x, node.y
            radius = 25
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill="#ff6b6b", outline="#ff0000", width=3
            )
            self.canvas.create_text(x, y, text=str(value), font=("Arial", 14, "bold"), fill="white")
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
            return
        
        if traversal_type == "Inorder":
            result = self.tree.inorder_traversal()
        elif traversal_type == "Preorder":
            result = self.tree.preorder_traversal()
        else:  # Postorder
            result = self.tree.postorder_traversal()
        
        traversal_str = " → ".join(map(str, result))
        messagebox.showinfo(f"{traversal_type} Traversal", traversal_str)
    
    def update_display(self):
        """Update the tree visualization"""
        self.canvas.delete("all")
        
        if self.tree.root is None:
            self.info_label.configure(text="Tree Information: No nodes")
            return
        
        # Calculate positions for all nodes
        self._calculate_positions()
        
        # Draw edges first
        self._draw_edges(self.tree.root)
        
        # Draw nodes
        self._draw_nodes(self.tree.root)
        
        # Update info label
        height = self.tree.get_height()
        node_count = self._count_nodes(self.tree.root)
        info_text = f"Tree Type: {self.tree_type} | Nodes: {node_count} | Height: {height}"
        if self.use_ctk:
            self.info_label.configure(text=info_text)
        else:
            self.info_label.configure(text=info_text)
        
        # Update scroll region with padding
        bbox = self.canvas.bbox("all")
        if bbox:
            # Add padding around the tree
            padding = 100
            scroll_left = bbox[0] - padding
            scroll_top = bbox[1] - padding
            scroll_right = bbox[2] + padding
            scroll_bottom = bbox[3] + padding
            
            # Ensure minimum scroll region size
            scroll_right = max(scroll_right, self.canvas_width)
            scroll_bottom = max(scroll_bottom, self.canvas_height)
            
            self.canvas.configure(scrollregion=(scroll_left, scroll_top, scroll_right, scroll_bottom))
        else:
            # Default scroll region if no items
            self.canvas.configure(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
    
    def _calculate_positions(self):
        """Calculate x, y positions for all nodes using recursive algorithm with centering"""
        if self.tree.root is None:
            return
        
        # More compact spacing for a slimmer tree
        x_spacing = 60
        y_spacing = 80
        
        def position_node(node, x, y, level):
            """Recursively position nodes"""
            if node is None:
                return
            
            node.x = x
            node.y = y
            
            # Calculate positions for children
            if node.left is not None or node.right is not None:
                # Calculate subtree widths
                left_width = self._calculate_subtree_width(node.left, x_spacing)
                right_width = self._calculate_subtree_width(node.right, x_spacing)
                
                # Position left child
                if node.left:
                    left_x = x - (right_width + x_spacing / 2)
                    position_node(node.left, left_x, y + y_spacing, level + 1)
                
                # Position right child
                if node.right:
                    right_x = x + (left_width + x_spacing / 2)
                    position_node(node.right, right_x, y + y_spacing, level + 1)
        
        # First pass: calculate positions relative to root at (0, 0)
        temp_root_x = 0
        temp_root_y = 0
        position_node(self.tree.root, temp_root_x, temp_root_y, 0)
        
        # Calculate actual bounds of the tree
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
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
        
        # Calculate center offset to center the tree
        tree_width = max_x - min_x if max_x > min_x else 0
        tree_height = max_y - min_y if max_y > min_y else 0
        
        # Center the tree in the canvas
        center_offset_x = (self.canvas_width - tree_width) / 2 - min_x
        center_offset_y = 50 - min_y  # Start 50 pixels from top
        
        # Second pass: adjust all positions to center the tree
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
                fill="#64b5f6", width=2
            )
            self._draw_edges(node.left)
        
        if node.right:
            self.canvas.create_line(
                node.x, node.y, node.right.x, node.right.y,
                fill="#64b5f6", width=2
            )
            self._draw_edges(node.right)
    
    def _draw_nodes(self, node: Optional[TreeNode]):
        """Draw nodes with their values"""
        if node is None:
            return
        
        # Draw circle
        radius = 25
        self.canvas.create_oval(
            node.x - radius, node.y - radius,
            node.x + radius, node.y + radius,
            fill="#42a5f5", outline="#1976d2", width=2
        )
        
        # Draw value text
        self.canvas.create_text(
            node.x, node.y,
            text=str(node.value),
            font=("Arial", 12, "bold"),
            fill="white"
        )
        
        # Draw children recursively
        self._draw_nodes(node.left)
        self._draw_nodes(node.right)
    
    def _count_nodes(self, node: Optional[TreeNode]) -> int:
        """Count total number of nodes"""
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)


def main():
    """Main function to run the application"""
    if USE_CTK:
        root = ctk.CTk()
    else:
        root = tk.Tk()
    app = TreeVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()