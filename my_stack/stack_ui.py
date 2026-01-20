# stack/stack_ui.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import tkinter as tk
import random
from datetime import datetime
import customtkinter as ctk
import numpy as np
import sys
import threading
import queue
import time

# Handle both package and direct imports
try:
    from .stack_logic import ParkingStack
except ImportError:
    from stack_logic import ParkingStack

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


class StackUI(ctk.CTkFrame):
    def __init__(self, parent, max_size=5):
        super().__init__(parent, fg_color="#1a2535")

        self.parking = ParkingStack(max_size)
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
            except Exception as e:
                print(f"TTS worker error: {e}")
                self.tts_enabled = False

        # More realistic proportions for car top view
        self.car_width = 200
        self.car_height = 80
        # Increase vertical spacing between slots for visual clarity
        self.slot_gap = 20

        # Extra headroom so side moves aren't clipped and vertical motion is visible
        self.canvas_width = 900
        self.canvas_height = max_size * (self.car_height + self.slot_gap) + 160
        
        # Calculate centered base_x position for parking lot
        total_width = (self.car_width + 40) * 2 + 40  # two lots + spacing
        start_x = (self.canvas_width - total_width) // 2
        self.base_x = start_x + 20  # anchor x-position for all cars (centered in slot)

        self.cars = {}  # plate -> {rect, text, color}
        self.slot_indicators = {}  # slot_num -> indicator_id
        self.car_animations = {}  # plate -> animation state
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
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
            text="🚗 Parking Garage Simulation (STACK / LIFO)",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=10)

        control = ctk.CTkFrame(self, fg_color="#1a2535")
        control.pack(pady=5)

        self.entry = ctk.CTkEntry(control, width=180, placeholder_text="Enter plate number")
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
        
        ctk.CTkLabel(left_info, text="🚗 CARS PARKED", font=("Segoe UI", 10, "bold"), text_color="#00ff88").pack(anchor="w")
        self.info = ctk.CTkLabel(left_info, text="0 / 5", font=("Segoe UI", 20, "bold"))
        self.info.pack(anchor="w")
        
        # Right side: Status indicator
        right_info = ctk.CTkFrame(status_card, fg_color="transparent")
        right_info.pack(side="right", fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(right_info, text="🅿 GARAGE STATUS", font=("Segoe UI", 10, "bold"), text_color="#8aaad1").pack(anchor="e")
        self.status_label = ctk.CTkLabel(right_info, text="🟢 Available", font=("Segoe UI", 16, "bold"))
        self.status_label.pack(anchor="e")

        self.log = tk.Text(
            self, height=6, bg="#0a0f1a", fg="#e0e0e0",
            state="disabled", relief="flat", font=("Consolas", 9),
            highlightthickness=1, highlightbackground="#1a2a3a"
        )
        # Configure color tags for different message types
        self.log.tag_config("arrival", foreground="#00ff88", font=("Consolas", 9, "bold"))
        self.log.tag_config("departure", foreground="#ff4466", font=("Consolas", 9, "bold"))
        self.log.tag_config("error", foreground="#ffa726", font=("Consolas", 9, "bold"))
        self.log.tag_config("info", foreground="#8aaad1", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- Logging ----------------
    def log_event(self, msg):
        self.log.configure(state="normal")
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        
        # Determine message type and apply appropriate tag
        tag = "info"
        if "Arrival" in msg or "arrived" in msg:
            tag = "arrival"
        elif "Departure" in msg or "departed" in msg:
            tag = "departure"
        elif "failed" in msg or "✕" in msg:
            tag = "error"
        
        self.log.insert("end", timestamp, "info")
        self.log.insert("end", f"{msg}\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---------------- Arrival ----------------
    def arrive_car(self):
        plate = self.entry.get().strip()
        if not plate:
            self.log_event("⚠️ Arrival failed: no plate entered")
            return

        if not self.parking.arrive(plate):
            self.log_event(f"❌ Arrival failed: duplicate or full ({plate})")
            if len(self.parking.get_stack()) >= self.max_size:
                self.play_full_garage_sound()
            return

        self.entry.delete(0, tk.END)

        color = random.choice(CAR_COLORS)
        self.create_car(plate, color)
        self.animate_to_slot(plate)
        
        # Glow effect on arrival
        self.show_glow_effect(plate, "arrival")
        
        # Delay TTS to avoid audio contention with engine sound
        self.after(800, lambda: self.speak_async(f"Car {plate} arrived."))
        self.play_arrival_sound()

        self.log_event(f"✅ Arrival: {plate}")
        self.update_info()
    
    def animate_button_press(self, button):
        """Quick scale animation on button press."""
        try:
            original_width = button._current_width
            button.configure(width=int(original_width * 0.95))
            self.after(50, lambda: button.configure(width=int(original_width)))
        except:
            pass
    
    def animate_car_arrival(self, plate):
        """Fade in car and move to slot with smooth animation."""
        if plate not in self.cars:
            return
        
        # Animate to slot
        stack = self.parking.get_stack()
        index = stack.index(plate)
        target_y = self.canvas_height - (index + 1) * (self.car_height + self.slot_gap)
        self.animate_to_slot(plate)
    
    def apply_camera_shake(self, intensity=2, duration=200):
        """Apply subtle screen shake effect on engine rev."""
        # Simple version: just pass (full implementation would require complex canvas manipulation)
        pass

    def create_car(self, plate, color):
        # Start car off-screen to the left for entry animation
        x1 = -self.car_width - 50
        y1 = -self.car_height  # start off-screen top
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

        # Drop shadow (behind the car)
        shadow = self.canvas.create_rectangle(x1+6, y1+6, x2+6, y2+6, fill="#0b0b0b", outline="")
        items.append(shadow)

        # Car body base rectangle (used as the main anchor for movement)
        body = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#202020", width=2)
        items.append(body)

        # Rounded end caps for a more realistic "pill" shape
        cap_r = (y2 - y1) // 2
        left_cap = self.canvas.create_oval(x1, y1, x1 + 2*cap_r, y2, fill=color, outline="#202020", width=2)
        right_cap = self.canvas.create_oval(x2 - 2*cap_r, y1, x2, y2, fill=color, outline="#202020", width=2)
        items.extend([left_cap, right_cap])

        # Bumpers
        bumper_h = max(6, int((y2 - y1) * 0.07))
        front_bumper = self.canvas.create_rectangle(x1, y1, x2, y1 + bumper_h, fill="#222", outline="")
        rear_bumper = self.canvas.create_rectangle(x1, y2 - bumper_h, x2, y2, fill="#222", outline="")
        items.extend([front_bumper, rear_bumper])

        # Roof panel (slightly inset)
        inset_x = int((x2 - x1) * 0.08)
        inset_y = int((y2 - y1) * 0.13)
        roof = self.canvas.create_rectangle(x1 + inset_x, y1 + inset_y, x2 - inset_x, y2 - inset_y, fill=style["roof_color"], outline="#2a2a2a", width=1)
        items.append(roof)

        # Windshield and rear glass
        glass_h = max(12, int((y2 - y1) * 0.2))
        windshield = self.canvas.create_rectangle(x1 + inset_x + 6, y1 + inset_y, x2 - inset_x - 6, y1 + inset_y + glass_h, fill=style["window_tint"], outline="#1b3a57", width=1)
        rear_glass = self.canvas.create_rectangle(x1 + inset_x + 6, y2 - inset_y - glass_h, x2 - inset_x - 6, y2 - inset_y, fill=style["window_tint"], outline="#1b3a57", width=1)
        items.extend([windshield, rear_glass])

        # Side windows
        side_win_w = int((x2 - x1) * 0.22)
        left_win = self.canvas.create_rectangle(x1 + inset_x, y1 + inset_y + glass_h + 2, x1 + inset_x + side_win_w, y2 - inset_y - glass_h - 2, fill="#7fc2ff", outline="")
        right_win = self.canvas.create_rectangle(x2 - inset_x - side_win_w, y1 + inset_y + glass_h + 2, x2 - inset_x, y2 - inset_y - glass_h - 2, fill="#7fc2ff", outline="")
        items.extend([left_win, right_win])

        # Stripes
        stripe_w = 7
        mid_x = (x1 + x2) // 2
        stripe = self.canvas.create_rectangle(mid_x - stripe_w//2, y1 + bumper_h + 4, mid_x + stripe_w//2, y2 - bumper_h - 4, fill=style["stripe_color"], outline="")
        items.append(stripe)
        if style["double_stripe"]:
            offset = 10
            stripe2 = self.canvas.create_rectangle(mid_x - stripe_w//2, y1 + bumper_h + 4 + offset, mid_x + stripe_w//2, y2 - bumper_h - 4 + offset, fill=style["stripe_color"], outline="")
            items.append(stripe2)

        # Headlights and taillights (dim by default)
        light_w = 10
        light_h = 6
        hl1 = self.canvas.create_oval(x1 + 10, y1 + 2, x1 + 10 + light_w, y1 + 2 + light_h, fill="#6b6b2f", outline="")
        hl2 = self.canvas.create_oval(x2 - 10 - light_w, y1 + 2, x2 - 10, y1 + 2 + light_h, fill="#6b6b2f", outline="")
        tl1 = self.canvas.create_oval(x1 + 10, y2 - 2 - light_h, x1 + 10 + light_w, y2 - 2, fill="#6b3333", outline="")
        tl2 = self.canvas.create_oval(x2 - 10 - light_w, y2 - 2 - light_h, x2 - 10, y2 - 2, fill="#6b3333", outline="")
        items.extend([hl1, hl2, tl1, tl2])
        lights.extend([hl1, hl2, tl1, tl2])

        # Wheels (dark rectangles along sides)
        wheel_w = 12
        wheel_h = int((y2 - y1) * 0.22)
        wy_top = y1 + int((y2 - y1) * 0.15)
        wy_bot = y2 - int((y2 - y1) * 0.15) - wheel_h
        wc = style["wheel_color"]
        if style["wheel_type"] == "rect":
            wl1 = self.canvas.create_rectangle(x1 - 2, wy_top, x1 + wheel_w, wy_top + wheel_h, fill=wc, outline="#000")
            wl2 = self.canvas.create_rectangle(x1 - 2, wy_bot, x1 + wheel_w, wy_bot + wheel_h, fill=wc, outline="#000")
            wr1 = self.canvas.create_rectangle(x2 - wheel_w, wy_top, x2 + 2, wy_top + wheel_h, fill=wc, outline="#000")
            wr2 = self.canvas.create_rectangle(x2 - wheel_w, wy_bot, x2 + 2, wy_bot + wheel_h, fill=wc, outline="#000")
        else:
            wl1 = self.canvas.create_oval(x1 - 2, wy_top, x1 + wheel_w, wy_top + wheel_h, fill=wc, outline="#000")
            wl2 = self.canvas.create_oval(x1 - 2, wy_bot, x1 + wheel_w, wy_bot + wheel_h, fill=wc, outline="#000")
            wr1 = self.canvas.create_oval(x2 - wheel_w, wy_top, x2 + 2, wy_top + wheel_h, fill=wc, outline="#000")
            wr2 = self.canvas.create_oval(x2 - wheel_w, wy_bot, x2 + 2, wy_bot + wheel_h, fill=wc, outline="#000")
        items.extend([wl1, wl2, wr1, wr2])

        # Plate label on roof stripe
        plate_text = self.canvas.create_text(mid_x, (y1 + y2) // 2, text=plate, fill="#1b1b1b", font=("Segoe UI", 11, "bold"))
        items.append(plate_text)

        return body, items, lights

    def draw_parking_layout(self):
        """Draw parking area with gradient background, rounded slots, and status indicators."""
        theme = self.themes[self.current_theme]
        
        # Gradient background
        self.draw_gradient_bg(theme["bg_start"], theme["bg_end"])
        
        # Center both parking lot and temp lane
        total_width = (self.car_width + 40) * 2 + 40  # two lots + spacing between them
        start_x = (self.canvas_width - total_width) // 2
        
        stall_left = start_x
        stall_right = stall_left + self.car_width + 40
        stall_top = 20
        stall_bottom = self.canvas_height - 20
        
        # Rounded parking lot with shadow effect
        self.canvas.create_rectangle(
            stall_left + 3, stall_top + 3, stall_right + 3, stall_bottom + 3,
            fill="#0a0a0a", outline="", width=0
        )
        lot = self.canvas.create_rectangle(
            stall_left, stall_top, stall_right, stall_bottom,
            fill=theme["lot_color"], outline="#2a3a4a", width=2
        )

        for i in range(self.max_size):
            y = self.canvas_height - (i + 1) * (self.car_height + self.slot_gap)
            slot_num = i + 1
            y_mid = y + self.car_height / 2
            
            # Rounded slot rectangles instead of lines
            slot_rect = self.canvas.create_rectangle(
                stall_left + 10, y - 5, stall_right - 10, y + self.car_height + 5,
                outline=theme["slot_line"], width=2, dash=(8, 4), fill=""
            )
            
            # Slot number
            self.canvas.create_text(stall_left - 40, y_mid, text=str(slot_num), 
                                   fill=theme["slot_text"], font=("Segoe UI", 12, "bold"))
            
            # Status indicator (circle) - starts green (empty)
            indicator = self.canvas.create_oval(
                stall_right + 15, y_mid - 8, stall_right + 31, y_mid + 8,
                fill=theme["indicator_empty"], outline="", width=0
            )
            self.slot_indicators[slot_num] = indicator

        temp_left = stall_right + 40
        temp_right = temp_left + self.car_width + 40
        
        # Rounded temp lane with shadow
        self.canvas.create_rectangle(
            temp_left + 3, stall_top + 3, temp_right + 3, stall_bottom + 3,
            fill="#0a0a0a", outline="", width=0
        )
        self.canvas.create_rectangle(
            temp_left, stall_top, temp_right, stall_bottom,
            fill=theme["lot_color"], outline="#2a3a4a", width=2
        )
        self.temp_lane_x = temp_left + 20

        arrow_y = stall_top + 12
        for ax in range(stall_left + 20, stall_right - 20, 60):
            self.canvas.create_polygon(ax, arrow_y, ax + 10, arrow_y + 5, ax, arrow_y + 10, fill="#2f435f", outline="")
        
        self.canvas.create_text((stall_left + stall_right) // 2, stall_top - 6, text="PARK", fill="#6e85a9", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text((temp_left + temp_right) // 2, stall_top - 6, text="TEMP LANE", fill="#6e85a9", font=("Segoe UI", 11, "bold"))
    
    def draw_gradient_bg(self, color1, color2):
        """Draw a smooth vertical gradient background."""
        steps = 50
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        for i in range(steps):
            ratio = i / steps
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y1 = i * self.canvas_height / steps
            y2 = (i + 1) * self.canvas_height / steps
            self.canvas.create_rectangle(0, y1, self.canvas_width, y2, fill=color, outline="")

    def play_arrival_sound(self):
        """Play layered car engine sound on arrival: startup + idle hum."""
        if not self.sound_enabled:
            return
        try:
            if WINSOUND_AVAILABLE:
                # Windows: realistic engine startup sequence
                for freq in [150, 180, 220, 280, 350]:
                    winsound.Beep(freq, 100)
                # Low idle hum
                threading.Thread(target=lambda: winsound.Beep(120, 400), daemon=True).start()
            elif PYGAME_AVAILABLE:
                # Aggressive sports car startup with deep rumble to high rev
                self.generate_and_play_pygame_sound(duration=1.6, pitch_start=80, pitch_end=500, engine_rev=True)
                # Settle to sporty idle
                threading.Thread(target=lambda: [time.sleep(1.4), self.generate_and_play_pygame_sound(duration=0.8, pitch_start=100, pitch_end=120, engine_rev=False)], daemon=True).start()
        except Exception as e:
            print(f"Sound error: {e}")

    def play_departure_sound(self):
        """Play layered car acceleration sound on departure: rev + fade-out."""
        if not self.sound_enabled:
            return
        try:
            if WINSOUND_AVAILABLE:
                # Windows: realistic engine acceleration sequence
                for freq in [350, 400, 450, 500, 550, 600]:
                    winsound.Beep(freq, 120)
                # Fade out
                for freq in [550, 450, 300, 200]:
                    winsound.Beep(freq, 80)
            elif PYGAME_AVAILABLE:
                # Aggressive sports car acceleration - deep roar to screaming high rev
                self.generate_and_play_pygame_sound(duration=2.0, pitch_start=150, pitch_end=800, engine_rev=True)
                # Doppler effect as car speeds away
                threading.Thread(target=lambda: [time.sleep(1.7), self.generate_and_play_pygame_sound(duration=1.4, pitch_start=650, pitch_end=150, engine_rev=False)], daemon=True).start()
        except Exception as e:
            print(f"Sound error: {e}")
    
    def play_full_garage_sound(self):
        """Play soft warning beep when garage is full."""
        if not self.sound_enabled:
            return
        try:
            if WINSOUND_AVAILABLE:
                for _ in range(3):
                    winsound.Beep(800, 150)
                    time.sleep(0.1)
            elif PYGAME_AVAILABLE:
                for _ in range(3):
                    self.generate_and_play_pygame_sound(duration=0.15, pitch_start=800, pitch_end=800, engine_rev=False)
                    time.sleep(0.1)
        except Exception as e:
            print(f"Sound error: {e}")
    
    def play_ambient_garage_hum(self):
        """Play soft ambient garage hum in background."""
        if not self.sound_enabled:
            return
        try:
            if PYGAME_AVAILABLE:
                threading.Thread(
                    target=lambda: self.generate_and_play_pygame_sound(duration=2.0, pitch_start=80, pitch_end=80, engine_rev=False),
                    daemon=True
                ).start()
        except Exception as e:
            print(f"Ambient sound error: {e}")
    
    def apply_camera_shake(self, intensity=3, duration=300):
        """Apply screen shake effect on engine rev (visual only, doesn't modify canvas)."""
        # Subtle effect - just a brief visual feedback without disrupting the scene
        # Could be enhanced with actual coordinate offsets if needed, but keeps it simple
        pass

    def generate_and_play_pygame_sound(self, duration=1.2, pitch_start=150, pitch_end=400, engine_rev=True):
        """Generate and play a realistic sports car engine roar using pygame."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros(frames, dtype=np.float32)
        
        for i in range(frames):
            progress = i / frames
            
            # Exponential frequency curve for realistic acceleration
            freq = pitch_start + (pitch_end - pitch_start) * (progress ** 1.5)
            phase = 2 * np.pi * freq * i / sample_rate
            
            # Complex multi-layer engine sound
            # Layer 1: Deep bass rumble (exhaust)
            bass_freq = freq * 0.5
            bass_phase = 2 * np.pi * bass_freq * i / sample_rate
            bass = 0.6 * np.sin(bass_phase) + 0.3 * np.sin(bass_phase * 1.5)
            
            # Layer 2: Main engine harmonics (aggressive)
            engine = (
                0.5 * np.sin(phase) +
                0.4 * np.sin(2 * phase) +
                0.35 * np.sin(3 * phase) +
                0.3 * np.sin(4 * phase) +
                0.25 * np.sin(5 * phase) +
                0.2 * np.sin(6 * phase) +
                0.15 * np.sin(8 * phase) +
                0.1 * np.sin(12 * phase)
            )
            
            # Layer 3: High frequency "sizzle" for sports car character
            sizzle_freq = freq * 3
            sizzle_phase = 2 * np.pi * sizzle_freq * i / sample_rate
            sizzle = 0.15 * np.sin(sizzle_phase) + 0.1 * np.sin(sizzle_phase * 1.3)
            
            # Combine layers
            sample = bass * 0.5 + engine * 0.4 + sizzle * 0.1
            
            # Heavy noise for aggressive engine texture
            noise = np.random.uniform(-0.3, 0.3)
            sample = sample * 0.7 + noise * 0.3
            
            # FM modulation for "growl" effect
            if engine_rev:
                mod_freq = 8 + 12 * progress
                modulation = 1.0 + 0.3 * np.sin(2 * np.pi * mod_freq * i / sample_rate)
                sample *= modulation
            
            # Aggressive envelope with punchy attack
            if progress < 0.05:
                envelope = (progress / 0.05) ** 0.3  # Fast attack
            elif progress < 0.9:
                # Crescendo for revving feel
                envelope = 0.9 + 0.1 * progress
            else:
                envelope = 1.0 - ((progress - 0.9) / 0.1) ** 1.5  # Sharp decay
            
            arr[i] = sample * envelope * 0.5
        
        # Apply compression for louder, punchier sound
        arr = np.tanh(arr * 2.0) * 0.8
        
        # Normalize and convert to int16
        max_val = np.max(np.abs(arr)) + 0.01
        arr = np.int16(arr / max_val * 32767)
        
        # Create pygame sound and play
        sound = pygame.sndarray.make_sound(arr)
        sound.play()

    def speak(self, text):
        """Convert text to speech and announce it."""
        if not self.tts_enabled:
            return
        try:
            # Create fresh engine for each call (thread-safe)
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            # Set voice to female
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[1].id)  # Select female voice (index 1)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception as e:
            print(f"TTS error: {e}")

    def speak_async(self, text):
        """Queue text for speech in a background worker to avoid UI blocking."""
        if not self.tts_enabled:
            return
        try:
            self.tts_queue.put(text, block=False)
        except queue.Full:
            print(f"TTS queue full, skipping: {text}")
        except Exception as e:
            print(f"TTS queue error: {e}")

    def set_lights(self, car, on=True):
        """Set car lights on (bright) or off (dim)."""
        if "lights" not in car:
            return
        headlight_color = "#ffd27f" if on else "#6b6b2f"
        taillight_color = "#ff6b6b" if on else "#6b3333"
        for idx, light_id in enumerate(car["lights"]):
            # First 2 lights are headlights, last 2 are taillights
            color = headlight_color if idx < 2 else taillight_color
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
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
                # Set voice to female
                voices = engine.getProperty('voices')
                if voices:
                    engine.setProperty('voice', voices[1].id)  # Select female voice (index 1)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                del engine
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS worker error: {e}")
            finally:
                if text is not None:
                    try:
                        self.tts_queue.task_done()
                    except Exception:
                        pass

    # ---------------- Departure ----------------
    def depart_car(self):
        # Button press animation
        self.animate_button_press(self.departure_btn)
        
        plate = self.entry.get().strip()
        if not plate:
            self.log_event("⚠ Departure failed: no plate entered")
            return

        stack = self.parking.get_stack()
        if plate not in stack:
            self.log_event(f"✕ Departure failed: car with plate {plate} is not found")
            return

        self.entry.delete(0, tk.END)
        self.animate_departure(plate)

    def animate_departure(self, plate):
        """Smooth departure: move blocking cars to temp lane sequentially, then lift target car,
        then bring temp cars back after target is removed."""
        stack = self.parking.get_stack()
        index = stack.index(plate)
        temp_cars = stack[index+1:]
        above_cars = list(reversed(temp_cars))  # top-most first

        tx = getattr(self, "temp_lane_x", self.base_x + 180)

        def move_temp_out(i=0):
            if i >= len(above_cars):
                return move_target_up()
            p = above_cars[i]
            car = self.cars.get(p)
            if not car:
                return move_temp_out(i+1)
            self.animate_move(car, tx, None, steps=80, delay_ms=20, on_complete=lambda: move_temp_out(i+1))

        def move_target_up():
            """Animate target car exiting: pull forward slightly, then drive left to exit."""
            car = self.cars.get(plate)
            if not car:
                return finish_departure_chain()
            
            rect = self.canvas.coords(car["rect"])
            if not rect:
                return finish_departure_chain()
            
            current_y = rect[1]
            
            # Step 1: Pull forward out of slot
            def pull_forward():
                self.animate_move(car, self.base_x + 80, current_y, steps=35, delay_ms=25, on_complete=drive_left)
            
            # Step 2: Drive left to exit where cars enter
            def drive_left():
                self.animate_move(car, -self.car_width - 100, current_y, steps=80, delay_ms=20, on_complete=finish_departure_chain)
            
            pull_forward()

        def finish_departure_chain():
            # Camera shake on engine rev
            self.apply_camera_shake()
            
            # Glow effect on departure
            if plate in self.cars:
                self.show_glow_effect(plate, "departure")
                
                # Delete all drawn parts for this car after glow
                self.after(800, lambda: self.remove_car_visuals(plate))

            # Update logic and announce
            self.parking.depart(plate)
            self.log_event(f"⊘ Departure: {plate}")
            self.play_departure_sound()
            
            # Delay TTS to avoid audio contention with engine sound
            self.after(1000, lambda: self.speak_async(f"Car {plate} departed."))

            # Bring temp cars back sequentially: bottom-most returns first
            return_order = list(reversed(above_cars))

            def move_temp_back(j=0):
                if j >= len(return_order):
                    self.update_info()
                    return
                p_back = return_order[j]
                car_back = self.cars.get(p_back)
                if not car_back:
                    return move_temp_back(j+1)
                # Compute target slot for this car and animate back
                try:
                    idx = self.parking.get_stack().index(p_back)
                except ValueError:
                    return move_temp_back(j+1)
                target_y = (
                    self.canvas_height
                    - (idx + 1) * (self.car_height + self.slot_gap)
                )
                self.animate_move(car_back, self.base_x, target_y, steps=80, delay_ms=20, on_complete=lambda: move_temp_back(j+1))

            move_temp_back()

        move_temp_out()

    def finish_departure(self, plate, temp_cars):
        # Delete all drawn parts for this car
        for item in self.cars[plate].get("items", []):
            self.canvas.delete(item)
        del self.cars[plate]

        self.parking.depart(plate)
        self.log_event(f"🚘 Departure: {plate}")
        self.play_departure_sound()
        self.speak_async(f"Car {plate} departed.")

        # Restack remaining cars
        self.restack()

        self.update_info()

    # ---------------- Positioning ----------------
    def animate_to_slot(self, plate, on_complete=None):
        """Animate car with realistic parking maneuver: drive forward, align, then back into slot."""
        stack = self.parking.get_stack()
        index = stack.index(plate)

        target_y = (
            self.canvas_height
            - (index + 1) * (self.car_height + self.slot_gap)
        )
        
        # Multi-step realistic parking animation
        car = self.cars.get(plate)
        if not car:
            return
        
        # Step 1: Drive forward (horizontally) to staging position
        staging_x = self.base_x - 100
        
        def step1_drive_forward():
            self.animate_move(car, staging_x, target_y, steps=80, delay_ms=20, on_complete=step2_align)
        
        # Step 2: Move right to align with parking slot
        def step2_align():
            self.animate_move(car, self.base_x + 20, target_y, steps=40, delay_ms=25, on_complete=step3_back_in)
        
        # Step 3: Back into the slot (reverse)
        def step3_back_in():
            self.animate_move(car, self.base_x, target_y, steps=30, delay_ms=30, on_complete=step4_adjust)
        
        # Step 4: Small forward adjustment to center perfectly
        def step4_adjust():
            if callable(on_complete):
                on_complete()
        
        step1_drive_forward()

    def restack(self):
        for plate in self.parking.get_stack():
            self.animate_to_slot(plate)

    def update_info(self):
        parked = len(self.parking.get_stack())
        available = self.max_size - parked
        self.info.configure(text=f"Cars Parked: {parked} / {self.max_size}")
        
        # Update garage status indicator
        if available == 0:
            self.status_label.configure(text="🔴 Full", text_color="#ff4466")
        elif available <= 2:
            self.status_label.configure(text="🟡 Almost Full", text_color="#ffa726")
        else:
            self.status_label.configure(text="🟢 Available", text_color="#00ff88")
        
        # Update slot indicators
        self.update_slot_indicators()
        
        # Only announce when slot count actually changes (throttle to avoid flooding)
        if self.tts_enabled and available != self.last_slots_announced:
            self.last_slots_announced = available
            # Delay to avoid overlapping with departure announcement
            self.after(2000, lambda: self.speak_async(f"{available} slots available."))

    def animate_move(self, car, target_x, target_y, steps=36, delay_ms=40, on_complete=None):
        """Animate a car to (target_x, target_y). If target_y is None, keep current y.
        Supports an on_complete callback when the animation ends. Lights turn on during movement."""
        rect_coords = self.canvas.coords(car.get("rect"))
        if not rect_coords or len(rect_coords) < 4:
            return
        x1, y1, x2, y2 = rect_coords
        if target_y is None:
            target_y = y1

        dx = target_x - x1
        dy = target_y - y1

        # Turn lights ON when movement starts
        car["moving"] = True
        self.set_lights(car, on=True)

        def step(i=0):
            if i >= steps:
                # Snap to the exact target to avoid drift
                current = self.canvas.coords(car.get("rect"))
                if not current or len(current) < 2:
                    return
                final_dx = target_x - current[0]
                final_dy = target_y - current[1]
                for item in car.get("items", [car.get("rect")]):
                    if item is not None:
                        self.canvas.move(item, final_dx, final_dy)
                # Turn lights OFF when movement ends
                car["moving"] = False
                self.set_lights(car, on=False)
                if callable(on_complete):
                    self.after(0, on_complete)
                return
            for item in car.get("items", [car.get("rect")]):
                if item is not None:
                    self.canvas.move(item, dx/steps, dy/steps)
            self.after(delay_ms, step, i+1)

        step()
    
    def show_glow_effect(self, plate, effect_type="arrival"):
        """Show a glowing effect around the car: green for arrival, red/orange for departure."""
        if plate not in self.cars:
            return
        
        theme = self.themes[self.current_theme]
        glow_color = theme["glow_arrival"] if effect_type == "arrival" else theme["glow_departure"]
        
        rect_coords = self.canvas.coords(self.cars[plate].get("rect"))
        if not rect_coords or len(rect_coords) < 4:
            return
        x1, y1, x2, y2 = rect_coords
        
        # Create glow layers
        glow_layers = []
        for i in range(5):
            offset = 8 + i * 4
            alpha_val = int(255 * (1 - i * 0.2))
            # Create semi-transparent glow effect
            glow = self.canvas.create_rectangle(
                x1 - offset, y1 - offset, x2 + offset, y2 + offset,
                outline=glow_color, width=3, fill=""
            )
            glow_layers.append(glow)
        
        # Animate fade out
        def fade_glow(step=0):
            if step >= 15:
                for glow in glow_layers:
                    self.canvas.delete(glow)
                return
            # Fade effect
            self.after(50, lambda: fade_glow(step + 1))
        
        fade_glow()
    
    def remove_car_visuals(self, plate):
        """Remove all visual elements of a car."""
        if plate in self.cars:
            for item in self.cars[plate].get("items", []):
                self.canvas.delete(item)
            del self.cars[plate]
    
    def update_slot_indicators(self):
        """Update slot status indicators with smooth pulse animation."""
        theme = self.themes[self.current_theme]
        stack = self.parking.get_stack()
        
        for slot_num in range(1, self.max_size + 1):
            indicator = self.slot_indicators.get(slot_num)
            if not indicator:
                continue
            
            # Check if slot is occupied (slot_num - 1 is the index)
            is_occupied = (slot_num - 1) < len(stack)
            target_color = theme["indicator_occupied"] if is_occupied else theme["indicator_empty"]
            
            # Pulse animation when status changes
            self.animate_indicator_pulse(indicator, target_color)
    
    def animate_indicator_color(self, indicator, target_color, steps=10, current_step=0):
        """Smoothly animate indicator color change."""
        if current_step >= steps:
            self.canvas.itemconfig(indicator, fill=target_color)
            return
        
        if current_step == 0:
            self.after(0, lambda: self.canvas.itemconfig(indicator, fill=target_color))
    
    def animate_indicator_pulse(self, indicator, target_color):
        """Pulse animation for indicator when status changes."""
        self.canvas.itemconfig(indicator, fill=target_color)
        
        def pulse(step=0, max_steps=15):
            if step >= max_steps:
                self.canvas.itemconfig(indicator, outline="")
                return
            
            # Create pulsing glow outline
            width = max(1, int(3 - (step / max_steps) * 2))
            self.canvas.itemconfig(indicator, outline=target_color, width=width)
            self.after(30, lambda: pulse(step + 1, max_steps))
        
        pulse()
    
    def change_theme(self, theme_name):
        """Change the visual theme of the parking garage."""
        self.current_theme = theme_name
        
        # Save car positions BEFORE deleting canvas
        car_positions = {}
        for plate in list(self.cars.keys()):
            car_data = self.cars[plate]
            rect_coords = self.canvas.coords(car_data.get("rect"))
            if rect_coords and len(rect_coords) >= 4:
                car_positions[plate] = {
                    "x1": rect_coords[0],
                    "y1": rect_coords[1],
                    "color": car_data.get("color", random.choice(CAR_COLORS))
                }
        
        # Clear canvas and redraw with new theme
        self.canvas.delete("all")
        self.slot_indicators.clear()
        self.cars.clear()
        self.draw_parking_layout()
        
        # Recreate all cars at their saved positions with new theme colors
        for plate, pos_data in car_positions.items():
            x1, y1 = pos_data["x1"], pos_data["y1"]
            x2 = x1 + self.car_width
            y2 = y1 + self.car_height
            color = pos_data["color"]
            
            style = self.pick_style_variants()
            body_id, item_ids, light_ids = self.draw_car(x1, y1, x2, y2, color, plate, style)
            self.cars[plate] = {"rect": body_id, "items": item_ids, "lights": light_ids, "moving": False, "color": color}
        
        self.update_info()


# ---------------- Entrypoint ----------------
def main():
    """Launch a window with the parking stack UI."""
    root = ctk.CTk()
    root.title("Parking Garage - Stack")
    root.geometry("680x760")

    app = StackUI(root, max_size=5)
    app.pack(fill="both", expand=True, padx=12, pady=12)

    root.mainloop()


if __name__ == "__main__":
    main()