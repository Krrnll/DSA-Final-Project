# queue/queue_logic.py

class ParkingQueue:
    """
    Pure queue logic for Parking Game simulation.
    Handles ONLY data, not visualization.
    Follows FIFO (First In First Out) principle.
    """

    def __init__(self, max_size=10):
        self.queue = []          # front -> rear
        self.max_size = max_size
        self.car_stats = {}      # plate -> {"arrivals": count, "departures": count}

    def arrive(self, plate: str) -> bool:
        """
        Add a car to the rear of the queue.
        Returns True if successful, False otherwise.
        """
        if not plate:
            return False

        if plate in self.queue:
            return False  # duplicate plate in queue

        if len(self.queue) >= self.max_size:
            return False  # parking full

        self.queue.append(plate)
        
        # Initialize or increment arrival count
        if plate not in self.car_stats:
            self.car_stats[plate] = {"arrivals": 1, "departures": 0}
        else:
            self.car_stats[plate]["arrivals"] += 1
        
        return True

    def depart(self, plate: str) -> dict:
        """
        Remove a car from the queue following FIFO rules.
        If the car is blocked, all cars in front must step aside temporarily, then return to their positions.
        
        Returns a dict with:
        - "success": bool
        - "temp_departed": list of plates that temporarily stepped aside
        - "stats": dict of car statistics for the departed car
        """
        if plate not in self.queue:
            return {"success": False, "temp_departed": [], "stats": None}

        temp_departed = []
        target_index = self.queue.index(plate)

        # Remove all cars in front of the target car (they step aside)
        for i in range(target_index):
            front_car = self.queue.pop(0)
            temp_departed.append(front_car)
            # Increment departure count for temporarily moved cars
            self.car_stats[front_car]["departures"] += 1

        # Remove the target car (it's now at position 0)
        self.queue.pop(0)
        self.car_stats[plate]["departures"] += 1
        
        # Get stats before returning cars
        departed_stats = self.car_stats[plate].copy()

        # Return temporarily departed cars to their ORIGINAL positions at the front
        for car in temp_departed:
            self.queue.insert(0, car)
            # Increment arrival count for returned cars
            self.car_stats[car]["arrivals"] += 1
        
        # Reverse to maintain original order
        self.queue[:len(temp_departed)] = reversed(self.queue[:len(temp_departed)])

        return {
            "success": True,
            "temp_departed": temp_departed,
            "stats": departed_stats
        }

    def get_queue(self):
        """Return a copy of the queue (front → rear)."""
        return self.queue.copy()

    def get_stats(self, plate: str):
        """Get arrival/departure statistics for a specific car."""
        return self.car_stats.get(plate, {"arrivals": 0, "departures": 0})

    def get_all_stats(self):
        """Get statistics for all cars."""
        return self.car_stats.copy()

    def is_full(self):
        return len(self.queue) >= self.max_size

    def is_empty(self):
        return len(self.queue) == 0
    
    def is_at_front(self, plate: str):
        """Check if a car is at the front of the queue."""
        return len(self.queue) > 0 and self.queue[0] == plate
