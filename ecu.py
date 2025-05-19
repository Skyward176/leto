# This class simulates the ECU of a vehicle.

# The ECU has a bunch of sensors (inputs) and outputs. It also holds *calculated* values, which are computations it runs on sensor data.

# For the purposes of this project, the most important thing is that the ecu can control the throttle and the transmission of a vehicle.

class ECU:
    def __init__(self):
        # Outputs
        self.throttle_command = 0.0 # Float from 0 to 1
        self.gear_command = 0 # request a gear

        # Sensors
        self.throttle_position = 0.0 # The current possition of the throttle( not necessarily the same as command due to lag, and possibly idle, etc)
        self.current_gear = 0 # The current gear of the vehicle
        self.rpm = 0.0
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