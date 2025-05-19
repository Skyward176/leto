# This class simulates the ECU of a vehicle.

# The ECU has a bunch of sensors (inputs) and outputs. It also holds *calculated* values, which are computations it runs on sensor data.

# It also is programmed with certain maps that are used to control engine and transmission. 
# For the purposes of this project, the most important thing is that the ecu can control the throttle and the transmission of a vehicle.


# There is currently a lot more being initialized as defuault here that should actually be passed by the class that creates the ECU, but this will do for now.

class ECU:
    def __init__(self):
        # ROM Data
        # Fuel map: (rpm, throttle) -> injector pulse width (ms)
        self.fuel_map = {
            (1000, 0.1): 2.5,
            (2000, 0.3): 3.0,
            (3000, 0.5): 4.0,
            (4000, 0.7): 5.0,
            (6000, 1.0): 6.5,
        }

        # Throttle map: (pedal position 0-1) -> throttle plate opening (0-1)
        self.throttle_map = {
            0.0: 0.0,
            0.2: 0.1,
            0.4: 0.25,
            0.6: 0.5,
            0.8: 0.8,
            1.0: 1.0,
        }

        # Ignition map: (rpm, load) -> ignition timing advance (degrees BTDC)
        self.ignition_map = {
            (1000, 0.2): 10,
            (2000, 0.4): 18,
            (3000, 0.6): 24,
            (4000, 0.8): 28,
            (6000, 1.0): 22,
        }

        # Transmission map: (throttle range, speed range) -> recommended gear
        # Throttle ranges: (min%, max%)
        # Speed ranges: (min km/h, max km/h)
        # Example: ((0, 20), (0, 20)): 1 means throttle 0-20%, speed 0-20 km/h -> gear 1

        self.transmission_map = {
            ((0, 20), (0, 20)): 1,
            ((0, 20), (20, 40)): 2,
            ((0, 20), (40, 60)): 3,
            ((0, 20), (60, 80)): 4,
            ((0, 20), (80, 120)): 5,
            ((0, 20), (120, 1000)): 6,

            ((20, 50), (0, 20)): 1,
            ((20, 50), (20, 40)): 2,
            ((20, 50), (40, 60)): 3,
            ((20, 50), (60, 80)): 4,
            ((20, 50), (80, 120)): 5,
            ((20, 50), (120, 1000)): 6,

            ((50, 80), (0, 20)): 1,
            ((50, 80), (20, 40)): 2,
            ((50, 80), (40, 60)): 3,
            ((50, 80), (60, 80)): 4,
            ((50, 80), (80, 120)): 5,
            ((50, 80), (120, 1000)): 6,

            ((80, 101), (0, 20)): 1,
            ((80, 101), (20, 40)): 2,
            ((80, 101), (40, 60)): 3,
            ((80, 101), (60, 80)): 4,
            ((80, 101), (80, 120)): 5,
            ((80, 101), (120, 1000)): 6,
        }

        # Outputs
        self.throttle_command = 0.0 # Float from 0 to 1
        self.gear_command = 0 # request a gear

        # Sensors
        self.throttle_position = 0.0 # The current possition of the throttle( not necessarily the same as command due to lag, and possibly idle, etc)
        self.current_gear = 1 # The current gear of the vehicle
        self.rpm = 700
        self.vehicle_speed = 0.0 # Speed of the vehicle from speed sensors        
        self.maf_airflow = 0.0 # MAF sensor reading (used in fuel consumption calculations)
        self.fuel_pressure = 0.0 # fuel pressure at the fuel rail

        # Caclulated values
        self.average_fuel_consumption = 0.0 # The average fuel consumption of the vehicle on the current drive cycle
        self.instant_fuel_consumption = 0.0 # The current fuel consumption of the vehicle (calculcated)
        self.distance_traveled = 0.0 # The distance traveled by the vehicle on the current drive cycle

    def command_throttle(self, value: float):
        self.throttle_command = max(0.0, min(1.0, value))

    def select_gear(self, gear: int):
        self.gear_command = gear
    
    def recalculate_values(self):
        self.average_fuel_consumption = 0.0
        self.instant_fuel_consumption = 0.0
        self.distance_traveled = 0.0

    def update_sensors(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.recalculate_values()