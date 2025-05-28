from ecu import ECU
import math
class Car:
    def __init__(self):
        # attributes
        self.weight =  1450 # weight in kg
        self.tire_width = 245 # tire width in mm
        self.tire_diameter = 18 # tire diameter in inches

        # Basically just the transmission
        self.gear_count = 6
        self.gear_ratios = [3.5, 2.2, 1.5, 1.0, 0.8, 0.6]
        self.final_drive_ratio = 3.5

        # Engine (in case I need to simulate it in some way that doesn't fit into the ecu code neatly)
        self.cyclinder_count = 4
        self.displacement = 2398 # in cc
        self.max_rpm = 6_700
        # hp vs rpm curve: {rpm: hp}
        self.power_curve = {
            1000: 40,
            2000: 80,
            3000: 120,
            4000: 160,
            5000: 200,
            6000: 220,
            6700: 210
        }
        # torque vs rpm curve: {rpm: torque (Nm)}
        self.torque_curve = {
            1000: 130,
            2000: 180,
            3000: 210,
            4000: 230,
            5000: 220,
            6000: 200,
            6700: 180
        }
        #dynamic data
        self.ecu = ECU(self.max_rpm)
        self.speed = 0.0

    def get_speed(self): # gets the current speed
        return self.speed

    def set_speed(self, dt): # calculetes the new speed based on the current acceleration
        wheel_force = self.ecu.throttle_position*self.calc_wheel_force() - self.calc_rolling_resistance() - self.calc_drag() # calculate the force at the wheels, minus rolling resistance and drag
        acceleration = wheel_force / self.weight # get acceleration from force and weight
        self.speed = self.speed + acceleration * dt # update speed based on acceleration and time step
        # Convert speed (m/s) to engine RPM
        tire_circumference = math.pi * (self.tire_diameter * 0.0254) # Convert tire diameter from inches to meters
        wheel_rpm = (self.speed / tire_circumference) * 60 if tire_circumference > 0 else 0 # Calculate wheel RPM (m/s to RPM)

        # 2. Calculate engine RPM: wheel RPM * gear ratio * final drive ratio
        gear = self.ecu.tcu.current_gear # Get current gear from ECU
        gear_ratio = self.gear_ratios[gear-1] # Get gear ratio for the current gear
        final_drive = self.final_drive_ratio # Get final drive ratio
        self.ecu.rpm = wheel_rpm * gear_ratio * final_drive # Convert wheel RPM to engine RPM

        if self.ecu.rpm < 700: # stop engine from stalling (because there is no neutral right now)
            self.ecu.rpm = 700
        self.ecu.shift_gear(self.speed, dt) 
    def calc_torque(self, rpm):
        rpms = sorted(self.torque_curve.keys())
        if rpm <= rpms[0]:
            rpm_low = 0
            rpm_high = rpms[0]
            torque_low = 0
            torque_high = self.torque_curve[rpm_high]
            # Linear interpolation
            torque = torque_low + (torque_high - torque_low) * (rpm - rpm_low) / (rpm_high - rpm_low)
        elif rpm >= rpms[-1]:
            torque = self.torque_curve[rpms[-1]]
        else:
            for i in range(0, len(rpms)):
                if rpm < rpms[i]:
                    rpm_low = rpms[i - 1]
                    rpm_high = rpms[i]
                    torque_low = self.torque_curve[rpm_low]
                    torque_high = self.torque_curve[rpm_high]
                    # Linear interpolation
                    torque = torque_low + (torque_high - torque_low) * (rpm - rpm_low) / (rpm_high - rpm_low)
                    break
        return torque


    def calc_wheel_force(self):
        rpm = self.ecu.rpm
        engine_torque = self.calc_torque(rpm)

        gear = self.ecu.tcu.current_gear
        gear_ratio = self.gear_ratios[gear - 1]
        final_drive = self.final_drive_ratio
        wheel_torque = engine_torque * gear_ratio * final_drive

        # 3. Calculate wheel force (F = torque / radius)
        tire_radius_m = (self.tire_diameter * 0.0254) / 2  # inches to meters, then radius
        wheel_force = wheel_torque / tire_radius_m
        return wheel_force

    def calc_rolling_resistance(self):
        # Rolling resistance coefficient for typical car tires
        if self.speed <=0:
            return 0
        c1 = 0.015  # base rolling resistance coefficient
        c2 = 0.0003  # speed-dependent coefficient (example value)
        g = 9.81  # gravity in m/s^2
        v = self.speed  # current speed in m/s
        rolling_resistance = (c1 + c2 * v) * self.weight * g
        return rolling_resistance
    def calc_drag(self):
        # Typical drag coefficient and frontal area for a sedan
        drag_coefficient = 0.29
        frontal_area = 2.2  # m^2
        air_density = 1.225  # kg/m^3 at sea level
        v = self.speed  # speed in m/s

        drag_force = 0.5 * drag_coefficient * frontal_area * air_density * v * v
        return drag_force



    def apply_throttle(self, throttle, dt=0.1):
        # Apply throttle to the car
        self.ecu.throttle_command = throttle # there is a lag here, but we're not simulating it right now
        self.ecu.throttle_position = throttle
        self.set_speed(dt)
