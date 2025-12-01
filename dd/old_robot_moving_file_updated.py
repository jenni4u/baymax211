from utils.brick import Motor, BP, wait_ready_sensors, TouchSensor, reset_brick
import math
import time
import old_pendulum_file_updated as pendulum_mvt
import threading

#-------- MOVEMENT PARAMETERS -----------#
RADIUS = 2 #radius of wheel in cm
DISTTODEG = 360 / (2 * math.pi * RADIUS) # Conversion factor from cm to degrees for 2 cm radius wheels

#-------- CONSTANTS -----------#
DPS = 50  # speed of the robot
MAX_ROOM_DISTANCE = 19 #cm
DISTANCE_PER_SCANNING = 2.8/2 #2.8 is the size of a sticker
DISTANCE_ENTER = 9 # Distance from orange door at which the robot must leave

#------------- SETUP -------------#
emergency_stop = False
right_motor = Motor("C") # RIGHT_WHEEL
left_motor = Motor("B") # LEFT_WHEEL
touch_sensor = TouchSensor(4)
wait_ready_sensors()
pendulum_mvt.scanner_motor.reset_encoder()
pendulum_mvt.drop_motor.reset_encoder()
right_motor.reset_encoder()
left_motor.reset_encoder()


# ------------EMERGENCY STOP ---------------- #

def wheels_stop():
    """
    Function that stop the movement of all the motors of the robot
    
    """
    right_motor.set_dps(0)
    left_motor.set_dps(0)
    pendulum_mvt.drop_motor.set_dps(0)
    pendulum_mvt.scanner_motor.set_dps(0)

def emergency_triggered(): # lowkey so useless actually, I could just  the global variable of the robot file : emergency_stop
                            # For this file, ngl, I asked chatgpt to help me for the emergency stop cuz I wasn't so sure
    """
    Function that returns the emergency_stop Boolean of the pendulum file
    If it is true, that means the touch sensor was pressed
    """
    return pendulum_mvt.emergency_stop  # use pendulum’s global flag

def safe_sleep(t):
    """
    Function that verifies the emergency_stop Boolean of pendulum file every 0.05 milisecond for one second
    for a certain duration t (Function derived from chatgpt ngl)
    Acts as a time.sleep
    If emergency_stop activated, stop all movements from both files that contain motors

    Args:
        t (float): The distance by which the robot must move
    """
    for _ in range(int(t * 20)):
        if emergency_triggered():
            wheels_stop() # Haha it looks like I am stopping the arms twice but better too much than not enough
            pendulum_mvt.emergency_stop_arms()
            return
        time.sleep(0.05)



#-------- MOVE THE ROBOT ------------#
def move_robot(distance, dps):
    """
    Function that moves the robot by a certain distance and at a certain speed.

    Args:
        distance (float): The distance by which the robot must move
        dps (int): The speed at which the robot must move
    """

    # Stop the movement of the motors if emergency_stop of pendulum True, i.e. touch sensor was pressed 
    if emergency_triggered():
        wheels_stop()
        pendulum_mvt.emergency_stop_arms()
        return

    # Set the speed of the wheels  
    right_motor.set_dps(dps)
    left_motor.set_dps(dps)

    # Rotate wheels to travel a certain distance
    left_motor.set_position_relative(-distance * DISTTODEG)
    right_motor.set_position_relative(-distance * DISTTODEG)


def move_back_after_scanning(total_distance):
    """
    Function that moves the robot back to 9 cm from the orange door once it finished scanning the room 
    and no Green or Red was detected.
    It intializes the arms back at the same time to position 0 
    Args:
        total_distance (float): The total distance travelled by the robot starting from the orange door
    """

    # First stop the movement of the motors once the extremity of the room was reached
    wheels_stop()

    # Stop the movement of the arms if emergency_stop of pendulum True, i.e. touch sensor was pressed 
    if emergency_triggered():
        pendulum_mvt.emergency_stop_arms()
        return

    # Then reset the position of both arms at the same time to 0
    pendulum_mvt.reset_both_motors_to_initial_position()
    safe_sleep(1)

    # Don't move the robot if emergency_stop was triggered
    if emergency_triggered():
        return

    # Then move back the robot from the total distance it travelled (MAX_ROOM_DISTANCE) + DISTANCE_PER_SCANNING/2 since the robot
    # starts scanning approximately at the orange door
    move_robot(-(total_distance - DISTANCE_ENTER), 250)


