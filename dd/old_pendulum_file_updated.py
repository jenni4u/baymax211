from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, TouchSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils


#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 150
TIME_SLEEP = 1.5

#------------- SETUP -------------#
scanner_motor = Motor("A") # color sensor arm
drop_motor = Motor("D")  # block arm
color_sensor = EV3ColorSensor(3)
touch_sensor = TouchSensor(4)
wait_ready_sensors()
scanner_motor.reset_encoder()
drop_motor.reset_encoder()


#------- COLOR CLASSIFICATION -------------#
color_detection_algorithm = ColorDetectionAlgorithm()


#------------- GLOBAL VARIABLES -------------#
emergency_stop = False
stopped_drop_motor = False
stopped_scanner_motor = False
stopped_color_detection = False


#----------------------- STOP LOGIC -------------------------#

def stop_the_arms_movement(color):
    """
    Function that stops the movement of the robot's arms once Green or Red has been detected by setting their dps to 0
    It sets the global detected_color variable to the passed color argument
    It sets the boolean stopped_color_detection to True to stop the color sensor from reading values

    Args:
        color (String): The color detected by the sensor (either Green or Red)
    """
    global detected_color, stopped_color_detection

    detected_color = color
    stopped_color_detection = True


    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)


def emergency_stop_arms():
    """
    Function that stops the movement of the robot's arms in case of an emergency stop by setting their dps to 0
    It sets the global emergency_stop variable to True
    Used in emergency_stop_monitor function of the top_level_main, that detects when touch sensor is pressed

    Args:
        color (String): The color detected by the sensor (either Green or Red)
    """
    global emergency_stop
    emergency_stop = True
    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)


#----------------- COLOR CLASSIFICATION --------------------------#

def color_sample():
    """
    Function that continously samples the colors in the room.
    Runs as long as robot's arms have not stopped yet, the emergency stop has not been activated yet
    and the color sensor detection has not been stopped yet
    (i.e. a color was detected or the robot finished scanning the room)

    Returns:
        String: Return the color detected in the room, which is either Green, Red or None
    """
    global detected_color, stopped_color_detection

    # Counts that ensure that at least 5 "red" or "green" have been detected in a row.
    # This ensure the "red" or "green" detected was not an error from the color sensor 
    count_green = 0
    count_red = 0

    while (not emergency_stop and not stopped_color_detection and not stopped_drop_motor and not stopped_scanner_motor):
        
        # Stop the movement of the arms if emergency_stop True 
        if emergency_stop:
            scanner_motor.set_dps(0)
            drop_motor.set_dps(0)
            return None

        try:
            # Read the values and ensure they are valid numbers
            values = color_sensor.get_value()
            if values:

                # Classify the color
                R, G, B, L = values
                color = color_detection_algorithm.classify_the_color(R, G, B)
                print(color)

                # If the color is green, increment the count_green by 1 and set back the count_red to 0
                if color == "green":
                    count_green += 1
                    count_red = 0
                # If the color is red, increment the count_red by 1 and set back the count_green to 0
                elif color == "red":
                    count_red += 1
                    count_green = 0
                # A color different from Green or Red has been detected, so the counters must be set back to 0
                else:
                    count_green = 0
                    count_red = 0


                # If the counter of Green is equal or higher than 5, the sensor correctly detected the color Green.
                # Otherwise, the color is None
                # Stop the movement
                if count_green >= 5:
                    color="green"
                    stop_the_arms_movement(color)
                    sounds_utils.play_wav("balalala.wav")
                else:
                    color = None

                # If the counter of Red is equal or higher than 5, the sensor correctly detected the color Red
                # Otherwise, the color is None
                # Stop the movement of the arms
                if count_red >= 5:
                    color = "red"
                    stop_the_arms_movement(color)
                else:
                    color = None

        except SensorError:
            print("Color sensor read error")

    return None


