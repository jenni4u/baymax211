from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils


#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
LEFT_POSITION_2 = -40
RIGHT_POSITION = 45
RIGHT_POSITION_2 = 40
MOTOR_DPS = 150
TIME_SLEEP = 1.5
COLOR_SENSOR = EV3ColorSensor(3)

#----- COLOR DETECTION OBJECT -----#
color_detection_algorithm = ColorDetectionAlgorithm()

#------------- SETUP -------------#
motor_color_sensor = Motor("A") 
motor_block = Motor("D")  
wait_ready_sensors()
motor_color_sensor.reset_encoder()
motor_block.reset_encoder()


#---------- COLOR CLASSIFICATION ----------#

"""
    Function that stops the movement of the robot's arms once Green or Red has been detected by setting their dps to 0
    It sets the global detected_color variable to the passed color argument
    It sets the boolean stopped_color_detection to True to stop the color sensor from reading values

    Args:
        color (String): The color detected by the sensor (either Green or Red)
"""
def stop_the_arms_movement(color):
    global detected_color, stopped_color_detection

    detected_color = color
    stopped_color_detection = True
    motor_color_sensor.set_dps(0)  # Stop both of robot's arms
    motor_block.set_dps(0)




"""
    Function that continously samples the colors in the room.
    Runs as long as robot's arms have not stopped yet and the color sensor detection has not been stopped yet 
    (i.e. a color was detected or the robot finished scanning the room)

    Returns:
        String: Return the color detected in the room, which is either Green, Red or None
"""
def color_sample():
    global detected_color, stopped_color_detection
    
    # Counts that ensure that at least 5 "red" or "green" have been detected in a row.
    # This ensure the "red" or "green" detected was not an error from the color sensor 
    count_green = 0
    count_red = 0


    while not stopped_color_detection and not stopped_motor_block and not stopped_motor_color_sensor:
        try:

            # Read the values and ensure they are valid numbers
            values = COLOR_SENSOR.get_value()
            if values:

                # Classify the color
                R, G, B, L = values
                color = color_detection_algorithm.classify_the_color(R, G, B)
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
                # Stop the movement 
                if (count_green >=5):
                    color = "green"
                    stop_the_arms_movement(color)
                    sounds_utils.play_wav("balalala.wav")
                else:
                    color = None
  

                # If the counter of Red is equal or higher than 5, the sensor correctly detected the color Red
                # Otherwise, the color is None
                # Stop the movement of the arms
                if (count_red >=5):
                    color = "red"
                    stop_the_arms_movement(color)
                
                else:
                    color = None                  
                
        except SensorError:
            print("Color sensor read error")
        
    return None



#---------- ARMS MOVEMENT ----------#

"""
    Function that moves the arm in a pendulum movement to scan the width of the room.
    Runs only if the color sensor detection has not been stopped yet 
    (i.e. a color was detected or the robot finished scanning the room)

    Args:
        motor (Motor): The robot's arm to move
        left: the limit angle it turns when going to the left
        right: the limit angle it turns when going to the right
"""


def move_motor(motor, left, right): 

    global stopped_color_detection

    print('System is Ready!')

    motor.set_dps(MOTOR_DPS) # Activate the arm (i.e. set its speed)
    time.sleep(0.01)

    # If stopped_color_detection is true, it means a Red or Green was detected, so stop the motor's arm
    if stopped_color_detection:
        motor.set_dps(0)

    # Initially, before tentering the room, the robot's arm is at a position of 0. 
    # To scan the room's width, it needs to scan left, then right    
    elif (motor.get_position()==0):
        motor.set_position(left)
        time.sleep(1)
        motor.set_position(right)
        time.sleep(1)

    # If the arm is at the right of the robot, move it to the left side of the robot    
    elif(motor.get_position() > 0) :
        motor.set_position(left)
        time.sleep(1)

    # If the arm is at the left of the robot, move it to the right side of the robot  
    else :
        motor.set_position(right)
        time.sleep(1)



"""
    Function that moves the color sensor arm to scan the width of the room.
    Once the scanning is done, it should be stopped from moving
"""
def move_motor_pendulum(): 

    global stopped_color_detection, stopped_motor_color_sensor

    move_motor(motor_color_sensor, LEFT_POSITION, RIGHT_POSITION)

    # The scanning is done and no color has been detected, so stop the arm and global variable stopped_motor_color_sensor should be set to True
    motor_color_sensor.set_dps(0)
    stopped_motor_color_sensor = True



"""
    Function that moves the block arm to scan the width of the room.
    Once the scanning is done, it should be stopped from moving

"""
def move_motor_block(): 

    global stopped_color_detection, stopped_motor_block

    print('System is Ready!')
    
    move_motor(motor_color_sensor, LEFT_POSITION_2, RIGHT_POSITION_2)

    motor_block.set_dps(0)
    stopped_motor_block = True   
        



#------------- JOIN THE 3 SYSTEMS -------------#
"""
    Function that runs the sampling of the color sensor, the movement of the color arm and the movement of the block arm at the same time
    Use threading

    Returns:
        String: Return the color detected in the room when the 3 systems stopped running : Red, Green or None
"""
def main_pendulum():

    global detected_color, stopped_color_detection, stopped_motor_block, stopped_motor_color_sensor

    detected_color = None
    stopped_color_detection = False # Boolean that ensures the color sensor can keep reading values
    stopped_motor_block = False # Boolean that verifies that the  block arm is moving
    stopped_motor_color_sensor = False # Boolean that verifies that the color sensor arm is moving

    try:

        color_thread = threading.Thread(target=color_sample)
        move_pendulum_thread = threading.Thread(target=move_motor_pendulum)
        move_block_thread = threading.Thread(target=move_motor_block)

        color_thread.start()
        move_pendulum_thread.start()
        move_block_thread.start()
        
        color_thread.join()      
        move_pendulum_thread.join()
        move_block_thread.join()
        
        print("done")
        return detected_color
    
    except SensorError as error:
        print("error")



#----------- REINITIALIZING MOTORS ---------------#
"""
    Function that resets the position of an arm to initial position

    Args:
        motor (Motor): The robot's arm to set back to position 0
"""
def reset_motor_to_initial_position(motor):
    motor.set_dps(MOTOR_DPS)
    motor.set_position(INITIAL_POSITION)
    # Wait until motor reaches position
    time.sleep(1)
    motor.set_dps(0)


"""
    Function that resets the position of the robot's arms at the same tim to initial position using threading
"""
def reset_both_motors_to_initial_position():
    thread_color_arm = threading.Thread(target=reset_motor_to_initial_position, args=(motor_color_sensor,))
    thread_block_arm = threading.Thread(target=reset_motor_to_initial_position, args=(motor_block,))
    thread_color_arm.start()
    thread_block_arm.start()

    # Wait until both complete
    thread_color_arm.join()
    thread_block_arm.join()


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
    main_pendulum()
