from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils as sounds_utils # Assuming this module handles sound playback

class PendulumScanner:
    #----------- CONSTANTS -----------#
    
    # Motor angle limits for pendulum movement (relative to initial position)
    LEFT_POSITION = -45
    RIGHT_POSITION = 45
    LEFT_POSITION_2 = -45 
    RIGHT_POSITION_2 = 45

    MOTOR_DPS = 150 # Degrees Per Second - speed of the motors
    TIME_SLEEP = 0.01 # Small sleep time for thread stability

    #------------- CONSTRUCTOR -------------#
    def __init__(self, motor_color_sensor, motor_block, color_sensor):
        """
        Initializes a new instance of the color scanner.
        """
        # Motors for the arms
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block

        # Color sensor
        self.COLOR_SENSOR = color_sensor

        # Color classifier
        self.color_detection_algorithm = ColorDetectionAlgorithm()

        # Store initial positions for relative movement calculations
        # These should be read once at startup.
        self.initial_color_pos = self.motor_color_sensor.get_position()
        self.initial_block_pos = self.motor_block.get_position()
        
        # Shared State Variables (Crucial for Inter-Thread Communication)
        self.detected_color = None 
        # Flag set to True by the color thread to signal the motors to stop
        self.stopped_color_detection = False 


    #---------- CONTROL FUNCTIONS ----------#

    def stop_the_arms_movement(self, color):
        """
        Stops the movement of the robot's arms and sets the global stop flag.
        This function is called by the color_sample thread.
        """
        self.detected_color = color
        
        # 1. Set the global flag to True
        self.stopped_color_detection = True

        # 2. Immediately issue non-blocking stop commands
        self.motor_color_sensor.set_dps(0) 
        self.motor_block.set_dps(0)
        
        # Play sound immediately after stopping
        sounds_utils.play_wav("balalala.wav")


    #---------- COLOR CLASSIFICATION THREAD ----------#

    def color_sample(self):
        """
        Function that continuously samples the colors.
        Runs until the global stop flag (self.stopped_color_detection) is set.
        """
        consecutive_count = 0
        last_target_color = None
        
        # Loop runs until the global stop flag is set (by this thread)
        while not self.stopped_color_detection:
            try:
                # Read the values
                values = self.COLOR_SENSOR.get_value()
                if values:
                    # Classify the color
                    R, G, B, L = values
                    color = self.color_detection_algorithm.classify_the_color(R, G, B)
                    print(f"Detected: {color}, Consecutive: {consecutive_count}")

                    # Check for target colors (green or red)
                    if color == "green" or color == "red":
                        # If the color is the same as the last target color, increment
                        if color == last_target_color:
                            consecutive_count += 1
                        # If it's a new target color (or the first one), reset count to 1
                        else:
                            consecutive_count = 1
                            last_target_color = color
                    else:
                        # Non-target color detected, reset the sequence
                        consecutive_count = 0
                        last_target_color = None

                    # STOPPING CONDITION
                    if consecutive_count >= 5:
                        self.stop_the_arms_movement(last_target_color)
                        # Once stopped, return to end the thread
                        return self.detected_color

                time.sleep(self.TIME_SLEEP) 

            except SensorError:
                print("Color sensor read error")
                time.sleep(0.1) 
        
        return self.detected_color


    #---------- ARMS MOVEMENT THREADS ----------#

    def _run_pendulum_movement(self, motor, left_limit, right_limit):
        """
        Core logic for continuous pendulum movement using non-blocking set_dps.
        It runs until the stop flag is set by the color thread.
        """
        
        # Determine the correct initial position for relative limit checks
        if motor == self.motor_color_sensor:
            initial_pos = self.initial_color_pos
        else:
            initial_pos = self.initial_block_pos
        
        # Start moving in one direction
        motor.set_dps(self.MOTOR_DPS) 
        print(f"{motor} started movement.")
        
        # Loop runs until the shared state flag is set
        while not self.stopped_color_detection:
            
            current_pos = motor.get_position()
            
            # Check if we hit the right limit
            if current_pos >= initial_pos + right_limit:
                motor.set_dps(-self.MOTOR_DPS) # Reverse to left
                
            # Check if we hit the left limit
            elif current_pos <= initial_pos + left_limit:
                motor.set_dps(self.MOTOR_DPS) # Reverse to right
            
            time.sleep(self.TIME_SLEEP) # Keep this short for responsiveness
            
        # Motor thread ends, ensure motor is stopped (if not already done by stop_the_arms_movement)
        motor.set_dps(0)


    def move_motor_pendulum(self): 
        """Dedicated thread target for the color sensor arm movement."""
        self._run_pendulum_movement(self.motor_color_sensor, self.LEFT_POSITION, self.RIGHT_POSITION)

    def move_motor_block(self): 
        """Dedicated thread target for the block arm movement."""
        self._run_pendulum_movement(self.motor_block, self.LEFT_POSITION_2, self.RIGHT_POSITION_2)
            
    
    #------------- JOIN THE 3 SYSTEMS -------------#

    def main_pendulum(self):
        """
        Function that runs the sampling of the color sensor and the movement
        of both arms simultaneously using threading.
        """
        # Reset all shared state variables before starting a new scan
        self.detected_color = None
        self.stopped_color_detection = False 
        
        print('System is Ready! Starting scan...')
        
        try:
            # Setup threads
            color_thread = threading.Thread(target=self.color_sample)
            move_pendulum_thread = threading.Thread(target=self.move_motor_pendulum)
            move_block_thread = threading.Thread(target=self.move_motor_block)

            # Start threads
            color_thread.start()
            move_pendulum_thread.start()
            move_block_thread.start()
            
            # Wait for all threads to complete (they exit when the stop flag is set)
            color_thread.join()      
            move_pendulum_thread.join()
            move_block_thread.join()
            
            print("Scan complete.")
            return self.detected_color
        
        except Exception as error: 
            print(f"An unexpected error occurred: {error}")
            # Ensure motors are stopped on error
            self.motor_color_sensor.set_dps(0) 
            self.motor_block.set_dps(0)
            return None


    #----------- REINITIALIZING MOTORS ---------------#
    
    # NOTE: The reset functions are kept simple, using blocking commands is generally 
    # acceptable here since they are run AFTER the main threads have JOINED and stopped.

    def reset_motor_to_initial_position(self, motor):
        """Function that resets the position of an arm to initial position (0)."""
        
        motor.set_dps(self.MOTOR_DPS)
        # Use run_to_position if available and blocking is acceptable here, 
        # or set_position(0) if the library supports it as a blocking move.
        # Assuming set_position is a non-blocking request for movement to 0
        motor.set_position(0) 
        
        # Wait for the motor to reach position (using time.sleep is a rough estimate)
        time.sleep(1) 

        motor.set_dps(0)


    def reset_both_motors_to_initial_position(self):
        """
        Function that resets the position of the robot's arms at the same time to initial position using threading.
        """
        thread_color_arm = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_color_sensor,))
        thread_block_arm = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_block,))
        
        thread_color_arm.start()
        thread_block_arm.start()

        # Wait until both complete
        thread_color_arm.join()
        thread_block_arm.join()