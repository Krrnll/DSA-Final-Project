# queue/queue_ui.py
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import random
import queue
import threading
import time
import math

# Handle both package and direct imports
try:
    from .queue_logic import ParkingQueue
except ImportError:
    from queue_logic import ParkingQueue

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

if sys.platform == "win32":
    import winsound
    WINSOUND_AVAILABLE = True
else:
    WINSOUND_AVAILABLE = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CAR_COLORS = [
    "#EF5350", "#AB47BC", "#5C6BC0",
    "#26A69A", "#66BB6A", "#FFA726",
    "#8D6E63", "#78909C"
]

STRIPE_COLORS = ["#ffffff", "#ffd54f", "#b0bec5"]
ROOF_COLORS = ["#e8e8e8", "#dfe4ea", "#f0f0f0"]
WINDOW_TINTS = ["#6fb5ff", "#7fc2ff", "#8bd0ff"]
WHEEL_COLORS = ["#0e0e0e", "#1a1a1a", "#111"]


class QueueUI(ctk.CTkFrame):
    def __init__(self, parent, max_size=10):
        super().__init__(parent, fg_color="#1a2535")

        self.parking = ParkingQueue(max_size)
        self.max_size = max_size
        
        if PYGAME_AVAILABLE:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self.sound_enabled = PYGAME_AVAILABLE or WINSOUND_AVAILABLE
        
        # Initialize text-to-speech
        self.tts_enabled = PYTTSX3_AVAILABLE
        
        # TTS queue/worker for non-blocking, consistent announcements
        self.tts_queue = queue.Queue()
        self.last_slots_announced = None
        if self.tts_enabled:
            try:
                self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
                self.tts_thread.start()
            except:
                self.tts_enabled = False

        # Horizontal layout for queue (FIFO visualization)
        self.car_width = 140
        self.car_height = 60
        self.slot_gap = 25  # horizontal spacing between cars

        # Canvas dimensions for horizontal queue
        self.canvas_width = max_size * (self.car_width + self.slot_gap) + 200
        self.canvas_height = 400
        
        # Base positions
        self.base_y = self.canvas_height // 2 - self.car_height // 2

        self.cars = {}  # plate -> {rect, items, lights, color}
        self.slot_indicators = {}  # slot_num -> indicator_id
        self.car_animations = {}  # plate -> animation state
        
        # Theme system
        self.themes = {
            "Night Mode": {
                "bg_start": "#0a0e1a",
                "bg_end": "#1a2535",
                "lot_color": "#0f1320",
                "slot_line": "#27374f",
                "slot_text": "#8aaad1",
                "glow_arrival": "#00ff88",
                "glow_departure": "#ff4466",
                "indicator_empty": "#00ff88",
                "indicator_occupied": "#ff4466"
            },
            "City Garage": {
                "bg_start": "#1a1a2e",
                "bg_end": "#2d3142",
                "lot_color": "#16213e",
                "slot_line": "#0f4c75",
                "slot_text": "#3282b8",
                "glow_arrival": "#00d9ff",
                "glow_departure": "#ff6b35",
                "indicator_empty": "#00d9ff",
                "indicator_occupied": "#ff6b35"
            },
            "Minimal Clean": {
                "bg_start": "#f5f5f5",
                "bg_end": "#e0e0e0",
                "lot_color": "#fafafa",
                "slot_line": "#bdbdbd",
                "slot_text": "#424242",
                "glow_arrival": "#4caf50",
                "glow_departure": "#f44336",
                "indicator_empty": "#4caf50",
                "indicator_occupied": "#f44336"
            }
        }
        self.current_theme = "Night Mode"

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        ctk.CTkLabel(
            self,
            text="🚗 Parking Game Simulation (QUEUE / FIFO)",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=10)

        control = ctk.CTkFrame(self, fg_color="#1a2535")
        control.pack(pady=5)

        self.entry = ctk.CTkEntry(control, width=180, placeholder_text="Plate (max 7 chars)")
        self.entry.grid(row=0, column=0, padx=6)

        self.arrival_btn = ctk.CTkButton(
            control, text="✓ Arrival", command=self.arrive_car,
            fg_color="#00ff88", hover_color="#00dd77", text_color="#000000",
            corner_radius=8, font=("Segoe UI", 11, "bold")
        )
        self.arrival_btn.grid(row=0, column=1, padx=6)
        
        self.departure_btn = ctk.CTkButton(
            control, text="⊘ Departure", command=self.depart_car,
            fg_color="#ff4466", hover_color="#ff3355", text_color="#ffffff",
            corner_radius=8, font=("Segoe UI", 11, "bold")
        )
        self.departure_btn.grid(row=0, column=2, padx=6)
        
        # Theme selector
        self.theme_menu = ctk.CTkOptionMenu(
            control,
            values=["Night Mode", "City Garage", "Minimal Clean"],
            command=self.change_theme,
            width=140, corner_radius=8,
            button_color="#2a3a4a", button_hover_color="#3a4a5a"
        )
        self.theme_menu.set("Night Mode")
        self.theme_menu.grid(row=0, column=3, padx=6)

        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1a2535",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        self.draw_parking_layout()

        # Enhanced status bar with status card
        status_frame = ctk.CTkFrame(self, fg_color="#1a2535")
        status_frame.pack(pady=5, fill="x", padx=10)
        
        # Status card background
        status_card = ctk.CTkFrame(status_frame, fg_color="#0f1a2e", corner_radius=8)
        status_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # Left side: Cars info
        left_info = ctk.CTkFrame(status_card, fg_color="transparent")
        left_info.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        ctk.CTkLabel(left_info, text="🚗 CARS IN QUEUE", font=("Segoe UI", 10, "bold"), text_color="#00ff88").pack(anchor="w")
        self.info = ctk.CTkLabel(left_info, text=f"0 / {self.max_size}", font=("Segoe UI", 20, "bold"))
        self.info.pack(anchor="w")
        
        # Right side: Status indicator
        right_info = ctk.CTkFrame(status_card, fg_color="transparent")
        right_info.pack(side="right", fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(right_info, text="🅿 QUEUE STATUS", font=("Segoe UI", 10, "bold"), text_color="#8aaad1").pack(anchor="e")
        self.status_label = ctk.CTkLabel(right_info, text="🟢 Available", font=("Segoe UI", 16, "bold"))
        self.status_label.pack(anchor="e")

        self.log = tk.Text(
            self, height=8, bg="#0a0f1a", fg="#e0e0e0",
            state="disabled", relief="flat", font=("Consolas", 9),
            highlightthickness=1, highlightbackground="#1a2a3a"
        )
        # Configure color tags for different message types
        self.log.tag_config("arrival", foreground="#00ff88", font=("Consolas", 9, "bold"))
        self.log.tag_config("departure", foreground="#ff4466", font=("Consolas", 9, "bold"))
        self.log.tag_config("error", foreground="#ffa726", font=("Consolas", 9, "bold"))
        self.log.tag_config("info", foreground="#8aaad1", font=("Consolas", 9))
        self.log.tag_config("stats", foreground="#a78bfa", font=("Consolas", 9, "bold"))
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- Logging ----------------
    def log_event(self, msg, tag="info"):
        self.log.configure(state="normal")
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        
        self.log.insert("end", timestamp, "info")
        self.log.insert("end", f"{msg}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---------------- Arrival ----------------
    def arrive_car(self):
        plate = self.entry.get().strip()
        if not plate:
            self.log_event("✕ Please enter a plate number.", "error")
            return
        
        if len(plate) > 7:
            self.log_event("✕ Plate number must be 7 characters or less.", "error")
            return

        if not self.parking.arrive(plate):
            if self.parking.is_full():
                self.log_event(f"✕ Arrival failed: Queue is full!", "error")
                self.play_full_garage_sound()
                self.speak_async("Queue is full.")
            else:
                self.log_event(f"✕ Arrival failed: {plate} already in queue.", "error")
            return

        self.entry.delete(0, tk.END)

        color = random.choice(CAR_COLORS)
        self.create_car(plate, color)
        self.animate_to_slot(plate, steps=70, delay_ms=25)
        
        # Glow effect on arrival
        self.show_glow_effect(plate, "arrival")
        
        # Delay TTS to avoid audio contention with engine sound
        self.after(800, lambda: self.speak_async(f"Car {plate} arrived."))
        self.play_arrival_sound()

        self.log_event(f"✅ Arrival: {plate}", "arrival")
        self.update_info()

    def create_car(self, plate, color):
        # Start car off-screen to the right for entry animation
        x1 = self.canvas_width + 50
        y1 = self.base_y
        x2 = x1 + self.car_width
        y2 = y1 + self.car_height

        style = self.pick_style_variants()
        body_id, item_ids, light_ids = self.draw_car(x1, y1, x2, y2, color, plate, style)
        self.cars[plate] = {"rect": body_id, "items": item_ids, "lights": light_ids, "moving": False, "color": color}

    def pick_style_variants(self):
        return {
            "stripe_color": random.choice(STRIPE_COLORS),
            "double_stripe": random.random() < 0.35,
            "roof_color": random.choice(ROOF_COLORS),
            "window_tint": random.choice(WINDOW_TINTS),
            "wheel_color": random.choice(WHEEL_COLORS),
            "wheel_type": random.choice(["rect", "oval"]),
        }

    def draw_car(self, x1, y1, x2, y2, color, plate, style):
        """Draw a top-view car composed of multiple shapes. Returns (body_id, all_item_ids, light_ids)."""
        items = []
        lights = []

        # Drop shadow
        shadow = self.canvas.create_rectangle(x1+4, y1+4, x2+4, y2+4, fill="#0b0b0b", outline="")
        items.append(shadow)

        # Car body base rectangle
        body = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#202020", width=2)
        items.append(body)

        # Rounded end caps for a more realistic "pill" shape
        cap_r = (y2 - y1) // 2
        left_cap = self.canvas.create_oval(x1, y1, x1 + 2*cap_r, y2, fill=color, outline="#202020", width=2)
        right_cap = self.canvas.create_oval(x2 - 2*cap_r, y1, x2, y2, fill=color, outline="#202020", width=2)
        items.extend([left_cap, right_cap])

        # Bumpers
        bumper_h = max(4, int((y2 - y1) * 0.07))
        front_bumper = self.canvas.create_rectangle(x1, y1, x2, y1 + bumper_h, fill="#222", outline="")
        rear_bumper = self.canvas.create_rectangle(x1, y2 - bumper_h, x2, y2, fill="#222", outline="")
        items.extend([front_bumper, rear_bumper])

        # Roof panel (slightly inset)
        inset_x = int((x2 - x1) * 0.08)
        inset_y = int((y2 - y1) * 0.13)
        roof = self.canvas.create_rectangle(x1 + inset_x, y1 + inset_y, x2 - inset_x, y2 - inset_y, fill=style["roof_color"], outline="#2a2a2a", width=1)
        items.append(roof)

        # Windshield and rear glass
        glass_h = max(10, int((y2 - y1) * 0.2))
        windshield = self.canvas.create_rectangle(x1 + inset_x + 4, y1 + inset_y, x2 - inset_x - 4, y1 + inset_y + glass_h, fill=style["window_tint"], outline="#1b3a57", width=1)
        rear_glass = self.canvas.create_rectangle(x1 + inset_x + 4, y2 - inset_y - glass_h, x2 - inset_x - 4, y2 - inset_y, fill=style["window_tint"], outline="#1b3a57", width=1)
        items.extend([windshield, rear_glass])

        # Side mirrors
        mirror_w = 4
        mirror_h = max(8, int((y2 - y1) * 0.15))
        mirror_y = (y1 + y2) // 2 - mirror_h // 2
        left_mirror = self.canvas.create_rectangle(x1 - mirror_w, mirror_y, x1, mirror_y + mirror_h, fill="#333", outline="#111", width=1)
        right_mirror = self.canvas.create_rectangle(x2, mirror_y, x2 + mirror_w, mirror_y + mirror_h, fill="#333", outline="#111", width=1)
        items.extend([left_mirror, right_mirror])

        # Headlights (front)
        light_w = max(6, int((x2 - x1) * 0.04))
        light_h = max(6, int((y2 - y1) * 0.12))
        left_headlight = self.canvas.create_oval(x1 + 8, y1 + 8, x1 + 8 + light_w, y1 + 8 + light_h, fill="#ffeb3b", outline="#fbc02d", width=1)
        right_headlight = self.canvas.create_oval(x1 + 8, y2 - 8 - light_h, x1 + 8 + light_w, y2 - 8, fill="#ffeb3b", outline="#fbc02d", width=1)
        lights.extend([left_headlight, right_headlight])
        items.extend([left_headlight, right_headlight])

        # Taillights (rear)
        left_taillight = self.canvas.create_oval(x2 - 8 - light_w, y1 + 8, x2 - 8, y1 + 8 + light_h, fill="#c62828", outline="#b71c1c", width=1)
        right_taillight = self.canvas.create_oval(x2 - 8 - light_w, y2 - 8 - light_h, x2 - 8, y2 - 8, fill="#c62828", outline="#b71c1c", width=1)
        lights.extend([left_taillight, right_taillight])
        items.extend([left_taillight, right_taillight])

        # Racing stripes (optional)
        if style["double_stripe"]:
            stripe_w = max(2, int((x2 - x1) * 0.02))
            center_y = (y1 + y2) // 2
            stripe1 = self.canvas.create_rectangle(x1 + inset_x, center_y - stripe_w - 2, x2 - inset_x, center_y - 2, fill=style["stripe_color"], outline="")
            stripe2 = self.canvas.create_rectangle(x1 + inset_x, center_y + 2, x2 - inset_x, center_y + stripe_w + 2, fill=style["stripe_color"], outline="")
            items.extend([stripe1, stripe2])

        # Wheels
        wheel_w = max(8, int((x2 - x1) * 0.06))
        wheel_h = max(12, int((y2 - y1) * 0.2))
        wheel_offset_x = int((x2 - x1) * 0.15)
        
        if style["wheel_type"] == "oval":
            fl_wheel = self.canvas.create_oval(x1 + wheel_offset_x, y1 - wheel_h//2, x1 + wheel_offset_x + wheel_w, y1 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
            fr_wheel = self.canvas.create_oval(x1 + wheel_offset_x, y2 - wheel_h//2, x1 + wheel_offset_x + wheel_w, y2 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
            rl_wheel = self.canvas.create_oval(x2 - wheel_offset_x - wheel_w, y1 - wheel_h//2, x2 - wheel_offset_x, y1 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
            rr_wheel = self.canvas.create_oval(x2 - wheel_offset_x - wheel_w, y2 - wheel_h//2, x2 - wheel_offset_x, y2 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
        else:
            fl_wheel = self.canvas.create_rectangle(x1 + wheel_offset_x, y1 - wheel_h//2, x1 + wheel_offset_x + wheel_w, y1 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
            fr_wheel = self.canvas.create_rectangle(x1 + wheel_offset_x, y2 - wheel_h//2, x1 + wheel_offset_x + wheel_w, y2 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
            rl_wheel = self.canvas.create_rectangle(x2 - wheel_offset_x - wheel_w, y1 - wheel_h//2, x2 - wheel_offset_x, y1 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
            rr_wheel = self.canvas.create_rectangle(x2 - wheel_offset_x - wheel_w, y2 - wheel_h//2, x2 - wheel_offset_x, y2 + wheel_h//2, fill=style["wheel_color"], outline="#333", width=1)
        
        items.extend([fl_wheel, fr_wheel, rl_wheel, rr_wheel])

        # Plate text with background for visibility
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Dark background rectangle for plate text
        text_bg = self.canvas.create_rectangle(
            center_x - 35, center_y - 10,
            center_x + 35, center_y + 10,
            fill="#1a1a1a", outline="#ffeb3b", width=2
        )
        items.append(text_bg)
        
        # Plate text (larger and more visible)
        text_id = self.canvas.create_text(
            center_x, center_y, 
            text=plate, 
            fill="#ffffff", 
            font=("Arial", 11, "bold")
        )
        items.append(text_id)

        return body, items, lights

    def draw_parking_layout(self):
        """Draw horizontal parking slots for FIFO queue."""
        theme = self.themes[self.current_theme]
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw gradient background
        self.draw_gradient_bg(theme["bg_start"], theme["bg_end"])
        
        # Draw title and direction indicators
        self.canvas.create_text(
            self.canvas_width // 2, 30,
            text="← FRONT (Exit)                    REAR (Entry) →",
            fill=theme["slot_text"], font=("Segoe UI", 12, "bold")
        )
        
        # Draw parking slots horizontally
        start_x = 80
        y_center = self.canvas_height // 2
        
        for i in range(self.max_size):
            x = start_x + i * (self.car_width + self.slot_gap)
            
            # Slot background
            slot_rect = self.canvas.create_rectangle(
                x, y_center - self.car_height//2 - 10,
                x + self.car_width, y_center + self.car_height//2 + 10,
                fill=theme["lot_color"], outline=theme["slot_line"], width=2
            )
            
            # Slot number
            self.canvas.create_text(
                x + self.car_width // 2, y_center + self.car_height//2 + 25,
                text=f"#{i+1}", fill=theme["slot_text"], font=("Arial", 9, "bold")
            )
            
            # Status indicator (small circle)
            indicator = self.canvas.create_oval(
                x + self.car_width // 2 - 5, y_center - self.car_height//2 - 25,
                x + self.car_width // 2 + 5, y_center - self.car_height//2 - 15,
                fill=theme["indicator_empty"], outline=""
            )
            self.slot_indicators[i] = indicator
        
        # Draw entry/exit lanes
        entry_x = start_x + self.max_size * (self.car_width + self.slot_gap)
        exit_x = 20
        
        # Entry arrow (right side)
        self.canvas.create_line(
            entry_x - 20, y_center,
            entry_x + 30, y_center,
            arrow=tk.FIRST, fill=theme["glow_arrival"], width=3
        )
        self.canvas.create_text(
            entry_x + 5, y_center - 20,
            text="ENTRY", fill=theme["glow_arrival"], font=("Arial", 10, "bold")
        )
        
        # Exit arrow (left side)
        self.canvas.create_line(
            exit_x, y_center,
            exit_x + 40, y_center,
            arrow=tk.LAST, fill=theme["glow_departure"], width=3
        )
        self.canvas.create_text(
            exit_x + 20, y_center - 20,
            text="EXIT", fill=theme["glow_departure"], font=("Arial", 10, "bold")
        )
    
    def draw_gradient_bg(self, color1, color2):
        """Draw a gradient background."""
        # Simple vertical gradient
        steps = 20
        for i in range(steps):
            y1 = i * (self.canvas_height // steps)
            y2 = (i + 1) * (self.canvas_height // steps)
            
            # Interpolate colors
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            
            ratio = i / steps
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_rectangle(0, y1, self.canvas_width, y2, fill=color, outline="")

    def play_arrival_sound(self):
        """Play arrival sound effect."""
        if not self.sound_enabled:
            return
        
        if PYGAME_AVAILABLE:
            try:
                self.generate_and_play_pygame_sound(duration=1.0, pitch_start=150, pitch_end=350)
            except:
                pass
        elif WINSOUND_AVAILABLE:
            try:
                winsound.Beep(400, 200)
            except:
                pass

    def play_departure_sound(self):
        """Play departure sound effect."""
        if not self.sound_enabled:
            return
        
        if PYGAME_AVAILABLE:
            try:
                self.generate_and_play_pygame_sound(duration=1.2, pitch_start=300, pitch_end=180)
            except:
                pass
        elif WINSOUND_AVAILABLE:
            try:
                winsound.Beep(300, 300)
            except:
                pass
    
    def play_full_garage_sound(self):
        """Play error sound when garage is full."""
        if not self.sound_enabled:
            return
        
        if WINSOUND_AVAILABLE:
            try:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except:
                pass

    def generate_and_play_pygame_sound(self, duration=1.0, pitch_start=150, pitch_end=400, engine_rev=True):
        """Generate and play a car engine sound using pygame."""
        if not PYGAME_AVAILABLE:
            return
        
        try:
            sample_rate = 22050
            num_samples = int(duration * sample_rate)
            
            # Generate sound array
            sound_array = []
            for i in range(num_samples):
                t = i / sample_rate
                progress = i / num_samples
                
                # Pitch envelope
                if engine_rev:
                    pitch = pitch_start + (pitch_end - pitch_start) * progress
                else:
                    pitch = pitch_start
                
                # Generate sound wave with harmonics
                wave = 0
                wave += math.sin(2 * math.pi * pitch * t) * 0.5
                wave += math.sin(2 * math.pi * pitch * 2 * t) * 0.25
                wave += math.sin(2 * math.pi * pitch * 3 * t) * 0.15
                
                # Add noise
                noise = random.uniform(-0.1, 0.1)
                wave += noise
                
                # Volume envelope
                if progress < 0.1:
                    volume = progress / 0.1
                elif progress > 0.9:
                    volume = (1.0 - progress) / 0.1
                else:
                    volume = 1.0
                
                wave *= volume * 0.3
                
                # Convert to 16-bit
                sample = int(max(-1.0, min(1.0, wave)) * 32767)
                sound_array.append([sample, sample])
            
            # Create and play sound
            sound = pygame.sndarray.make_sound(sound_array)
            sound.play()
        except Exception as e:
            pass

    def speak(self, text):
        """Speak text using text-to-speech (blocking)."""
        if not self.tts_enabled:
            return
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except:
            pass

    def speak_async(self, text):
        """Speak text using text-to-speech (non-blocking via queue)."""
        if not self.tts_enabled:
            return
        
        try:
            self.tts_queue.put(text)
        except:
            pass

    def set_lights(self, car, on=True):
        """Turn car lights on or off."""
        if car not in self.cars:
            return
        
        light_ids = self.cars[car].get("lights", [])
        color = "#ffeb3b" if on else "#888888"
        for light_id in light_ids[:2]:  # headlights
            self.canvas.itemconfig(light_id, fill=color)

    def _tts_worker(self):
        """Background worker that creates fresh engine per message (thread-safe)."""
        while True:
            text = None
            try:
                text = self.tts_queue.get(timeout=0.5)
                if text is None:
                    self.tts_queue.task_done()
                    break
                
                # Create fresh engine for each message to avoid threading issues
                engine = pyttsx3.init()
                engine.setProperty('rate', 175)
                engine.setProperty('volume', 0.9)
                # Set voice to female
                voices = engine.getProperty('voices')
                if len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)  # Select female voice (index 1)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                del engine
                
            except queue.Empty:
                continue
            except Exception as e:
                pass
            finally:
                if text is not None:
                    try:
                        self.tts_queue.task_done()
                    except Exception:
                        pass

    # ---------------- Departure ----------------
    def depart_car(self):
        plate = self.entry.get().strip()
        if not plate:
            self.log_event("✕ Please enter a plate number.", "error")
            return
        
        if len(plate) > 7:
            self.log_event("✕ Plate number must be 7 characters or less.", "error")
            return
        
        # Check if car exists BEFORE attempting departure
        current_queue = self.parking.get_queue()
        if plate not in current_queue:
            self.log_event(f"✕ Departure failed: {plate} not found in queue.", "error")
            return
        
        # Get the position and blocking cars info BEFORE depart modifies the queue
        plate_index = current_queue.index(plate)
        temp_departed_list = current_queue[:plate_index]  # All cars before this one (will block)
        
        # Get stats BEFORE departure
        pre_stats = self.parking.get_stats(plate).copy()
        temp_stats_before = {car: self.parking.get_stats(car).copy() for car in temp_departed_list}
        
        # Now perform the actual departure in logic (this modifies the queue)
        result = self.parking.depart(plate)
        
        if not result["success"]:
            self.log_event(f"✕ Departure failed: {plate} not found in queue.", "error")
            return
        
        self.entry.delete(0, tk.END)
        
        # Log temporary departures
        if temp_departed_list:
            self.log_event(f"⚠ {len(temp_departed_list)} car(s) blocking {plate}. They will step aside temporarily...", "info")
            for temp_plate in temp_departed_list:
                self.log_event(f"  → {temp_plate} will step aside", "info")
        
        # Animate the departure with the blocking cars list
        self.animate_departure(plate, temp_departed_list)
        
        # Show statistics summary (will display after animation completes)
        self.after(100, lambda: self._show_departure_stats(plate, result["stats"], temp_departed_list))
        
        self.speak_async(f"Car {plate} departed.")
        self.play_departure_sound()
    
    def _show_departure_stats(self, plate, stats, temp_departed_list):
        """Show departure statistics after animation starts."""
        self.log_event(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "stats")
        self.log_event(f"📊 DEPARTURE SUMMARY FOR {plate}:", "stats")
        self.log_event(f"   Total Arrivals: {stats['arrivals']}", "stats")
        self.log_event(f"   Total Departures: {stats['departures']}", "stats")
        self.log_event(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "stats")
        
        # Show stats for temporarily moved cars
        if temp_departed_list:
            self.log_event(f"📊 Stats for temporarily moved cars:", "info")
            for temp_plate in temp_departed_list:
                temp_stats = self.parking.get_stats(temp_plate)
                self.log_event(f"   {temp_plate}: Arrivals: {temp_stats['arrivals']}, Departures: {temp_stats['departures']}", "info")

    def animate_departure(self, plate, temp_departed):
        """Animate departure of target car and temporary movement of blocking cars."""
        if not temp_departed:
            # No blocking cars, just depart directly
            self._depart_single_car(plate, on_complete=lambda: self._finish_single_departure(plate))
        else:
            # Start departing blocking cars one by one through the exit
            self._depart_blocking_cars(temp_departed, 0, plate)
    
    def _depart_blocking_cars(self, temp_departed, index, target_plate):
        """Depart blocking cars one by one through the exit."""
        if index >= len(temp_departed):
            # All blocking cars departed, now depart the target car
            # Set restack_after=True so remaining cars move forward to fill the gap
            self._depart_single_car(target_plate, 
                                   on_complete=lambda: self._return_blocking_cars(temp_departed, 0, target_plate),
                                   restack_after=True)
            return
        
        blocking_plate = temp_departed[index]
        if blocking_plate in self.cars:
            self.log_event(f"  ← {blocking_plate} departing (temporarily)...", "info")
            self.show_glow_effect(blocking_plate, "departure")
            # Move to exit (left side)
            self.animate_move(blocking_plate, -self.car_width - 100, self.base_y, 
                            steps=65, delay_ms=25,
                            on_complete=lambda: self._after_blocking_depart(temp_departed, index, target_plate, blocking_plate))
        else:
            # Skip if car not found
            self._depart_blocking_cars(temp_departed, index + 1, target_plate)
    
    def _after_blocking_depart(self, temp_departed, index, target_plate, blocking_plate):
        """After a blocking car departs, remove its visuals and continue."""
        # Remove the visual representation of the blocking car
        self.remove_car_visuals(blocking_plate)
        # Continue with next blocking car after a short delay
        self.after(400, lambda: self._depart_blocking_cars(temp_departed, index + 1, target_plate))
    
    def _depart_single_car(self, plate, on_complete=None, restack_after=False):
        """Depart a single car through the exit."""
        if plate in self.cars:
            self.show_glow_effect(plate, "departure")
            # Move to exit (left side)
            self.animate_move(plate, -self.car_width - 100, self.base_y, 
                            steps=70, delay_ms=25,
                            on_complete=lambda: self._remove_and_callback(plate, on_complete, restack_after))
    
    def _remove_and_callback(self, plate, callback, restack_after=False):
        """Remove car visuals and execute callback."""
        self.remove_car_visuals(plate)
        if restack_after:
            # Restack remaining visible cars to fill the gap
            self.after(300, lambda: self.restack(animate=True))
            # Then execute callback after restack animation
            self.after(1200, callback if callback else lambda: None)
        elif callback:
            callback()
    
    def _finish_single_departure(self, plate):
        """Finish a simple departure with no blocking cars."""
        self.log_event(f"✅ Departure: {plate}", "departure")
        self.restack()
        self.update_info()
    
    def _return_blocking_cars(self, temp_departed, index, target_plate):
        """Return blocking cars one by one to their original positions at the front."""
        if index >= len(temp_departed):
            # All cars returned
            self.log_event(f"✅ Departure: {target_plate}", "departure")
            self.log_event(f"✅ {len(temp_departed)} car(s) returned to front positions.", "info")
            self.update_info()
            return
        
        blocking_plate = temp_departed[index]
        
        # Get the color (use a random color if we don't have it stored)
        color = random.choice(CAR_COLORS)
        
        # Create the car at the entry point (coming back from the side/exit area)
        # They'll enter from the left side where they exited
        x1 = -self.car_width - 50
        y1 = self.base_y
        x2 = x1 + self.car_width
        y2 = y1 + self.car_height

        style = self.pick_style_variants()
        body_id, item_ids, light_ids = self.draw_car(x1, y1, x2, y2, color, blocking_plate, style)
        self.cars[blocking_plate] = {"rect": body_id, "items": item_ids, "lights": light_ids, "moving": False, "color": color}
        
        self.log_event(f"  → {blocking_plate} returning to position {index + 1}...", "info")
        self.show_glow_effect(blocking_plate, "arrival")
        
        # Animate to its original position at the front (index position in queue)
        self.animate_to_slot(blocking_plate, 
                           on_complete=lambda: self._continue_return(temp_departed, index, target_plate),
                           steps=70, delay_ms=25)
    
    def _continue_return(self, temp_departed, index, target_plate):
        """Continue returning the next blocking car."""
        self.after(400, lambda: self._return_blocking_cars(temp_departed, index + 1, target_plate))
    
    def create_car_at_entry(self, plate, color):
        """Create a car at the entry point (right side)."""
        x1 = self.canvas_width + 50
        y1 = self.base_y
        x2 = x1 + self.car_width
        y2 = y1 + self.car_height

        style = self.pick_style_variants()
        body_id, item_ids, light_ids = self.draw_car(x1, y1, x2, y2, color, plate, style)
        self.cars[plate] = {"rect": body_id, "items": item_ids, "lights": light_ids, "moving": False, "color": color}

    # ---------------- Positioning ----------------
    def animate_to_slot(self, plate, on_complete=None, steps=70, delay_ms=25):
        """Animate car to its correct slot position in the queue."""
        if plate not in self.cars:
            return
        
        queue = self.parking.get_queue()
        try:
            index = queue.index(plate)
        except ValueError:
            return
        
        # Calculate target position (left to right, front to rear)
        start_x = 80
        target_x = start_x + index * (self.car_width + self.slot_gap)
        target_y = self.base_y
        
        self.animate_move(plate, target_x, target_y, steps=steps, delay_ms=delay_ms, on_complete=on_complete)

    def restack(self, animate=True):
        """Reposition all cars to their correct queue positions."""
        queue = self.parking.get_queue()
        for plate in queue:
            if plate in self.cars:
                if animate:
                    self.animate_to_slot(plate)
                else:
                    # Instant positioning without animation
                    index = queue.index(plate)
                    start_x = 80
                    target_x = start_x + index * (self.car_width + self.slot_gap)
                    target_y = self.base_y
                    
                    # Get current position
                    rect_id = self.cars[plate]["rect"]
                    coords = self.canvas.coords(rect_id)
                    dx = target_x - coords[0]
                    dy = target_y - coords[1]
                    
                    # Move all items instantly
                    for item_id in self.cars[plate]["items"]:
                        try:
                            self.canvas.move(item_id, dx, dy)
                        except:
                            pass
        self.update_slot_indicators()

    def update_info(self):
        """Update status information display."""
        count = len(self.parking.get_queue())
        self.info.configure(text=f"{count} / {self.max_size}")
        
        if self.parking.is_full():
            self.status_label.configure(text="🔴 Queue Full", text_color="#ff4466")
        elif count == 0:
            self.status_label.configure(text="⚪ Empty", text_color="#8aaad1")
        else:
            self.status_label.configure(text="🟢 Available", text_color="#00ff88")
        
        self.update_slot_indicators()
        
        # Announce slot status changes
        if self.tts_enabled and count != self.last_slots_announced:
            if self.parking.is_full():
                self.speak_async("Queue is now full.")
            elif count == 0 and self.last_slots_announced != 0:
                self.speak_async("Queue is now empty.")
            self.last_slots_announced = count

    def animate_move(self, plate, target_x, target_y, steps=70, delay_ms=25, on_complete=None):
        """Smoothly animate a car to a target position."""
        if plate not in self.cars:
            if on_complete:
                on_complete()
            return
        
        car_data = self.cars[plate]
        if car_data.get("moving", False):
            return
        
        car_data["moving"] = True
        
        # Get current position
        rect_id = car_data["rect"]
        coords = self.canvas.coords(rect_id)
        start_x, start_y = coords[0], coords[1]
        
        dx = (target_x - start_x) / steps
        dy = (target_y - start_y) / steps
        
        def step(i):
            if plate not in self.cars or i >= steps:
                if plate in self.cars:
                    self.cars[plate]["moving"] = False
                if on_complete:
                    on_complete()
                return
            
            # Move all items
            for item_id in car_data["items"]:
                try:
                    self.canvas.move(item_id, dx, dy)
                except:
                    pass
            
            self.after(delay_ms, lambda: step(i + 1))
        
        step(0)
    
    def show_glow_effect(self, plate, effect_type="arrival"):
        """Show a glow effect around a car."""
        if plate not in self.cars:
            return
        
        theme = self.themes[self.current_theme]
        color = theme["glow_arrival"] if effect_type == "arrival" else theme["glow_departure"]
        
        rect_id = self.cars[plate]["rect"]
        coords = self.canvas.coords(rect_id)
        
        # Create glow circles
        glow_items = []
        for i in range(3):
            glow = self.canvas.create_oval(
                coords[0] - 10 - i*5, coords[1] - 10 - i*5,
                coords[2] + 10 + i*5, coords[3] + 10 + i*5,
                outline=color, width=2
            )
            glow_items.append(glow)
        
        # Fade out glow
        def fade(step=0):
            if step > 10:
                for glow in glow_items:
                    try:
                        self.canvas.delete(glow)
                    except:
                        pass
                return
            
            self.after(50, lambda: fade(step + 1))
        
        fade()
    
    def remove_car_visuals(self, plate):
        """Remove all visual elements of a car."""
        if plate not in self.cars:
            return
        
        car_data = self.cars[plate]
        for item_id in car_data["items"]:
            try:
                self.canvas.delete(item_id)
            except:
                pass
        
        del self.cars[plate]
    
    def update_slot_indicators(self):
        """Update the status indicators for each parking slot."""
        theme = self.themes[self.current_theme]
        queue = self.parking.get_queue()
        
        for i in range(self.max_size):
            indicator = self.slot_indicators.get(i)
            if indicator:
                if i < len(queue):
                    color = theme["indicator_occupied"]
                else:
                    color = theme["indicator_empty"]
                self.canvas.itemconfig(indicator, fill=color)
    
    def change_theme(self, theme_name):
        """Change the visual theme of the parking lot."""
        self.current_theme = theme_name
        
        # Store current car data before redrawing
        cars_backup = {}
        for plate, car_data in self.cars.items():
            rect_id = car_data["rect"]
            coords = self.canvas.coords(rect_id)
            if coords:
                cars_backup[plate] = {
                    "x": coords[0],
                    "y": coords[1],
                    "color": car_data["color"]
                }
        
        # Redraw layout (this clears canvas)
        self.draw_parking_layout()
        
        # Recreate all cars at their previous positions
        for plate, backup in cars_backup.items():
            x1 = backup["x"]
            y1 = backup["y"]
            x2 = x1 + self.car_width
            y2 = y1 + self.car_height
            
            style = self.pick_style_variants()
            body_id, item_ids, light_ids = self.draw_car(x1, y1, x2, y2, backup["color"], plate, style)
            self.cars[plate] = {"rect": body_id, "items": item_ids, "lights": light_ids, "moving": False, "color": backup["color"]}
        
        self.update_slot_indicators()
    
    def get_car_x(self, plate):
        """Get the current x position of a car."""
        if plate not in self.cars:
            return 0
        rect_id = self.cars[plate]["rect"]
        coords = self.canvas.coords(rect_id)
        return coords[0]


# ---------------- Entrypoint ----------------
def main():
    """Launch a window with the parking queue UI."""
    root = ctk.CTk()
    root.title("Parking Game - Queue")
    root.geometry("1200x680")

    app = QueueUI(root, max_size=10)
    app.pack(fill="both", expand=True, padx=12, pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()
