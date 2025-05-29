# This class simulates the ECU of a vehicle.

# The ECU has a bunch of sensors (inputs) and outputs. It also holds *calculated* values, which are computations it runs on sensor data.

# It also is programmed with certain maps that are used to control engine and transmission. 
# For the purposes of this project, the most important thing is that the ecu can control the throttle and the transmission of a vehicle.


# There is currently a lot more being initialized as defuault here that should actually be passed by the class that creates the ECU, but this will do for now.
import time
class TCU:
    def __init__(self, transmission_map:dict[tuple[tuple[int,int], tuple[int,int]], int]):
        self.transmission_map = transmission_map
        self.current_gear = 1
        # Kick-down when throttle ≥ 80% or throttle rate ≥ 0.5/s
        self.kickdown_throttle = 80
        self.kickdown_rate = 0.5
        # Don’t shift again until this many seconds have passed
        self.min_shift_interval = 1.0  
        self.last_shift_time = 0.0
        # Don’t upshift until you’re this many kph *above* the map threshold
        # and don’t downshift until this many kph *below* it
        self.hysteresis_kph = 2.0

    def select_gear_from_map(self, throttle_pct:float, speed_kph:float):
        """Basic lookup in your 2D map."""
        t = throttle_pct * 100  # convert 0–1 → 0–100
        for (t_range, s_range), gear in self.transmission_map.items():
            t_min, t_max = t_range
            s_min, s_max = s_range
            if t_min <= t < t_max and s_min <= speed_kph < s_max:
                return gear
        return self.current_gear

    def update(self, throttle_pct:float, throttle_rate:float, speed_kph:float, engine_load_pct:float):
        now = time.time()
        # 1) Base gear from map
        map_gear = self.select_gear_from_map(throttle_pct, speed_kph)
        target = map_gear
        reason = "Map"

        # 2) Throttle-aware kick-down (only if map_gear is not already requesting a downshift)
        # Prevent repeated kickdowns after a shift by only allowing kickdown if the current gear matches the map gear
        # Also, only allow kickdown if enough time has passed since the last shift
        kickdown_allowed = (
            self.current_gear == map_gear and
            self.current_gear > 1 and
            (now - self.last_shift_time) >= self.min_shift_interval
        )
        if (throttle_pct * 100 >= self.kickdown_throttle or 
            abs(throttle_rate) >= self.kickdown_rate):
            if kickdown_allowed:
                target = self.current_gear - 1
                reason = "Kick-down"
        else:
            # 3) Upshift with hysteresis
            if map_gear > self.current_gear:
                # find the lower bound speed for the next gear
                s_min = None
                for (tr, sr), g in self.transmission_map.items():
                    if g == map_gear and tr[0] <= throttle_pct*100 < tr[1]:
                        s_min, _ = sr
                        break
                if s_min is not None and speed_kph >= s_min + self.hysteresis_kph:
                    target = map_gear
                    reason = "Upshift"

            # 4) Downshift with hysteresis
            elif map_gear < self.current_gear:
                lower_gear = map_gear
                s_max = None
                for (tr, sr), g in self.transmission_map.items():
                    if g == lower_gear and tr[0] <= throttle_pct*100 < tr[1]:
                        _, s_max = sr
                        break
                if s_max is not None and speed_kph <= s_max - self.hysteresis_kph:
                    target = map_gear
                    reason = "Downshift"

        # 5) Enforce minimum shift interval
        if target != self.current_gear and (now - self.last_shift_time) >= self.min_shift_interval:
            self.current_gear = target
            self.last_shift_time = now
            print(f"{reason} → gear {self.current_gear} @ {speed_kph:.1f} km/h, "
                  f"throttle {throttle_pct*100:.1f}%, rate {throttle_rate:.2f}/s, "
                  f"load {engine_load_pct:.1f}%")

        return self.current_gear
class ECU:
    def __init__(self, max_rpm: int = 8000):
        # ROM Data
        # Fuel map: (rpm, throttle) -> injector pulse width (ms)
        self.max_rpm = max_rpm
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

        self.tcu = TCU(transmission_map = {
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
        })
        # Outputs
        self.throttle_command = 0.0 # Float from 0 to 1
        # self.gear_command = 0 # request a gear not using this

        # Sensors
        self.prev_throttle_position = 0.0
        self.throttle_position = 0.0 # The current possition of the throttle( not necessarily the same as command due to lag, and possibly idle, etc)
        self.rpm:int = 700
        self.vehicle_speed = 0.0 # Speed of the vehicle from speed sensors        
        self.maf_airflow = 0.0 # MAF sensor reading (used in fuel consumption calculations)
        self.fuel_pressure = 0.0 # fuel pressure at the fuel rail

        # Caclulated values
        self.average_fuel_consumption = 0.0 # The average fuel consumption of the vehicle on the current drive cycle
        self.instant_fuel_consumption = 0.0 # The current fuel consumption of the vehicle (calculcated)
        self.distance_traveled = 0.0 # The distance traveled by the vehicle on the current drive cycle
        self.engine_load = 0.0 # Engine load in percentage

    def command_throttle(self, value: float):
        self.throttle_command = max(0.0, min(1.0, value))

    def shift_gear(self, speed: float, dt: float):
        self.tcu.update(throttle_pct=self.throttle_position,
                        throttle_rate=(self.throttle_position - self.prev_throttle_position) / dt,
                        speed_kph=speed * 3.6,  # Convert m/s to km/h
                        engine_load_pct=self.engine_load)

    def recalculate_values(self):
        self.average_fuel_consumption = 0.0
        self.instant_fuel_consumption = 0.0
        self.distance_traveled = 0.0
        self.engine_load = self._calc_load()

    def _calc_load(self):
        return (self.throttle_position * self.rpm) / (self.max_rpm)
    def update_sensors(self, **kwargs: dict[str, object]):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.recalculate_values()