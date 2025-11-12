from utils.brick import Motor, BP, wait_ready_sensors
import math
import time
import pendulum_mvt

# MOVEMENT PARAMETERS
RADIUS = 2 #radius of wheel in cm
DISTTODEG = 360 / (2 * math.pi * RADIUS)  # Conversion factor from cm to degrees for 2 cm radius wheels

# TURNING PARAMETERS
DISTANCE_WHEEL_FROM_CENTER = 5.51 #distance between wheels in cm
CENTER = 12
INNER_RADIUS = CENTER - DISTANCE_WHEEL_FROM_CENTER 
OUTER_RADIUS = CENTER + DISTANCE_WHEEL_FROM_CENTER

# CONTROL PARAMETERS
DPS = 100 # speed of the robot
CHECK_TURN = -10 # distance outer wheel travels in entrance check turn

MAX_ROOM_DISTANCE = 19 #cm
DISTANCE_PER_SCANNING = 2.54

# Initialize motors
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
wait_ready_sensors()
print("System is ready!")



def move_robot(distance):
    """Move the robot forward by a certain distance."""
        
    RIGHT_WHEEL.set_speed(DPS)
    LEFT_WHEEL.set_speed(DPS)
    # rotate wheels
    LEFT_WHEEL.set_position_relative(distance * DISTTODEG)
    RIGHT_WHEEL.set_position_relative(distance * DISTTODEG)
    RIGHT_WHEEL.set_speed(0)
    LEFT_WHEEL.set_speed(0)

def scan_room():
    total_distance = 0
    try:
        while True:

            if (total_distance>= MAX_ROOM_DISTANCE):
                RIGHT_WHEEL.set_speed(0)
                LEFT_WHEEL.set_speed(0)
                pendulum_mvt.motor.set_position(pendulum_mvt.INITIAL_POSITION)
                pendulum_mvt.motor.set_dps(0)           
                pendulum_mvt.motor.set_power(0)
                move_robot(-(MAX_ROOM_DISTANCE + DISTANCE_PER_SCANNING/2))
                break
            move_robot(DISTANCE_PER_SCANNING)
            total_distance += DISTANCE_PER_SCANNING
            time.sleep(3)
            color = pendulum_mvt.find_color()

            if color == "red":
                move_robot(-DISTANCE_PER_SCANNING)
            elif color == "green":
                RIGHT_WHEEL.set_speed(0)
                LEFT_WHEEL.set_speed(0)
                break


    except KeyboardInterrupt:
        LEFT_WHEEL.set_speed(0)
        RIGHT_WHEEL.set_speed(0) 
        pendulum_mvt.motor.set_position(pendulum_mvt.INITIAL_POSITION)
        pendulum_mvt.motor.set_dps(0)           
        pendulum_mvt.motor.set_power(0)
        BP.reset_all()

    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()  


                

        

