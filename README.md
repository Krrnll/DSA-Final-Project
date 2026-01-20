# Data Structures and Algorithms — Visualization Suite

An interactive desktop app that visualizes core Data Structures and Algorithms (DSA) with a modern dark theme. Built in Python with Tkinter/CustomTkinter, it includes animated simulations, real‑time traversal output, and clean UI/UX focused on learning.

## Highlights
- Visual, interactive simulations for Stack, Queue, Binary Tree, Binary Search Tree, and Recursion (Factorial, Fibonacci, Tower of Hanoi)
- Real-time traversal panel for trees (Preorder/TLR, Inorder/LTR, Postorder/LRT)
- Modern dark theme with accessible contrast and accent color
- Single unified launcher with dropdown menu

## Tech Stack
- Python 3.x
- Tkinter (built-in) + CustomTkinter (optional, recommended for enhanced visuals)

If CustomTkinter isn’t installed, the app gracefully falls back to standard Tkinter.

## UI Theme
- Main background: `#121212`
- Card/Surface: `#1E1E1E` / `#2A2A2A`
- Primary text: `#E0E0E0`
- Accent (Primary actions): `#BB86FC`

## Project Structure
```
DSA-Final-Project/
├── dsa_project.py                # Main launcher
├── binary/
│   ├── __init__.py
│   ├── binary_search.py
│   └── binary_tree.py
├── my_stack/
│   ├── __init__.py
│   ├── stack_logic.py
│   └── stack_ui.py
├── my_queue/
│   ├── __init__.py
│   ├── queue_logic.py
│   └── queue_ui.py
├── recursion/
│   ├── factorial.py
│   ├── fibonacci.py
│   └── hanoi.py
└── README.md
```

> Note: Stack/Queue folders use `my_stack` and `my_queue` to avoid conflicts with Python’s standard library module names.

## Setup
Install Python 3.x. Optionally create a virtual environment, then install CustomTkinter for the best look and feel.

```powershell
# From project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Optional but recommended
pip install customtkinter
```

The app will still run without CustomTkinter (it falls back to Tkinter).

## Run
Launch the main menu (recommended):

```powershell
python dsa_project.py
```

Alternatively, run individual visualizers:

```powershell
# Recursion demos
python .\recursion\factorial.py
python .\recursion\fibonacci.py
python .\recursion\hanoi.py
```

## Using the App
1. Open the app and use the dropdown to choose a module.
2. Click Launch.
3. Each module opens in its own window with controls.

### Modules
- 1. Stack (LIFO)
	- Push/Pop with animated visualization
	- Parking Garage simulation for real-world intuition
- 2. Queue (FIFO)
	- Enqueue/Dequeue with animated flow
	- Parking Game simulation for sequential processing
- 3. Binary Tree
	- Insert, Delete, Search
	- Real-time tree layout with automatic spacing
	- Traversal panel shows Preorder (TLR), Inorder (LTR), Postorder (LRT)
- 4. Binary Search Tree (BST)
	- Maintains BST property on insert/delete
	- Efficient search and ordered traversals
- 5. Factorial (Recursion)
	- Animated call stack, recursion depth, step-by-step explanation
- 6. Fibonacci (Recursion)
	- Bar chart sequence, animated term-by-term calculation
	- Guards against excessive input
- 7. Tower of Hanoi (Recursion)
	- Disk movement animation with move counter (uses 2^n − 1)

## Tips & Troubleshooting
- Module Imports: Local folders are named `my_stack` and `my_queue` to avoid shadowing Python’s `stack`/`queue` modules.
- __pycache__: If you move or rename folders, clear `__pycache__` to prevent stale imports.
- Traversals: Tree traversals are implemented iteratively to avoid recursion depth errors and perform reliably for larger trees.
- CustomTkinter Missing: If you see a message about CustomTkinter not found, install it via `pip install customtkinter` or continue with standard Tkinter.

## Contributors
- Bangcasan, Angel Grace — Recursion
- Basco, Kris Rainiell — Binary Tree & Binary Search
- Mercado, Lorens Aron D. — Queue and Stack
- Nuyda, Karen — Recursion

## License
Academic/educational use.

