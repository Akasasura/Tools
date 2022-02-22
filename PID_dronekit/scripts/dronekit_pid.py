import dronekit
from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException, ChannelsOverride
from time import sleep


class PID:
    def __init__(self, setpoint=1.0, Kp=1.0, Ki=1.0, Kd=1.0):
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._setpoint = setpoint
        self._last_error = 0.0
        self._proportional = 0.0
        self._integral = 0.0
        self._derivative = 0.0

    def setKp(self, value):
        self._Kp = value

    def setKi(self, value):
        self._Ki = value

    def setKd(self, value):
        self.Kd = value

    def getPID(self, current, setpoint=None):
        if setpoint is not None:
            setpoint = self._setpoint
        err = setpoint - current
        self._proportional = self._Kp * err
        # no integral windup (NEEDED) soon will be added
        self._integral += err
        self._derivative = self._Kd * (err - self._last_error)
        out = self._proportional + self._integral + self._derivative
        if out > 2000:
            out = 2000
        elif out < 1000:
            out = 1000
        self._last_error = err
        return int(out)


class Drone:
    def __init__(self, connection='127.0.0.1:14553', baudrate=57600):
        try:
            self.vehicle = connect(connection, baud=baudrate, wait_ready=True)
        except APIException:
            print("Connection Failed")
        sleep(0.5)
        print(" === VEHICLE STATUS ===")
        # vehicle is an instance of the Vehicle class
        print("Autopilot Firmware version: %s" % self.vehicle.version)
        print("Autopilot capabilities (supports ftp): %s" %
              self.vehicle.capabilities.ftp)
        print("Global Location: %s" % self.vehicle.location.global_frame)
        print("Global Location (relative altitude): %s" %
              self.vehicle.location.global_relative_frame)
        print("Local Location: %s" % self.vehicle.location.local_frame)  # NED
        print("Attitude: %s" % self.vehicle.attitude)
        print("Velocity: %s" % self.vehicle.velocity)
        print("GPS: %s" % self.vehicle.gps_0)
        print("Groundspeed: %s" % self.vehicle.groundspeed)
        print("Airspeed: %s" % self.vehicle.airspeed)
        print("Gimbal status: %s" % self.vehicle.gimbal)
        print("Battery: %s" % self.vehicle.battery)
        print("EKF OK?: %s" % self.vehicle.ekf_ok)
        print("Last Heartbeat: %s" % self.vehicle.last_heartbeat)
        print("Rangefinder: %s" % self.vehicle.rangefinder)
        print("Rangefinder distance: %s" % self.vehicle.rangefinder.distance)
        print("Rangefinder voltage: %s" % self.vehicle.rangefinder.voltage)
        print("Heading: %s" % self.vehicle.heading)
        print("Is Armable?: %s" % self.vehicle.is_armable)
        print("System status: %s" % self.vehicle.system_status.state)
        print("Mode: %s" % self.vehicle.mode.name)  # settable
        print("Armed: %s" % self.vehicle.armed)  # settable

        self.pid = PID(Kp=1.0, Ki=1.0, Kd=1.0)
        self._takeoff = False

    def arm_and_takeoff(self, alt):
        while not self.vehicle.armed:
            self.vehicle.armed = True
            print(" Waiting for arming...")
            sleep(0.5)

        self.vehicle.mode = VehicleMode("STABILIZE")
        print("Taking off!")

        current_altitude = self.vehicle.location.global_relative_frame.alt
        while not self._takeoff:
            print(" Altitude: ", current_altitude)
            if current_altitude < alt:
                out = self.pid.getPID(current_altitude, alt)
                # for smoother takeoff
                if current_altitude >= alt*0.8:
                    out *= 0.85
                self.vehicle.channels.overrides = {'3': out}
            elif current_altitude > alt:
                print(" Altitude reached!")
                self._takeoff = True

    def alt_hold(self):
        self.vehicle.mode = VehicleMode("ALT_HOLD")
        self.vehicle.channels.overrides = {'3': 1500}
        print("Altitude hold!")

    def close(self):
        self.vehicle.close()


if __name__ == '__main__':
    drone = Drone()
    drone.arm_and_takeoff(3.0)
    drone.alt_hold()
    sleep(5)
    drone.vehicle.mode = VehicleMode("LAND")
    drone.close()
    print("Done!")