#---------- ARMS MOVEMENT ----------#
def move_motor(motor, position):
    """
    Function that moves the arm in a pendulum movement to scan the width of the room.
    Runs only if the color sensor detection has not been stopped yet (stopped_color_detection = False) and the emergency_stop Boolean has not been activated

    Args:
        motor (Motor): The robot's arm to move
        position (String) : The current position the arms are, either left or right
    """
    global stopped_color_detection, emergency_stop

    print("System is Ready!")

    # If stopped_color_detection is true, it means a Red or Green was detected, so stop the motor's arm
    # If emergency_stop is true, it means the touch sensor was pressed, so stop the motor's arm
    if emergency_stop or stopped_color_detection:
        motor.set_dps(0)
        return

    # Activate the arm (i.e. set its speed)
    motor.set_dps(MOTOR_DPS)
    time.sleep(0.01)

    # If emergency_stop is true, it means the touch sensor was pressed, so stop the motor's arm
    if emergency_stop:
        motor.set_dps(0)
        return

    # If the motor is at the right position, it must move left   
    if position == "right": 
        motor.set_position(LEFT_POSITION)
        
        # This is an equivalent of a time.sleep(1)
        # However, this verifies every milisecond for 1 second that a color and an emergency_stop have not been detected yet
        # Otherwise, stop the motor's movement
        for _ in range(100):
                if stopped_color_detection or emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)


    # If the motor is at the left position, it must move right  
    if position == "left":  
        motor.set_position(RIGHT_POSITION)
        
        # This is an equivalent of a time.sleep(1)
        # However, this verifies every milisecond for 1 second that a color and an emergency_stop have not been detected yet
        # Otherwise, stop the motor's movement
        for _ in range(100):
                if stopped_color_detection or emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)
    
    


#============================================================
# PENDULUM ARM
#============================================================
def move_motor_pendulum(position):
    global stopped_scanner_motor

    if emergency_stop:
        scanner_motor.set_dps(0)
        return

    move_motor(scanner_motor, position)

    scanner_motor.set_dps(0)
    stopped_scanner_motor = True


#============================================================
# BLOCK ARM
#============================================================
def move_drop_motor(position):
    global stopped_drop_motor

    if emergency_stop:
        drop_motor.set_dps(0)
        return

    move_motor(drop_motor, position)

    drop_motor.set_dps(0)
    stopped_drop_motor = True


#============================================================
# RUN ALL THREADS TOGETHER
#============================================================
def main_pendulum(position):
    global detected_color, emergency_stop
    global stopped_color_detection, stopped_drop_motor, stopped_scanner_motor

    detected_color = None
    stopped_color_detection = False
    stopped_drop_motor = False
    stopped_scanner_motor = False
    emergency_stop = False

    try:
        color_thread = threading.Thread(target=color_sample)
        pendulum_thread = threading.Thread(target=move_motor_pendulum, args=(position,))
        block_thread = threading.Thread(target=move_drop_motor, args=(position,))

        color_thread.start()
        pendulum_thread.start()
        block_thread.start()

        color_thread.join()
        pendulum_thread.join()
        block_thread.join()

        print("done")
        return detected_color

    except SensorError:
        print("error")


#============================================================
# RESET MOTORS (INTERRUPTIBLE)
#============================================================
def reset_motor_to_initial_position(motor):
    global emergency_stop

    if emergency_stop:
        motor.set_dps(0)
        return

    motor.set_dps(50)
    motor.set_position(INITIAL_POSITION)

    # INTERRUPTIBLE wait
    for _ in range(100):
        if stopped_color_detection or emergency_stop:
            motor.set_dps(0)
            return
        time.sleep(0.01)
                
 

    motor.set_dps(0)


def reset_both_motors_to_initial_position():
    global emergency_stop

    if emergency_stop:
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        return

    t1 = threading.Thread(target=reset_motor_to_initial_position, args=(scanner_motor,))
    t2 = threading.Thread(target=reset_motor_to_initial_position, args=(drop_motor,))

    t1.start()
    t2.start()

    # INTERRUPTIBLE wait for both
    while t1.is_alive() or t2.is_alive():
        if emergency_stop:
            scanner_motor.set_dps(0)
            drop_motor.set_dps(0)
            return
        time.sleep(0.01)

    t1.join()
    t2.join()


#============================================================
if __name__ == "__main__":
    main_pendulum("left")
