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

        # Variables for the movement of the arms and detection of sensor
        self.detected_color = None 
        self.stopped_color_detection = False # Boolean that ensures the color sensor can keep reading values
        self.stopped_motor_block = False # Boolean that verifies that the  block arm is moving
        self.stopped_motor_color_sensor = False # Boolean that verifies that the color sensor arm is moving




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


        while not self.stopped_color_detection and not self.stopped_motor_block and not self.stopped_motor_color_sensor:
            try:

                # Read the values and ensure they are valid numbers
                values = self.COLOR_SENSOR.get_value()
                if values:

                    # Classify the color
                    R, G, B, L = values
                    color = self.color_detection_algorithm.classify_the_color(R, G, B)
                    print(color)


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

    def move_motor(self, motor, left, right):

            
        """
            Function that moves the arm in a pendulum movement to scan the width of the room.
            Runs only if the color sensor detection has not been stopped yet 
            (i.e. a color was detected or the robot finished scanning the room)

            Args:
                motor (Motor): The robot's arm to move
                left: the limit angle it turns when going to the left
                right: the limit angle it turns when going to the right
        """
    

        print('System is Ready!')

        motor.set_dps(self.MOTOR_DPS) # Activate the arm (i.e. set its speed)
        time.sleep(0.01)
        print(motor.get_position())
        # If stopped_color_detection is true, it means a Red or Green was detected, so stop the motor's arm
        if self.stopped_color_detection:
            motor.set_dps(0)

        # Initially, before entering the room, the robot's arm is at a position of 0. 
        # To scan the room's width, it needs to scan left, then right    
#         elif (motor.get_position()==0):
#             motor.set_position(left)
#             time.sleep(1)
#             motor.set_position(right)
#             time.sleep(1)

        # If the arm is at the right of the robot, move it to the left side of the robot    
        elif(motor.get_position() > 0) :
            motor.set_position(left)
            time.sleep(1)

        # If the arm is at the left of the robot, move it to the right side of the robot  
        else :
            motor.set_position(right)
            time.sleep(1)



    def move_motor_pendulum(self): 

        """
        Function that moves the color sensor arm to scan the width of the room.
        Once the scanning is done, it should be stopped from moving
        """


        self.move_motor(self.motor_color_sensor, self.LEFT_POSITION, self.RIGHT_POSITION)

        # The scanning is done and no color has been detected, so stop the arm and variable stopped_motor_color_sensor should be set to True
        self.motor_color_sensor.set_dps(0)
        self.stopped_motor_color_sensor = True


    def move_motor_block(self): 
  
        """
            Function that moves the block arm to scan the width of the room.
            Once the scanning is done, it should be stopped from moving
        """

        print('System is Ready!')
        
        self.move_motor(self.motor_block, self.LEFT_POSITION_2, self.RIGHT_POSITION_2)

        self.motor_block.set_dps(0)
        self.stopped_motor_block = True   
            



    #------------- JOIN THE 3 SYSTEMS -------------#

    def main_pendulum(self):

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
            move_pendulum_thread = threading.Thread(target=self.move_motor_pendulum)
            move_block_thread = threading.Thread(target=self.move_motor_block)

            color_thread.start()
            move_pendulum_thread.start()
            move_block_thread.start()
            
            color_thread.join()      
            move_pendulum_thread.join()
            move_block_thread.join()
            
            print("done")
            return self.detected_color
        
        except SensorError as error:
            print("error")



    #----------- REINITIALIZING MOTORS ---------------#

    def reset_motor_to_initial_position(self,motor):

        """
        Function that resets the position of an arm to initial position

        Args:
            motor (Motor): The robot's arm to set back to position 0
        """

        motor.set_dps(self.MOTOR_DPS)
        motor.set_position(self.INITIAL_POSITION)
        # Wait until motor reaches position
        time.sleep(1)
        motor.set_dps(0)


    def reset_both_motors_to_initial_position(self):

        """
        Function that resets the position of the robot's arms at the same time to initial position using threading
        """
        
        thread_color_arm = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_color_sensor,))
        thread_block_arm = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_block,))
        thread_color_arm.start()
        thread_block_arm.start()

        # Wait until both complete
        thread_color_arm.join()
        thread_block_arm.join()


#------------- RUNNING MAIN -------------#i
if __name__ == "__main__":
    motor_color_sensor = Motor("A")
    motor_block = Motor("D")
    COLOR_SENSOR = EV3ColorSensor(3) 
    scanner = PendulumScanner(motor_color_sensor, motor_block, COLOR_SENSOR)
    scanner.main_pendulum()