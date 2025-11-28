from utils.brick import EV3ColorSensor, Motor, BP, SensorError, TouchSensor # Added TouchSensor
import math
import time
import threading # Crucial for non-blocking movement and monitoring
# from pendulum_mvt import PendulumScanner # Assuming Part 1 is imported
# from color_detection_algorithm import ColorDetectionAlgorithm 

class RobotScannerOfRoom:
    #-------- MOVEMENT PARAMETERS -----------#
    RADIUS = 2 
    DISTTODEG = 360 / (2 * math.pi * RADIUS) 

    #-------- CONSTANTS -----------#
    DPS = 50 
    MAX_ROOM_DISTANCE = 22 
    DISTANCE_PER_SCANNING = 2.8/2 
    DISTANCE_ENTER = 9 
    ORANGE_STOP_THRESHOLD = 5 # 5 in a row to stop at orange door

    #------------- CONSTRUCTOR & STATE -------------#
    def __init__(self, motor_color_sensor, motor_block, color_sensor, RIGHT_WHEEL, LEFT_WHEEL):
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block
        self.LEFT_WHEEL = LEFT_WHEEL
        self.RIGHT_WHEEL = RIGHT_WHEEL
        self.COLOR_SENSOR = color_sensor

        self.scanner = PendulumScanner(motor_color_sensor,motor_block,color_sensor)
        self.color_detection_algorithm = ColorDetectionAlgorithm()
        
        # Shared State Flags (accessible by external monitor)
        self.emergency_stop = False
        self.orange_stop_detected = False

    #-------- MOVE THE ROBOT ------------#

    def stop(self):
        """Immediately stops both wheel motors."""
        self.RIGHT_WHEEL.set_dps(0)
        self.LEFT_WHEEL.set_dps(0)
        
    def trigger_emergency_stop(self):
        """Sets the global emergency flag and stops all motors (wheels and arms)."""
        print("!!! GLOBAL EMERGENCY STOP ACTIVATED !!!")
        self.emergency_stop = True
        self.stop() # Stop wheels
        self.scanner.trigger_emergency_stop() # Stop arms (sets their internal flag too)

    def get_detected_color(self):
        """Reads and classifies the color from the sensor."""
        values = self.COLOR_SENSOR.get_value()
        if values:
            R, G, B, L = values
            return self.color_detection_algorithm.classify_the_color(R, G, B)
        return None
    
    # 5-ORANGE MONITORING THREAD LOGIC
    def monitor_orange_stop(self):
        """Runs in a separate thread to check for 5 consecutive orange readings."""
        consecutive_count = 0
        
        while not self.orange_stop_detected and not self.emergency_stop:
            try:
                color = self.get_detected_color()
                
                if color == "orange":
                    consecutive_count += 1
                else:
                    consecutive_count = 0
                
                if consecutive_count >= self.ORANGE_STOP_THRESHOLD:
                    self.orange_stop_detected = True
                    self.stop()
                    return

            except SensorError:
                time.sleep(0.05)
            
            time.sleep(0.01)

    def move_robot_orange_door(self, dps):
        """Backs the robot up until 5 orange colors are detected."""
        self.orange_stop_detected = False

        monitor_thread = threading.Thread(target=self.monitor_orange_stop)
        monitor_thread.start()

        # Start backing up (dps is negative for backwards)
        self.RIGHT_WHEEL.set_dps(-abs(dps))
        self.LEFT_WHEEL.set_dps(-abs(dps))

        monitor_thread.join() 
        
        if self.emergency_stop:
            print("Orange door movement interrupted by Emergency Stop.")
        else:
            print("Movement stopped at Orange Door.")

    # CONTINUOUS MOVEMENT LOGIC
    def _move_robot_continuous(self, distance_cm, dps):
        """Moves the robot non-blockingly until the distance is reached or a stop flag is set."""
        target_degrees = distance_cm * self.DISTTODEG
        start_pos = self.RIGHT_WHEEL.get_position()
        target_pos = start_pos + target_degrees
        
        speed = abs(dps) if distance_cm > 0 else -abs(dps)
        
        self.RIGHT_WHEEL.set_dps(speed)
        self.LEFT_WHEEL.set_dps(speed)
        
        while not self.emergency_stop:
            current_pos = self.RIGHT_WHEEL.get_position()
            
            if (distance_cm > 0 and current_pos >= target_pos) or \
               (distance_cm < 0 and current_pos <= target_pos):
                self.stop()
                return True # Movement completed

            time.sleep(self.TIME_SLEEP)
            
        self.stop()
        return False # Movement interrupted

    def move_robot(self, distance_cm, dps):
        """Wrapper to execute and wait for continuous movement."""
        move_thread = threading.Thread(target=self._move_robot_continuous, 
                                       args=(distance_cm, dps))
        move_thread.start()
        move_thread.join()
        
        # Check if the movement was interrupted by emergency stop
        if self.emergency_stop:
            # Note: Wheels are already stopped inside _move_robot_continuous
            return

    # MISSION CONTROL FUNCTIONS
    def move_back_after_scanning(self, total_distance):
        
        self.stop()
        
        self.scanner.reset_both_motors_to_initial_position()
        time.sleep(1)

        # Move back the robot to its entrance position
        distance_to_travel = -(total_distance + self.DISTANCE_PER_SCANNING - self.DISTANCE_ENTER)
        self.move_robot(distance_to_travel, 300)

    def package_delivery(self,total_distance, delivery_counter):
        
        # ... (delivery logic is complex and relies on blocking set_position, 
        # but the emergency check is built into the PendulumScanner methods) ...

        # Note: All original set_position calls here are blocking and assume the 
        # threads have already been stopped by a red/green detection.

        angle_movement = 27 if delivery_counter == 0 else 50
        initial_color_angle = self.scanner.motor_color_sensor.get_position()
        drop_angle = initial_color_angle + angle_movement if initial_color_angle < 0 else initial_color_angle - angle_movement

        self.scanner.motor_color_sensor.set_dps(self.scanner.MOTOR_DPS - 100)
        self.scanner.motor_color_sensor.set_position(drop_angle) 
        time.sleep(2.5)     
        self.scanner.motor_color_sensor.set_dps(0)

        self.scanner.motor_color_sensor.set_dps(self.scanner.MOTOR_DPS - 100)
        self.scanner.motor_color_sensor.set_position(initial_color_angle)
        time.sleep(1.5)
        self.scanner.motor_color_sensor.set_dps(0)

        self.scanner.reset_both_motors_to_initial_position()
        time.sleep(1)

        # Move robot the remaining distance back toward where the robot entered
        # This logic is complex and handles two cases, ensuring move_robot is called
        remaining = abs(self.DISTANCE_ENTER - (total_distance + self.DISTANCE_PER_SCANNING))
        distance_to_move = remaining if total_distance < self.DISTANCE_ENTER else -remaining
        self.move_robot(distance_to_move, 150)
        time.sleep(1)

    def scan_room(self, delivery_counter):
        
        total_distance = 0
        self.stop()
        self.LEFT_WHEEL.set_position_relative(0)
        self.RIGHT_WHEEL.set_position_relative(0)
        time.sleep(0.05)
        position = "left"
        
        try:
            # 1. Back up to orange door, stop on 5 orange in a row
            self.move_robot_orange_door(200)
            if self.emergency_stop: return False
            time.sleep(0.5)
            
            while True and not self.emergency_stop:
                
                if total_distance >= self.MAX_ROOM_DISTANCE:
                    self.move_back_after_scanning(total_distance)
                    return False

                # 2. Advance by DISTANCE_PER_SCANNING
                self.move_robot(self.DISTANCE_PER_SCANNING, 150)
                if self.emergency_stop: return False
                
                total_distance += self.DISTANCE_PER_SCANNING
                
                # 3. Perform pendulum scan
                color = self.scanner.main_pendulum()
                
                # Flip scan position for next iteration
                position = "right" if position == "left" else "left"
                
                # 4. Handle Red or Green detection
                if color == "red":
                    # Red detected -> Stop, reset arms, retreat a fixed amount
                    self.stop()
                    self.scanner.reset_both_motors_to_initial_position()
                    
                    # Retreat distance needs recalculation:
                    # Move robot back to entrance (DISTANCE_ENTER) minus distance already traveled
                    # The value DISTANCE_PER_SCANNING*3 seems to be a hardcoded retreat distance.
                    # We will simply retreat to the entrance for a clean exit.
                    
                    self.move_robot(-total_distance + self.DISTANCE_ENTER, 150) 
                    return False

                elif color == "green":
                    # Green detected -> Stop, deliver package, return
                    self.stop()
                    self.package_delivery(total_distance, delivery_counter)
                    
                    return True 

        except BaseException as error:
            print("Error during scan_room:", error)
            BP.reset_all() 
            return False

