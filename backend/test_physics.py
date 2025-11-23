import unittest
from physics_engine import TireModel

class TestTireModel(unittest.TestCase):
    def setUp(self):
        self.tire = TireModel("SOFT")

    def test_initialization(self):
        self.assertEqual(self.tire.compound_name, "SOFT")
        self.assertEqual(self.tire.temperature, 25.0)
        self.assertEqual(self.tire.wear, 0.0)
        # Base grip for soft is 1.2.
        # In the new logic, grip is calculated only when _calculate_grip is called.
        # Initially it is just base_grip.
        self.assertEqual(self.tire.grip, 1.2)

    def test_heating_under_load(self):
        # Simulate heavy braking/cornering: High Slip, High Load
        initial_temp = self.tire.temperature
        
        # 1 second of 300km/h, 10% slip, 5000N load
        self.tire.update(dt=1.0, speed_kmh=300, slip_ratio=0.1, load_n=5000)
        
        self.assertGreater(self.tire.temperature, initial_temp)
        print(f"\nHeating Test: {initial_temp}C -> {self.tire.temperature:.2f}C")

    def test_cooling_on_straight(self):
        # Heat up tire first
        self.tire.temperature = 100.0
        
        # Simulate straight: High Speed, Zero Slip, Normal Load
        self.tire.update(dt=1.0, speed_kmh=300, slip_ratio=0.0, load_n=4000)
        
        self.assertLess(self.tire.temperature, 100.0)
        print(f"Cooling Test: 100.0C -> {self.tire.temperature:.2f}C")

    def test_wear_accumulation(self):
        initial_wear = self.tire.wear
        # Simulate burnout
        self.tire.update(dt=1.0, speed_kmh=100, slip_ratio=1.0, load_n=4000)
        
        self.assertGreater(self.tire.wear, initial_wear)
        print(f"Wear Test: {initial_wear}% -> {self.tire.wear*100:.2f}%")

    def test_grip_curve(self):
        # 1. Cold
        self.tire.temperature = 25.0
        self.tire._calculate_grip()
        cold_grip = self.tire.grip
        
        # 2. Optimal
        self.tire.temperature = 100.0
        self.tire._calculate_grip()
        opt_grip = self.tire.grip
        
        # 3. Overheat
        self.tire.temperature = 150.0
        self.tire._calculate_grip()
        hot_grip = self.tire.grip
        
        print(f"Grip Curve: Cold={cold_grip:.2f}, Opt={opt_grip:.2f}, Hot={hot_grip:.2f}")
        
        self.assertGreater(opt_grip, cold_grip)
        self.assertGreater(opt_grip, hot_grip)

from physics_engine import AeroModel

class TestAeroModel(unittest.TestCase):
    def setUp(self):
        self.aero = AeroModel()

    def test_drag_calculation(self):
        # 300 km/h = 83.33 m/s
        # Fd = 0.5 * 1.225 * 1.6 * 1.0 * (83.33^2) ~= 6800 N
        drag, _ = self.aero.calculate_forces(300)
        self.assertAlmostEqual(drag, 6805, delta=100)
        print(f"\nDrag at 300km/h: {drag:.0f} N")

    def test_drs_effect(self):
        speed = 300
        
        # 1. Base Drag
        self.aero.drs_active = False
        drag_closed, _ = self.aero.calculate_forces(speed)
        
        # 2. Open DRS
        self.aero.drs_available = True
        self.aero.toggle_drs()
        self.assertTrue(self.aero.drs_active)
        
        drag_open, _ = self.aero.calculate_forces(speed)
        
        # Drag should be lower
        self.assertLess(drag_open, drag_closed)
        print(f"DRS Effect: {drag_closed:.0f} N -> {drag_open:.0f} N")

    def test_drs_rules(self):
        # Not in zone -> Can't open
        self.aero.update(speed_kmh=200, in_drs_zone=False, time_gap=0.5)
        self.aero.toggle_drs()
        self.assertFalse(self.aero.drs_active)
        
        # In zone but gap > 1s -> Can't open
        self.aero.update(speed_kmh=200, in_drs_zone=True, time_gap=1.5)
        self.aero.toggle_drs()
        self.assertFalse(self.aero.drs_active)
        
        # Valid -> Open
        self.aero.update(speed_kmh=200, in_drs_zone=True, time_gap=0.5)
        self.aero.toggle_drs()
        self.assertTrue(self.aero.drs_active)

if __name__ == '__main__':
    unittest.main()
