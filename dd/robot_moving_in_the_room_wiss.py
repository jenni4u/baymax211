from utils.brick import EV3ColorSensor, TouchSensor, Motor, BP, wait_ready_sensors
import math
import time
from pendulum_mvt_wiss import PendulumScanner
import threading

class RobotScannerOfRoom:
    RADIUS = 2
    DISTTODEG = 360 / (2 * math.pi * RADIUS)
    DPS = 50
    MAX_ROOM_DISTANCE = 22
    DISTANCE_PER_SCANNING = 2.8 / 2
    DISTANCE_ENTER = 9

    def __init__(self, motor_color_sensor, motor_block, color_sensor, RIGHT_WHEEL, LEFT_WHEEL):
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block
        self.LEFT_WHEEL = LEFT_WHEEL
        self.RIGHT_WHEEL = RIGHT_WHEEL
        self.COLOR_SENSOR = color_sensor

        self.scanner = PendulumScanner(motor_color_sensor, motor_block, color_sensor)

        motor_block.reset_encoder()
        motor_color_sensor.reset_encoder()
        LEFT_WHEEL.reset_encoder()
        RIGHT_WHEEL.reset_encoder()

        self.emergency_stop = False

    # ----- CENTRAL EMERGENCY STOP -----
    def stop_all_motors(self):
        """Stop both wheels and both arms immediately"""
        self.scanner.emergency_stop = True
        self.scanner.stop_the_arms_movement
        self.emergency_stop = True
        self.LEFT_WHEEL.set_dps(0)
        self.RIGHT_WHEEL.set_dps(0)
        self.motor_color_sensor.set_dps(0)
        self.motor_block.set_dps(0)

    # ----- ROBOT MOVEMENT -----
    def move_robot(self, distance, dps):
        self.RIGHT_WHEEL.set_dps(dps)
        self.LEFT_WHEEL.set_dps(dps)

        self.LEFT_WHEEL.set_position_relative(-distance * self.DISTTODEG)
        self.RIGHT_WHEEL.set_position_relative(-distance * self.DISTTODEG)

        # Wait until wheels finish moving
        time.sleep(abs(distance) / 10)  # rough approximation

        # Immediately stop if emergency triggered
        if self.emergency_stop:
            self.stop_all_motors()

    def move_back_after_scanning(self, total_distance):
        self.stop_all_motors()

        # Reset both arms to initial position
        self.scanner.reset_both_motors_to_initial_position()
        time.sleep(1)

        # Move robot back
        self.move_robot(-(total_distance + self.DISTANCE_PER_SCANNING - self.DISTANCE_ENTER), 250)
        time.sleep(1)

    # ----- PACKAGE DELIVERY -----
    def package_delivery(self, total_distance, delivery_counter):
        self.stop_all_motors()

        # Move color arm to drop position
        initial_angle = self.scanner.motor_color_sensor.get_position()
        angle_movement = 30 if delivery_counter == 0 else 50
        drop_angle = initial_angle + angle_movement if initial_angle < 0 else initial_angle - angle_movement

        self.scanner.motor_color_sensor.set_dps(50)
        self.scanner.motor_color_sensor.set_position(drop_angle)
        time.sleep(2.5)
        self.scanner.motor_color_sensor.set_dps(0)

        # Return arm to initial angle
        self.scanner.motor_color_sensor.set_dps(50)
        self.scanner.motor_color_sensor.set_position(initial_angle)
        time.sleep(1.5)
        self.scanner.motor_color_sensor.set_dps(0)

        # Reset both arms
        self.scanner.reset_both_motors_to_initial_position()
        time.sleep(1)

    # ----- SCAN ROOM -----
    def scan_room(self, delivery_counter):
        total_distance = 0
        position = "left"

        try:
            # --- BACKUP UNTIL ORANGE DETECTED 5 TIMES ---
            count_orange = 0
            self.RIGHT_WHEEL.set_dps(150)  # move backward
            self.LEFT_WHEEL.set_dps(150)

            while count_orange < 5 and not self.emergency_stop:
                try:
                    R, G, B, L = self.COLOR_SENSOR.get_value()
                    color = self.scanner.color_detection_algorithm.classify_the_color(R, G, B)
                    if color == "orange":
                        count_orange += 1
                    else:
                        count_orange = 0
                except Exception:
                    pass
                time.sleep(0.05)

            # Stop wheels once orange detected 5 times
            self.RIGHT_WHEEL.set_dps(0)
            self.LEFT_WHEEL.set_dps(0)

            # --- PROCEED WITH ROOM SCANNING ---
            while True:
                if total_distance >= self.MAX_ROOM_DISTANCE or self.emergency_stop:
                    self.move_back_after_scanning(total_distance)
                    return False

                # Move forward by scanning increment
                self.move_robot(self.DISTANCE_PER_SCANNING, 150)
                total_distance += self.DISTANCE_PER_SCANNING
                time.sleep(1.5)

                # Scan width
                color = self.scanner.main_pendulum(position)
                position = "right" if position == "left" else "left"

                if color == "red" or self.emergency_stop:
                    self.stop_all_motors()
                    self.scanner.reset_both_motors_to_initial_position()
                    self.move_robot(self.DISTANCE_ENTER - self.DISTANCE_PER_SCANNING*3, 150)
                    return False

                elif color == "green":
                    self.stop_all_motors()
                    self.package_delivery(total_distance, delivery_counter)
                    total_distance = 0
                    position = "left"
                    return True

        except BaseException as e:
            print("Error during scan_room:", e)
            BP.reset_all()

#------------- RUNNING MAIN -------------# 
touch_sensor = TouchSensor(4)
motor_color_sensor = Motor("A") 
motor_block = Motor("D") 
COLOR_SENSOR = EV3ColorSensor(3) 
LEFT_WHEEL = Motor("B") 
RIGHT_WHEEL = Motor("C") 
scanner = RobotScannerOfRoom( motor_color_sensor, motor_block, COLOR_SENSOR, RIGHT_WHEEL, LEFT_WHEEL)
wait_ready_sensors()

def emergency_stop_monitor():
    """Monitor touch sensor for emergency stop signal."""
    print("Emergency stop monitor started. Press touch sensor to stop.")
    while True:
        
        if touch_sensor.is_pressed():
            print("\n*** EMERGENCY STOP ACTIVATED ***")
            
            scanner.emergency_stop = True
            scanner.stop_all_motors("emergency")
            
            BP.reset_all()
            reset_brick()
            break
        time.sleep(0.05)  # Check every 50ms
        
if __name__ == "__main__": 
    stop_thread = threading.Thread(target=emergency_stop_monitor, daemon=True)
    stop_thread.start()
    scanner.scan_room(1)