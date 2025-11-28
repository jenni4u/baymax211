from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, SensorError, TouchSensor
import threading
import time
# Assuming these are available in your environment:
# from color_detection_algorithm import ColorDetectionAlgorithm 
# import sounds_utils as sounds_utils 

# --- Placeholder/Mock Classes for Demonstration ---
# NOTE: In a real environment, you must import the actual classes.
class ColorDetectionAlgorithm:
    def classify_the_color(self, R, G, B):
        # Mock classification logic
        if R > 100 and G < 50: return "red"
        if G > 100 and R < 50: return "green"
        return "other"
class MockMotor:
    def __init__(self, port): self.position = 0; self.dps = 0; self.port = port
    def get_position(self): return self.position
    def set_dps(self, dps): self.dps = dps
    def set_position(self, pos): self.position = pos # Blocking is okay here for reset
class MockSensor:
    def get_value(self):
        # Mock R, G, B, L values
        return (120, 40, 30, 80)
class MockSounds:
    def play_wav(self, file): print(f"Playing sound: {file}")
sounds_utils = MockSounds()
# --- End of Placeholders ---

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
        
        # Motors for the arms
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block

        # Color sensor
        self.COLOR_SENSOR = color_sensor

        # Color classifier
        self.color_detection_algorithm = ColorDetectionAlgorithm()

        # Store initial positions for relative movement calculations
        self.initial_color_pos = self.motor_color_sensor.get_position()
        self.initial_block_pos = self.motor_block.get_position()
        
        # Shared State Flags (Crucial for Inter-Thread Communication)
        self.detected_color = None 
        self.stopped_color_detection = False # Set by color thread on 5-in-a-row
        self.emergency_stop = False         # Set by external touch sensor thread

    #---------- CONTROL FUNCTIONS ----------#

    def stop_the_arms_movement(self, color):
        """
        Stops the movement upon color sequence detection.
        Called ONLY by the color_sample thread.
        """
        self.detected_color = color
        self.stopped_color_detection = True

        # Immediately issue non-blocking stop commands
        self.motor_color_sensor.set_dps(0) 
        self.motor_block.set_dps(0)
        
        sounds_utils.play_wav("balalala.wav")
        
    def trigger_emergency_stop(self):
        """
        Stops the movement upon external emergency signal (Touch Sensor).
        Called ONLY by the external monitor thread.
        """
        print("!!! EMERGENCY STOP TRIGGERED !!!")
        self.emergency_stop = True
        
        # Immediately issue non-blocking stop commands
        self.motor_color_sensor.set_dps(0) 
        self.motor_block.set_dps(0)


    #---------- COLOR CLASSIFICATION THREAD ----------#

    def color_sample(self):
        """
        Continuously samples colors and checks for the 5-in-a-row stop condition.
        """
        consecutive_count = 0
        last_target_color = None
        
        # Loop runs until either stop flag is set
        while not self.stopped_color_detection and not self.emergency_stop: 
            try:
                values = self.COLOR_SENSOR.get_value()
                if values:
                    R, G, B, L = values
                    color = self.color_detection_algorithm.classify_the_color(R, G, B)
                    
                    if color == "green" or color == "red":
                        if color == last_target_color:
                            consecutive_count += 1
                        else:
                            consecutive_count = 1
                            last_target_color = color
                    else:
                        consecutive_count = 0
                        last_target_color = None

                    # STOPPING CONDITION
                    if consecutive_count >= 5:
                        self.stop_the_arms_movement(last_target_color)
                        return self.detected_color

                time.sleep(self.TIME_SLEEP) 

            except SensorError:
                print("Color sensor read error")
                time.sleep(0.1) 
        
        return self.detected_color

    #---------- ARMS MOVEMENT THREADS ----------#
    
    def _run_pendulum_movement(self, motor, left_limit, right_limit):
        """
        Core non-blocking logic for continuous pendulum movement.
        """
        
        # Determine the correct initial position for relative limit checks
        if motor == self.motor_color_sensor:
            initial_pos = self.initial_color_pos
        else:
            initial_pos = self.initial_block_pos
        
        motor.set_dps(self.MOTOR_DPS) # Start moving right
        
        # Loop runs until either stop flag is set
        while not self.stopped_color_detection and not self.emergency_stop:
            
            current_pos = motor.get_position()
            
            # Check if we hit the right limit
            if current_pos >= initial_pos + right_limit:
                motor.set_dps(-self.MOTOR_DPS) # Reverse to left
                
            # Check if we hit the left limit
            elif current_pos <= initial_pos + left_limit:
                motor.set_dps(self.MOTOR_DPS) # Reverse to right
            
            time.sleep(self.TIME_SLEEP) 
            
        # Ensure motor is stopped after exiting the loop
        motor.set_dps(0)


    def move_motor_pendulum(self): 
        """Dedicated thread target for the color sensor arm movement."""
        self._run_pendulum_movement(self.motor_color_sensor, self.LEFT_POSITION, self.RIGHT_POSITION)

    def move_motor_block(self): 
        """Dedicated thread target for the block arm movement."""
        self._run_pendulum_movement(self.motor_block, self.LEFT_POSITION_2, self.RIGHT_POSITION_2)
            
    
    #------------- MAIN EXECUTION FLOW -------------#

    def main_pendulum(self):
        """
        Runs the sampling and arm movements simultaneously.
        """
        # Reset all shared state variables before starting a new scan
        self.detected_color = None
        self.stopped_color_detection = False 
        self.emergency_stop = False # Must be reset here for subsequent runs
        
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
            
            # Wait for all threads to complete (they exit when a stop flag is set)
            color_thread.join()      
            move_pendulum_thread.join()
            move_block_thread.join()
            
            print("Scan complete.")
            return self.detected_color
        
        except Exception as error: 
            print(f"An unexpected error occurred: {error}")
            self.motor_color_sensor.set_dps(0) 
            self.motor_block.set_dps(0)
            return None


    #----------- REINITIALIZING MOTORS ---------------#
    
    def reset_motor_to_initial_position(self, motor):
        """Function that resets the position of an arm to initial position (0)."""
        motor.set_dps(self.MOTOR_DPS)
        motor.set_position(0) 
        time.sleep(1) 
        motor.set_dps(0)

    def reset_both_motors_to_initial_position(self):
        """Resets both arms simultaneously."""
        thread_color_arm = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_color_sensor,))
        thread_block_arm = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_block,))
        
        thread_color_arm.start()
        thread_block_arm.start()
        thread_color_arm.join()
        thread_block_arm.join()