#------------- RUNNING MAIN -------------#
# This is the external main logic to set up the emergency stop thread.
if __name__ == "__main__":
    # Assuming ports are correct
    motor_color_sensor = Motor("A")
    motor_block = Motor("D")
    COLOR_SENSOR = EV3ColorSensor(3) 
    LEFT_WHEEL = Motor("B")
    RIGHT_WHEEL = Motor("C")

    # Initialize robot and global reference for the monitor thread
    scanner_of_room = RobotScannerOfRoom(motor_color_sensor, motor_block, COLOR_SENSOR, RIGHT_WHEEL, LEFT_WHEEL)
    TOUCH_SENSOR = TouchSensor(4) # Assuming port 4 for the touch sensor

    # Monitor function (external to the class)
    def touch_sensor_monitor(scanner):
        while not scanner.emergency_stop:
            try:
                if TOUCH_SENSOR.is_pressed(): 
                    scanner.trigger_emergency_stop()
                    break 
            except SensorError:
                time.sleep(0.05)
            time.sleep(0.05)
            
    try:
        # Start the Touch Sensor monitoring thread
        monitor_thread = threading.Thread(target=touch_sensor_monitor, args=(scanner_of_room,))
        monitor_thread.start()
        print("Touch sensor monitor started.")

        # Run the mission
        block_dropped = scanner_of_room.scan_room(0)
        print(f"Mission finished. Block dropped: {block_dropped}")
        
        # Wait for monitor thread to clean up
        monitor_thread.join()

    except Exception as e:
        print(f"Main execution error: {e}")
    finally:
        BP.reset_all()