def package_delivery(total_distance, delivery_counter):
    """
    Function that drops the package and goes back to 9 cm from the door
    The angle at which the color arm must move depends on the number of packages dropped
    Args:
        total_distance (float): The total distance the robot travelled in the room
        delivery_count (int) : The number of dropped packages
    """

    # Stop the movement of the motors if emergency_stop of pendulum True, i.e. touch sensor was pressed 
    if emergency_triggered():
        wheels_stop()
        pendulum_mvt.emergency_stop_arms()
        return

    # Determine the angle of rotation of the color sensor arm depending on tis position
    drop_angle = 0
    #storing the initial color arm angle
    initial_color_angle = pendulum_mvt.scanner_motor.get_position()

    # Determine the angle at which the color arm must move, depending on wheter the first block was dropped or not
    if delivery_counter == 0:
        angle_movement = 30
    else:
        angle_movement = 50

    # Calculate the new position of the color arm    
    if initial_color_angle < 0:
        drop_angle = initial_color_angle + angle_movement
    else:
        drop_angle = initial_color_angle - angle_movement

    #reducing the speed of the color arm motor to make the dropping smoother
    pendulum_mvt.scanner_motor.set_dps(50)
    pendulum_mvt.scanner_motor.set_position(drop_angle)
    safe_sleep(2.5)

    # Stop the movement of the arms if emergency_stop of pendulum True, i.e. touch sensor was pressed 
    # The wheels are not moving right now so no need to stop them
    if emergency_triggered():
        pendulum_mvt.emergency_stop_arms()
        return

    #stop the arm
    pendulum_mvt.scanner_motor.set_dps(0)

    #move the arm back to its exact initial angle
    pendulum_mvt.scanner_motor.set_dps(50)
    pendulum_mvt.scanner_motor.set_position(initial_color_angle)
    safe_sleep(1.5)
    pendulum_mvt.scanner_motor.set_dps(0)

    #reset both arms to position 0 at the same time
    pendulum_mvt.reset_both_motors_to_initial_position()
    safe_sleep(1)

    # Don't do anything if emergency is triggered
    if emergency_triggered():
        return

    # Move robot the remaining distance back to 9 cm from the orange door
    remaining = abs(DISTANCE_ENTER - (total_distance + DISTANCE_PER_SCANNING))
    if total_distance < DISTANCE_ENTER:
        move_robot(remaining, 150)
    else:
        move_robot(-remaining, 150)

    safe_sleep(1)


def scan_room(delivery_counter):
    """
    Function that moves the robot and scan through the whole room
    Args:
        delivery_count (int) : The number of dropped packages
    Return:
        Boolean: Return if a green recipient was detected
    """

    # Initialize the wheels, the first position the arms are at and the total_distance
    total_distance = 0
    wheels_stop()
    left_motor.set_position_relative(0)
    right_motor.set_position_relative(0)
    time.sleep(0.05)
    position = "left"

    try:

        # Move the robot back until the color sensor detects 3 consecutive orange
        # That means the robot reached the orange door
        count_orange = 0
        right_motor.set_dps(150)
        left_motor.set_dps(150)
        # Move the robot back as long as the counter of orange is less than 3 and emergency stop has not been triggered
        while count_orange < 3 and not emergency_triggered(): 
            try:
                R, G, B, L = pendulum_mvt.color_sensor.get_value()
                color = pendulum_mvt.color_detection_algorithm.classify_the_color(R, G, B)
                if color == "orange":
                    print(color)
                    count_orange += 1
                else:
                    count_orange = 0
            except Exception:
                pass

            time.sleep(0.05)

        wheels_stop()

        while True:

            # Stop the movement of the motors if emergency_stop of pendulum True, i.e. touch sensor was pressed 
            if emergency_triggered():
                wheels_stop()
                pendulum_mvt.emergency_stop_arms()
                return False

            # If the robot travelled the whole room, it finished scanning it so it needs to go back to 9 cm from the door
            if total_distance >= MAX_ROOM_DISTANCE:
                move_back_after_scanning(total_distance)
                return False # No green detected
                

            # Else, the robot is still scanning the room
            # It needs to advance of a DISTANCE_PER_SCANNING, wait 1.5 seconds to ensure it finished advancing, 
            move_robot(DISTANCE_PER_SCANNING, 150)
            total_distance += DISTANCE_PER_SCANNING
            safe_sleep(1.5)

            # Don't proceed in the code if emergency stop triggered
            if emergency_triggered():
                return False
                
            # Scan the width
            color = pendulum_mvt.main_pendulum(position)

            # Change the position at which the arms must move next
            if position == "right":
                position = "left"
            else:
                position = "right"
            
            # If the color detected by the scanning is red, both wheels and arms should stop moving
            # Then, the arms must reset to 0
            # Then move the robot back to 9cm from the orange door
            if color == "red":
                wheels_stop()
                safe_sleep(1.5)
                pendulum_mvt.reset_both_motors_to_initial_position()
                safe_sleep(1)
                move_robot(DISTANCE_ENTER - DISTANCE_PER_SCANNING*3, 150)
                return False
                

            # If the color detected by the scanning is green, both wheels and arms should stop moving
            # Then the robot can proceed with the package delivery
            elif color == "green":
                wheels_stop()
                package_delivery(total_distance, delivery_counter)
                total_distance = 0
                return True 
                

    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()


# FOR TESTING EMERGENCY STOP 
def monitor_touch_sensor():
    """Continuously monitor the touch sensor and trigger emergency stop."""
    while True:
        if touch_sensor.is_pressed():
            print("TOUCH SENSOR PRESSED! Emergency stop triggered!")
            # Set emergency stop flags
            global emergency_stop
            emergency_stop = True
            pendulum_mvt.emergency_stop = True
            # Your helper function will handle stopping wheels and pendulum
            wheels_stop()            # stops the wheels
            pendulum_mvt.emergency_stop_arms()  # stops both pendulum motors
            reset_brick()
            break
        time.sleep(0.05)

if __name__ == "__main__":
    touch_thread = threading.Thread(target=monitor_touch_sensor)
    touch_thread.daemon = True
    touch_thread.start()
    scan_room(0)
