import time
import math
import random

import time
import math
import random
from physics_engine import TireModel, AeroModel

class TelemetryGenerator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.state = "ACCELERATE"
        self.speed = 0.0 # m/s internally, converted to km/h for output
        self.rpm = 1000.0
        self.gear = 1
        self.throttle = 0.0
        self.brake = 0.0
        self.steering = 0.0
        self.engine_temp = 90.0
        self.distance = 0.0
        self.last_update = time.time()
        
        # F1 Physics Constants
        self.mass = 798.0 # kg (Min weight)
        self.max_power = 750000.0 # Watts (~1000 hp)
        # self.drag_coeff = 1.0 # REPLACED BY AERO MODEL
        # self.frontal_area = 1.6 # REPLACED BY AERO MODEL
        # self.air_density = 1.225 # REPLACED BY AERO MODEL
        self.tire_friction = 1.5 # Grip coefficient
        
        # Advanced Physics: Tires (FL, FR, RL, RR)
        self.tires = [
            TireModel("SOFT"), # FL
            TireModel("SOFT"), # FR
            TireModel("SOFT"), # RL
            TireModel("SOFT")  # RR
        ]
        
        # Advanced Physics: Aerodynamics
        self.aero = AeroModel()
        
        # Gear Ratios (Speed in km/h -> m/s)
        self.gear_ratios = {
            1: 80 / 3.6,
            2: 130 / 3.6,
            3: 170 / 3.6,
            4: 220 / 3.6,
            5: 260 / 3.6,
            6: 290 / 3.6,
            7: 320 / 3.6,
            8: 360 / 3.6
        }
        self.max_rpm = 12000.0
        self.idle_rpm = 1000.0
        self.shift_up_rpm = 11600.0
        self.shift_down_rpm = 5000.0

    def get_next_frame(self):
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Prevent physics explosion on large time steps (e.g. after pause or lag)
        if dt > 0.1:
            dt = 0.1
        
        # --- State Machine ---
        if self.state == "ACCELERATE":
            self.throttle = 1.0
            self.brake = 0.0
            # Brake at end of straight (approx 315 km/h)
            if self.speed * 3.6 > 315: 
                self.state = "BRAKE"
        
        elif self.state == "BRAKE":
            self.throttle = 0.0
            self.brake = 1.0
            # Corner entry speed (approx 80 km/h)
            if self.speed * 3.6 < 80: 
                self.state = "CORNER"
                
        elif self.state == "CORNER":
            self.throttle = 0.5 # Partial throttle maintenance
            self.brake = 0.0
            if random.random() < 0.01: # Exit corner
                self.state = "ACCELERATE"
        
        # --- Tire Updates ---
        speed_kmh = self.speed * 3.6
        
        # Estimate Slip & Load based on State
        base_load = (self.mass * 9.81) / 4.0
        
        for i, tire in enumerate(self.tires):
            slip = 0.0
            load = base_load
            
            if self.state == "ACCELERATE":
                if i >= 2: # Rear
                    slip = 0.05 + (self.throttle * 0.05)
                    load *= 1.2
                else: # Front
                    slip = 0.01
                    load *= 0.8
                    
            elif self.state == "BRAKE":
                if i < 2: # Front
                    slip = 0.1
                    load *= 1.4
                else: # Rear
                    slip = 0.02
                    load *= 0.6
                    
            elif self.state == "CORNER":
                slip = 0.08
                if random.random() > 0.5:
                    if i % 2 == 0: load *= 1.5
                    else: load *= 0.5
                else:
                    if i % 2 != 0: load *= 1.5
                    else: load *= 0.5
            
            tire.update(dt, speed_kmh, slip, load)

        # --- Aero Updates ---
        # Simulate DRS Zone: On straights (ACCELERATE) and speed > 150
        in_drs_zone = (self.state == "ACCELERATE" and speed_kmh > 150)
        # Simulate Time Gap: Randomly available (50% chance)
        time_gap = 0.5 if random.random() > 0.5 else 1.5
        
        self.aero.update(speed_kmh, in_drs_zone, time_gap)
        
        # Auto-activate DRS if available (for demo purposes)
        if self.aero.drs_available and not self.aero.drs_active:
            self.aero.toggle_drs()
            
        drag_force, downforce_n = self.aero.calculate_forces(speed_kmh)

        # --- Physics Calculation (F = ma) ---
        
        # Average Tire Grip (0.0 to 1.2)
        avg_grip = sum([t.grip for t in self.tires]) / 4.0
        
        # Add Downforce to Grip! (More downforce = More Grip)
        # F_friction = coeff * (NormalLoad + Downforce)
        # We approximate this by boosting the grip multiplier
        downforce_grip_factor = 1.0 + (downforce_n / (self.mass * 9.81))
        total_grip = avg_grip * downforce_grip_factor
        
        # 1. Engine Force
        if self.speed < 1.0:
            engine_force = self.mass * 10.0 * self.throttle
        else:
            engine_force = (self.max_power * self.throttle) / self.speed
            # Traction Limit
            max_traction = self.mass * 9.81 * self.tire_friction * total_grip
            engine_force = min(engine_force, max_traction)

        # 2. Braking Force
        braking_force = self.mass * 9.81 * 5.0 * self.brake * total_grip

        # 3. Aerodynamic Drag (Calculated by AeroModel)
        # drag_force is already calculated

        # 4. Net Force
        net_force = engine_force - braking_force - drag_force

        # 5. Acceleration (a = F/m)
        acceleration = net_force / self.mass

        # 6. Update Velocity
        self.speed += acceleration * dt
        self.speed = max(0.0, self.speed)

        # --- Gear Logic ---
        current_gear_max = self.gear_ratios[self.gear]
        target_rpm = (self.speed / current_gear_max) * self.max_rpm
        target_rpm = max(self.idle_rpm, min(self.max_rpm, target_rpm))
        self.rpm += (target_rpm - self.rpm) * 20.0 * dt

        if self.rpm > self.shift_up_rpm and self.gear < 8:
            self.gear += 1
        elif self.gear > 1:
            lower_gear_max = self.gear_ratios[self.gear - 1]
            if self.speed < (lower_gear_max * 0.90):
                self.gear -= 1

        # Engine Temp
        target_temp = 90.0 + (self.rpm / 12000.0) * 30.0
        self.engine_temp += (target_temp - self.engine_temp) * 0.5 * dt
        
        # Anomaly
        is_anomaly = False
        if random.random() < 0.0005:
             self.engine_temp = 135.0
             is_anomaly = True

        # DEBUG
        # print(f"State: {self.state} | Speed: {speed_kmh:.1f} km/h | DRS: {self.aero.drs_active}")

        return {
            "timestamp": current_time,
            "speed_kmh": round(speed_kmh, 2),
            "rpm": round(self.rpm, 0),
            "gear": self.gear,
            "throttle": round(self.throttle, 2),
            "brake": round(self.brake, 2),
            "steering": round(self.steering, 2),
            "engine_temp": round(self.engine_temp, 1),
            "is_anomaly": is_anomaly,
            "tires": [t.get_status() for t in self.tires],
            "aero": {
                "drs": self.aero.drs_active,
                "drag": round(drag_force, 0),
                "downforce": round(downforce_n, 0)
            }
        }
