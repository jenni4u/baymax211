from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils as sounds_utils

class PendulumScanner:
    #----------- CONSTANTS -----------#
    INITIAL_POSITION = 0
    # The motor_block moves more than the motor_color_arm so its pendulum movement will be less (from -40 to 40)
    LEFT_POSITION = -45
    LEFT_POSITION_2 = -45
    RIGHT_POSITION = 45
    RIGHT_POSITION_2 = 45

    MOTOR_DPS = 150
    TIME_SLEEP = 1.5

    #------------- CONSTRUCTOR -------------#
    def __init__(self, motor_color_sensor, motor_block, color_sensor):

        """
        Initializes a new instance of the color scanner.

        Args:
            motor_color_sensor: The motor of the color arm.
            motor_block: The motor that contains the cage of the blocks
            color_sensor: The color sensor
        """

        # Motors for the arms
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block

        # Color sensor
        self.COLOR_SENSOR = color_sensor

        # Color classifier
        self.color_detection_algorithm = ColorDetectionAlgorithm()
        self.initial_color = self.motor_color_sensor.get_position()
        self.initial_block = self.motor_block.get_position()

        # Variables for the movement of the arms and detection of sensor
        self.detected_color = None 
        self.stopped_color_detection = False # Boolean that ensures the color sensor can keep reading values
        self.stopped_motor_block = False # Boolean that verifies that the  block arm is moving
        self.stopped_motor_color_sensor = False # Boolean that verifies that the color sensor arm is moving
        
        self.emergency_stop = False



    #---------- COLOR CLASSIFICATION ----------#


    def stop_the_arms_movement(self, color):

        """
        Function that stops the movement of the robot's arms once Green or Red has been detected by setting their dps to 0
        It sets the detected_color variable to the passed color argument
        It sets the boolean stopped_color_detection to True to stop the color sensor from reading values

        Args:
            color (String): The color detected by the sensor (either Green or Red)
        """

        self.detected_color = color
        self.stopped_color_detection = True

        # Stop both of robot's arms
        self.motor_color_sensor.set_dps(0) 
        self.motor_block.set_dps(0)



    def color_sample(self):


        """
        Function that continously samples the colors in the room.
        Runs as long as robot's arms have not stopped yet and the color sensor detection has not been stopped yet 
        (i.e. a color was detected or the robot finished scanning the room)

        Returns:
            String: Return the color detected in the room, which is either Green, Red or None
        """
        
        
        # Counts that ensure that at least 5 "red" or "green" have been detected in a row.
        # This ensure the "red" or "green" detected was not an error from the color sensor 
        count_green = 0
        count_red = 0


        while not self.stopped_color_detection and not self.emergency_stop:
            if self.emergency_stop:
                self.stop_the_arms_movement("emergency")
                return "emergency"

            try:

                # Read the values and ensure they are valid numbers
                values = self.COLOR_SENSOR.get_value()
                if values:

                    # Classify the color
                    R, G, B, L = values
                    color = self.color_detection_algorithm.classify_the_color(R, G, B)

                    #If the color is green, increment the count_green by 1 and set back the count_red to 0
                    if color == "green":
                        count_green+=1
                        print(count_green)
                        count_red = 0
                    #If the color is red, increment the count_red by 1 and set back the count_green to 0
                    elif color == "red":
                        count_red+=1 
                        count_green = 0 
                    # A color different from Green or Red has been detected, so the counters must be set back to 0
                    else:
                        count_green = 0
                        count_red = 0
    

                    # If the counter of Green is equal or higher than 5, the sensor correctly detected the color Green.
                    # Otherwise, the color is None
                    # Stop the movement of the arms and play a music
                    if (count_green >=5):
                        color = "green"
                        self.stop_the_arms_movement(color)
                        sounds_utils.play_wav("balalala.wav")
                    else:
                        color = None
    

                    # If the counter of Red is equal or higher than 5, the sensor correctly detected the color Red
                    # Otherwise, the color is None
                    # Stop the movement of the arms
                    if (count_red >=5):
                        color = "red"
                        self.stop_the_arms_movement(color)
                    
                    else:
                        color = None                  
                    
            except SensorError:
                print("Color sensor read error")
            
        return None



    #---------- ARMS MOVEMENT ----------#
    def get_pos(self, motor):
        if motor == self.motor_color_sensor:
            return self.initial_color
        else:
            return self.initial_block

    
    def move_motor(self, motor, left, right, position):
        """Simple pendulum move without repeated emergency checks"""
        motor.set_dps(self.MOTOR_DPS)
        base_pos = self.initial_color if motor == self.motor_color_sensor else self.initial_block

        if position == "right":
            motor.set_position(base_pos + left)
        else:
            motor.set_position(base_pos + right)

        time.sleep(1)  # allow motor to move
        motor.set_dps(0)

    def move_motor_pendulum(self, position):
        self.move_motor(self.motor_color_sensor, self.LEFT_POSITION, self.RIGHT_POSITION, position)

        # The scanning is done and no color has been detected, so stop the arm and variable stopped_motor_color_sensor should be set to True
        self.motor_color_sensor.set_dps(0)
        self.stopped_motor_color_sensor = True


    def move_motor_block(self, position): 
  
        """
            Function that moves the block arm to scan the width of the room.
            Once the scanning is done, it should be stopped from moving
        """

        print('System is Ready!')
        
        self.move_motor(self.motor_block, self.LEFT_POSITION_2, self.RIGHT_POSITION_2, position)

        self.motor_block.set_dps(0)
        self.stopped_motor_block = True   
            



    #------------- JOIN THE 3 SYSTEMS -------------#

    def main_pendulum(self, position):

        """
        Function that runs the sampling of the color sensor, the movement of the color arm and the movement of the block arm at the same time
        Use threading

        Returns:
            String: Return the color detected in the room when the 3 systems stopped running : Red, Green or None
        """

        # Since the object is called multiple times in Main, reset the variables
        self.detected_color = None
        self.stopped_color_detection = False # Boolean that ensures the color sensor can keep reading values
        self.stopped_motor_block = False # Boolean that verifies that the  block arm is moving
        self.stopped_motor_color_sensor = False # Boolean that verifies that the color sensor arm is moving

        try:
            color_thread = threading.Thread(target=self.color_sample)
            move_pendulum_thread = threading.Thread(target=self.move_motor_pendulum, args=(position,))
            move_block_thread = threading.Thread(target=self.move_motor_block, args=(position,))

        color_thread.start()
        pendulum_thread.start()
        block_thread.start()

        color_thread.join()
        pendulum_thread.join()
        block_thread.join()

        return self.detected_color
