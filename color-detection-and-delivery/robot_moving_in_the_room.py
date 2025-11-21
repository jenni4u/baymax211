from utils.brick import Motor, BP, wait_ready_sensors
import math
import time
import pendulum_mvt

#-------- MOVEMENT PARAMETERS -----------#
RADIUS = 2 #radius of wheel in cm
DISTTODEG = 360 / (2 * math.pi * RADIUS)  # Conversion factor from cm to degrees for 2 cm radius wheels


#-------- CONSTANTS -----------#
DPS = 50 # speed of the robot
MAX_ROOM_DISTANCE = 21 #cm
DISTANCE_PER_SCANNING = 2.8/2 #2.8 is the size of a sticker

#------------- SETUP -------------#
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
wait_ready_sensors()
pendulum_mvt.motor_color_sensor.reset_encoder()
pendulum_mvt.motor_block.reset_encoder()
RIGHT_WHEEL.reset_encoder()
LEFT_WHEEL.reset_encoder()



#-------- MOVE THE ROBOT ------------#


"""
    Function that moves the robot by a certain distance and at a certain speed.
    Runs only if the color sensor detection has not been stopped yet 
    (i.e. a color was detected or the robot finished scanning the room)

    Args:
        distance (float): The distance by which the robot must move
        dps (int): The speed at which the robot must move
"""
def move_robot(distance, dps):

    # Set the speed of the wheels    
    RIGHT_WHEEL.set_dps(dps)
    LEFT_WHEEL.set_dps(dps)

    # Rotate wheels to advance a certain distance
    LEFT_WHEEL.set_position_relative(-distance * DISTTODEG)
    RIGHT_WHEEL.set_position_relative(-distance * DISTTODEG)


"""
    Function that moves the robot back to the center of the orange door once it finished scanning the room 
    and no Green or Red was detected.
    It first intializes the arms back at the same time to position 0 using a function from pendulum_mvt file : set_both_motors_to_initial_position
    This function uses thread, so if you get an error, please
"""
def move_back_to_door_after_scanning():

    # First stop the movement of the wheels once the extremity of the room was reached
    RIGHT_WHEEL.set_dps(0)
    LEFT_WHEEL.set_dps(0)

    # Then reset the position of both arms at the same time to 0 calling a function from pendulum_mvt
    pendulum_mvt.reset_both_motors_to_initial_position()
    time.sleep(1)

    # Then move back the robot from the total distance it travelled (MAX_ROOM_DISTANCE) + DISTANCE_PER_SCANNING/2 (???)
    # This value was obtained through testing, so it might be retaken again to ensure the robot reaches the center of the orange door
    move_robot(-(MAX_ROOM_DISTANCE + DISTANCE_PER_SCANNING/2), 250)
    



"""
    Function that drops the package and goes back to the door
    Args:
        total_distance (float): The total distance the robot travelled in the room
"""
def package_delivery(total_distance):
        
        # First determine how much the color sensor arm should move to allow the dropping of the block (?????)
        # -> NEEDS TESTING ON THE POSITION OF THE ARM (POSITIVE, NEGATIVE, AT 0, ETC) 
        degree_rotation = 0
        if(pendulum_mvt.motor_color_sensor.get_position() < 0):
            degree_rotation = 17
        else :
            degree_rotation = -17


        # Set a speed to the color sensor arm and move it by degree_rotation, and waits for 3 seconds (???) for the dropping of the block
        pendulum_mvt.motor_color_sensor.set_dps(pendulum_mvt.MOTOR_DPS)
        #(???) Not sure if this is how we set the new position of the arm (by substracting the degree_rotation)
        pendulum_mvt.motor_color_sensor.set_position(pendulum_mvt.motor_color_sensor.get_position() - degree_rotation)
        time.sleep(3)

        pendulum_mvt.motor_color_sensor.set_dps(0)


        # Backup the robot a little (???), to reinitialize the position
        # The reason we backup a little is to ensure that, once the arms move, they don't get blocked by the block
        move_robot(-DISTANCE_PER_SCANNING, 150)
        time.sleep(0.3)


        # Set both arms to positon 0 using a function defined in pendulum_mvt : reset_both_motors_to_initial_position()
        # This function uses threading to move both arms at the same time
        pendulum_mvt.reset_both_motors_to_initial_position()
        time.sleep(1)  

        # Move the robot of the remaining distance to reach the door (The total_distance it travelled - little backup) (????)
        move_robot(-(total_distance - DISTANCE_PER_SCANNING), 150)
        time.sleep(1)
         



"""
    Function that moves the robot and scan through the whole room
"""
def scan_room():
    total_distance = 0
    RIGHT_WHEEL.set_dps(0)
    LEFT_WHEEL.set_dps(0)
    LEFT_WHEEL.set_position_relative(0)
    RIGHT_WHEEL.set_position_relative(0)
    time.sleep(0.05)
    try:
        while True:

            # If the robot travelled the whole room, it finished scanning it so it needs to go back to door
            if (total_distance>= MAX_ROOM_DISTANCE):
                move_back_to_door_after_scanning()
                break

            # Else, the robot is still scanning the room
            # It needs to advance of a DISTANCE_PER_SCANNING, wait 1.5 (???) second to ensure it finished advancing, 
            # and scan the width with the arms
            move_robot(DISTANCE_PER_SCANNING, 150)
            total_distance += DISTANCE_PER_SCANNING
            time.sleep(1.5)
            color = pendulum_mvt.main_pendulum()
          

            # If the color detected by the scanning is red, both wheels should stop moving
            # Then, the robot backups of DISTANCE_PER_SCANNING (????) -> might be the wrong value, please check that
            if color == "red":
                RIGHT_WHEEL.set_dps(0)
                LEFT_WHEEL.set_dps(0)
                time.sleep(1.5)
                move_robot(-DISTANCE_PER_SCANNING, 150)
                break


            # If the color detected by the scanning is red, both wheels should stop moving
            elif color == "green":
                RIGHT_WHEEL.set_dps(0)
                LEFT_WHEEL.set_dps(0)   
                package_delivery(total_distance)
                total_distance = 0 # Once done moving back, set the total_distance to 0
                break


    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()  


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
    scan_room() 

        

