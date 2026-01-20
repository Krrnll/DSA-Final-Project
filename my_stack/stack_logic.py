# stack/stack_logic.py

class ParkingStack:
    """
    Pure stack logic for Parking Garage simulation.
    Handles ONLY data, not visualization.
    """

    def __init__(self, max_size=5):
        self.stack = []          # bottom -> top
        self.max_size = max_size

    def arrive(self, plate: str) -> bool:
        """
        Push a car onto the stack.
        Returns True if successful, False otherwise.
        """
        if not plate:
            return False

        if plate in self.stack:
            return False  # duplicate plate

        if len(self.stack) >= self.max_size:
            return False  # parking full

        self.stack.append(plate)
        return True

    def depart(self, plate: str) -> bool:
        """
        Remove a car from the stack.
        Cars above it are temporarily removed and restored.
        """
        if plate not in self.stack:
            return False

        temp = []

        # Remove cars above target
        while self.stack[-1] != plate:
            temp.append(self.stack.pop())

        # Remove target car
        self.stack.pop()

        # Restore temporarily removed cars
        while temp:
            self.stack.append(temp.pop())

        return True

    def get_stack(self):
        """Return a copy of the stack (bottom → top)."""
        return self.stack.copy()

    def is_full(self):
        return len(self.stack) >= self.max_size

    def is_empty(self):
        return len(self.stack) == 0
