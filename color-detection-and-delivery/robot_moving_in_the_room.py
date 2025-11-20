from utils.brick import Motor, BP, wait_ready_sensors
import math
import time
import pendulum_mvt as pdm

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

MAX_ROOM_DISTANCE = 21 #cm
DISTANCE_PER_SCANNING = 2.8

# Initialize motors
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
wait_ready_sensors()
print("System is ready!")



def move_robot(distance, dps):
    """Move the robot forward by a certain distance."""
        
    RIGHT_WHEEL.set_dps(dps)
    LEFT_WHEEL.set_dps(dps)
    # rotate wheels
    LEFT_WHEEL.set_position_relative(-distance * DISTTODEG)
    RIGHT_WHEEL.set_position_relative(-distance * DISTTODEG)
#     RIGHT_WHEEL.set_dps(0)
#     LEFT_WHEEL.set_dps(0)

def scan_room():
    total_distance = 0
    RIGHT_WHEEL.set_dps(0)
    LEFT_WHEEL.set_dps(0)
    LEFT_WHEEL.set_position_relative(0)
    RIGHT_WHEEL.set_position_relative(0)
    time.sleep(0.05)
    try:
        while True:

            if (total_distance>= MAX_ROOM_DISTANCE):
                RIGHT_WHEEL.set_dps(0)
                LEFT_WHEEL.set_dps(0)
                pdm.motor_pendulum.set_position(pdm.INITIAL_POSITION)
                time.sleep(1)
                pendulum_mvt.motor_pendulum.set_dps(0)
                pdm.motor_block.set_position(pdm.INITIAL_POSITION)
                time.sleep(0.5)
                pdm.motor_block.set_dps(0)
                move_robot(-(MAX_ROOM_DISTANCE + DISTANCE_PER_SCANNING/2.5), 250)
                break
            move_robot(DISTANCE_PER_SCANNING, 150)
            print("robot moving")
            total_distance += DISTANCE_PER_SCANNING
            time.sleep(1.5)
            print("starting pendulum")
            color = pdm.main_pendulum()
          
            if color == "red":
                RIGHT_WHEEL.set_dps(0)
                LEFT_WHEEL.set_dps(0)
                pdm.motor_pendulum.set_dps(0)
                pdm.motor_block.set_dps(0) 

                time.sleep(1.5)
                move_robot(-DISTANCE_PER_SCANNING, 150)
                break
            elif color == "green":
                
                print("ENTER DELIVERY LOGIC")
                RIGHT_WHEEL.set_dps(0)
                LEFT_WHEEL.set_dps(0)
                pdm.motor_pendulum.set_dps(0)
                pdm.motor_block.set_dps(0)
                time.sleep(6)

                print("SUCCESSFULYY STOPPED THE MOVEMENT")
                
                
                degree_rotation = 0
                if(pdm.motor_pendulum.get_position() < 0):
                    degree_rotation = 5
                else :
                    degree_rotation = -5

                print("degree rotation", degree_rotation)


                pdm.motor_pendulum.set_dps(50)
                pdm.motor_pendulum.set_position(degree_rotation)
                time.sleep(0.5)

                pdm.motor_pendulum.set_dps(0)

                print("SUCCESSFULLY MOVED THE COLOR ARM")


                move_robot(DISTANCE_PER_SCANNING, 100)
                time.sleep(0.3)
                pdm.motor_pendulum.set_dps(50)
                pdm.motor_block.set_dps(pdm.MOTOR_DPS)
                pdm.motor_pendulum.set_position(pdm.INITIAL_POSITION)
                time.sleep(1)
                pdm.motor_pendulum.set_dps(0)
                pdm.motor_block.set_position(pdm.INITIAL_POSITION)

                time.sleep(1)  
                pdm.motor_block.set_dps(0)

           
                move_robot(-(total_distance - DISTANCE_PER_SCANNING))
                time.sleep(4)
                total_distance = 0
                break

    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()  


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
    scan_room() 

        

