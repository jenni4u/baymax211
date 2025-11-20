from utils.brick import Motor, BP, wait_ready_sensors
import math
import time
import pendulum_mvt, robot_moving_in_the_room


# MOVEMENT PARAMETERS
RADIUS = 2 #radius of wheel in cm
DISTTODEG = 360 / (2 * math.pi * RADIUS)  # Conversion factor from cm to degrees for 2 cm radius wheels

# TURNING PARAMETERS
DISTANCE_WHEEL_FROM_CENTER = 5.51 #distance between wheels in cm
CENTER = 12
INNER_RADIUS = CENTER - DISTANCE_WHEEL_FROM_CENTER 
OUTER_RADIUS = CENTER + DISTANCE_WHEEL_FROM_CENTER

# CONTROL PARAMETERS
DPS =50 # speed of the robot
CHECK_TURN = -10 # distance outer wheel travels in entrance check turn

MAX_ROOM_DISTANCE = 19 #cm
DISTANCE_PER_SCANNING = 2.8

# Initialize motors
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
wait_ready_sensors()
print("System is ready!")


def deliver_package():
    try:
        degree_rotation = 0
        if(pendulum_mvt.motor_pendulum().get_position < 0):
            degree_rotation = 15
        else :
            degree_rotation = -15


        pendulum_mvt.motor_pendulum.set_dps(pendulum_mvt.MOTOR_DPS)
        pendulum_mvt.motor_pendulum.set_position(degree_rotation)
        time.sleep(0.5)

        pendulum_mvt.motor_pendulum.set_dps(0)


        robot_moving_in_the_room.move_robot(3, 100)
        pendulum_mvt.motor_pendulum.set_dps(pendulum_mvt.MOTOR_DPS)
        pendulum_mvt.motor_pendulum.set_position(pendulum_mvt.INITIAL_POSITION)
        time.sleep(1)
        pendulum_mvt.motor_pendulum.set_dps(0)

   

        robot_moving_in_the_room.move_robot(robot_moving_in_the_room.total_distance - 3)
        robot_moving_in_the_room.total_distance = 0


    except KeyboardInterrupt:
        LEFT_WHEEL.set_dps(0)
        RIGHT_WHEEL.set_dps(0) 
        pendulum_mvt.detected_color_algorithm(pendulum_mvt.INITIAL_POSITION, 0, 0)
        BP.reset_all()

    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()  
            







