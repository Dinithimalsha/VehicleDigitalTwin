import math

class TireModel:
    """
    Advanced Tire Physics Model simulating Thermodynamics and Wear.
    """
    
    # Compound Constants
    COMPOUNDS = {
        "SOFT": {
            "base_grip": 1.2,
            "wear_rate": 0.0015, # per second at max load
            "optimal_temp_min": 90.0,
            "optimal_temp_max": 110.0,
            "heat_coeff": 1.2, # Heats up faster
        },
        "MEDIUM": {
            "base_grip": 1.0,
            "wear_rate": 0.0008,
            "optimal_temp_min": 85.0,
            "optimal_temp_max": 105.0,
            "heat_coeff": 1.0,
        },
        "HARD": {
            "base_grip": 0.9,
            "wear_rate": 0.0004,
            "optimal_temp_min": 80.0,
            "optimal_temp_max": 100.0,
            "heat_coeff": 0.8, # Heats up slower
        }
    }

    def __init__(self, compound="MEDIUM"):
        if compound not in self.COMPOUNDS:
            raise ValueError(f"Invalid compound: {compound}. Valid: {list(self.COMPOUNDS.keys())}")
        
        self.compound_name = compound
        self.params = self.COMPOUNDS[compound]
        
        # State
        self.temperature = 25.0 # Ambient start (Celsius)
        self.wear = 0.0 # 0.0 (New) to 1.0 (Dead)
        self.grip = self.params["base_grip"]
        
        # Physics Constants
        self.ambient_temp = 25.0
        self.specific_heat = 1200.0 # J/kg*K (Rubber)
        self.tire_mass = 10.0 # kg
        self.surface_area = 0.5 # m^2 (Contact patch + sidewall for cooling)
        self.convection_coeff = 50.0 # W/m^2*K (Cooling efficiency)

    def update(self, dt, speed_kmh, slip_ratio, load_n):
        """
        Update tire state for a time step.
        
        Args:
            dt: Time step (seconds)
            speed_kmh: Vehicle speed (km/h)
            slip_ratio: Tire slip (0.0 to 1.0, where 1.0 is burnout/lockup)
            load_n: Vertical load on tire (Newtons)
        """
        if dt <= 0:
            return

        speed_ms = speed_kmh / 3.6
        
        # --- 1. THERMODYNAMICS ---
        
        # Heating: Friction (Slip * Load) + Flexing (Speed)
        # Q_gen = (Coeff * Load * SlipSpeed) + (FlexFactor * Speed)
        friction_heat = 0.005 * load_n * (speed_ms * slip_ratio) * self.params["heat_coeff"]
        flex_heat = 2.0 * speed_ms * self.params["heat_coeff"] # Internal flexing
        total_heat_gen = friction_heat + flex_heat
        
        # Cooling: Convection (Airflow)
        # Q_cool = h * A * (T_tire - T_env)
        # Convection coeff increases with speed
        h_dynamic = self.convection_coeff + (2.0 * speed_ms)
        cooling_rate = h_dynamic * self.surface_area * (self.temperature - self.ambient_temp)
        
        # Net Temp Change: dQ = m * c * dT  ->  dT = dQ / (m * c)
        net_energy = (total_heat_gen - cooling_rate) * dt
        temp_change = net_energy / (self.tire_mass * self.specific_heat)
        
        self.temperature += temp_change
        
        # Clamp to realistic bounds (e.g., won't go below ambient or above burning)
        self.temperature = max(self.ambient_temp, self.temperature)
        
        # --- 2. WEAR MODEL ---
        # Wear depends on Load, Slip, and Temperature (hotter = softer = more wear)
        temp_wear_factor = 1.0 + max(0, (self.temperature - 100.0) * 0.02) # Increases above 100C
        wear_step = self.params["wear_rate"] * slip_ratio * (load_n / 4000.0) * temp_wear_factor * dt
        
        # Base wear just from rolling
        rolling_wear = self.params["wear_rate"] * 0.1 * (speed_ms / 100.0) * dt
        
        self.wear += (wear_step + rolling_wear)
        self.wear = min(1.0, self.wear) # Cap at 100% wear
        
        # --- 3. GRIP CALCULATION ---
        self._calculate_grip()

    def _calculate_grip(self):
        """
        Calculate current grip based on Temperature and Wear.
        """
        # Temperature Curve (Gaussian-ish)
        opt_min = self.params["optimal_temp_min"]
        opt_max = self.params["optimal_temp_max"]
        
        temp_factor = 1.0
        
        if self.temperature < opt_min:
            # Cold: Linear ramp from 0.6 to 1.0
            # 25C -> 0.6, OptMin -> 1.0
            t_norm = (self.temperature - 25.0) / (opt_min - 25.0)
            temp_factor = 0.6 + (0.4 * max(0.0, t_norm))
            
        elif self.temperature > opt_max:
            # Overheat: Drop off
            # OptMax -> 1.0, 150C -> 0.7
            overheat = self.temperature - opt_max
            temp_factor = max(0.5, 1.0 - (overheat * 0.01))
            
        else:
            # Optimal Window
            temp_factor = 1.0
            
        # Wear Factor (Linear drop off)
        # 0% wear -> 1.0, 100% wear -> 0.3
        wear_factor = 1.0 - (self.wear * 0.7)
        
        self.grip = self.params["base_grip"] * temp_factor * wear_factor

    def get_status(self):
        return {
            "compound": self.compound_name,
            "temp": round(self.temperature, 1),
            "wear": round(self.wear * 100, 1), # Percent
            "grip": round(self.grip, 2)
        }

class AeroModel:
    """
    Aerodynamics Model simulating Drag and Downforce with DRS.
    """
    def __init__(self):
        # Constants
        self.air_density = 1.225 # kg/m^3
        self.frontal_area = 1.6 # m^2
        
        # Drag Coefficients
        self.cd_base = 1.0 # High downforce setup
        self.cd_drs_open = 0.7 # 30% reduction
        
        # Downforce Coefficients (Cl = Lift Coefficient, negative for downforce)
        self.cl_base = 3.5 
        self.cl_drs_open = 2.5 # Less downforce when DRS open
        
        # State
        self.drs_active = False
        self.drs_available = False # In zone + <1s gap

    def update(self, speed_kmh, in_drs_zone, time_gap):
        """
        Update Aero state (DRS logic).
        """
        # DRS Rules:
        # 1. Must be in DRS Zone
        # 2. Gap to car ahead < 1.0s (Simulated)
        # 3. Speed > 0
        self.drs_available = in_drs_zone and (time_gap < 1.0)
        
        # Auto-close DRS if braking or slow
        if speed_kmh < 10.0:
            self.drs_active = False

    def toggle_drs(self):
        """
        Driver attempts to toggle DRS.
        """
        if self.drs_available:
            self.drs_active = not self.drs_active
        else:
            self.drs_active = False

    def calculate_forces(self, speed_kmh):
        """
        Calculate Drag and Downforce at current speed.
        Returns: (DragForce_N, Downforce_N)
        """
        speed_ms = speed_kmh / 3.6
        
        # Dynamic Coefficients based on DRS
        cd = self.cd_drs_open if self.drs_active else self.cd_base
        cl = self.cl_drs_open if self.drs_active else self.cl_base
        
        # F_drag = 0.5 * rho * A * Cd * v^2
        drag = 0.5 * self.air_density * self.frontal_area * cd * (speed_ms ** 2)
        
        # F_downforce = 0.5 * rho * A * Cl * v^2
        downforce = 0.5 * self.air_density * self.frontal_area * cl * (speed_ms ** 2)
        
        return drag, downforce
