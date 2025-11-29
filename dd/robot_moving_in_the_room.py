from utils.brick import EV3ColorSensor, Motor, BP, wait_ready_sensors
import math
import time
from pendulum_mvt import PendulumScanner


class RobotScannerOfRoom:
    #-------- MOVEMENT PARAMETERS -----------#
    RADIUS = 2 #radius of wheel in cm
    DISTTODEG = 360 / (2 * math.pi * RADIUS)  # Conversion factor from cm to degrees for 2 cm radius wheels


    #-------- CONSTANTS -----------#
    DPS = 50 # speed of the robot
    MAX_ROOM_DISTANCE = 22 #cm
    DISTANCE_PER_SCANNING = 2.8/2 #2.8 is the size of a sticker
    DISTANCE_ENTER = 9 # According to my testing (might need to be verified) the color sensor is placed at 9cm from the orange door (extremity)

    #------------- CONSTRUCTOR -------------#
    def __init__(self, motor_color_sensor, motor_block, color_sensor, RIGHT_WHEEL, LEFT_WHEEL):
        """
        Initializes a new instance of the robot scanner in the room.

        Args:
            motor_color_sensor: The motor of the color arm.
            motor_block: The motor that contains the cage of the blocks
            color_sensor: The color sensor
            RIGHT_WHEEL: The right wheel of the robot
            LEFT_WHEEL: The left wheel of the robot
        """

        # Motor for the arms
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block

        # Wheels
        self.LEFT_WHEEL = LEFT_WHEEL
        self.RIGHT_WHEEL = RIGHT_WHEEL

        # Color sensor 
        self.COLOR_SENSOR = color_sensor

        # Create the pendulum object that scans the width
        self.scanner = PendulumScanner(motor_color_sensor,motor_block,color_sensor)
        
        motor_block.reset_encoder()
        motor_color_sensor.reset_encoder()
        LEFT_WHEEL.reset_encoder()
        RIGHT_WHEEL.reset_encoder()

        self.emergency_stop = False


    #-------- MOVE THE ROBOT ------------#

    def stop(self):
        self.RIGHT_WHEEL.set_dps(0)
        self.LEFT_WHEEL.set_dps(0)
        
    def move_robot(self, distance, dps):

        """
        Function that moves the robot by a certain distance and at a certain speed.

        Args:
            distance (float): The distance by which the robot must move
            dps (int): The speed at which the robot must move
        """
        
        if (self.emergency_stop):
            self.stop()
            return

        # Set the speed of the wheels    
        self.RIGHT_WHEEL.set_dps(dps)
        self.LEFT_WHEEL.set_dps(dps)

        # Rotate wheels to advance a certain distance
        self.LEFT_WHEEL.set_position_relative(-distance * self.DISTTODEG)
        self.RIGHT_WHEEL.set_position_relative(-distance * self.DISTTODEG)

        if (self.emergency_stop):
            self.stop()
            return




    def move_back_after_scanning(self, total_distance):
        """
        Function that moves the robot back to where the robot entered once it finished scanning the room and no Green or Red was detected.
        It first intializes the arms back at the same time to position 0 using a function from pendulum_mvt file : set_both_motors_to_initial_position

        Args:
            total_distance (float): The total distance the robot travelled in the room starting from the center of the orange door (color sensor)
        """
            
        if (self.emergency_stop):
            self.stop()
            return
        
        # First stop the movement of the wheels once the extremity of the room was reached
        self.RIGHT_WHEEL.set_dps(0)
        self.LEFT_WHEEL.set_dps(0)

        # Then reset the position of both arms at the same time to 0 calling a function from pendulum_mvt
        self.scanner.reset_both_motors_to_initial_position()
        time.sleep(1)

        # Then move back the robot to its entrance position
        # The total_distance doesn't include half of the orange door
        # Since the robot must be placed at 9 cm form the orange door, include this DISTANCE_PER_SCANNING IN THE CALCULATION
        self.move_robot(-(total_distance + self.DISTANCE_PER_SCANNING - self.DISTANCE_ENTER), 250)

        if (self.emergency_stop):
            self.stop()
            return
        




    def package_delivery(self,total_distance, delivery_counter):

        """
        Function that drops the package and goes back to where the robot entered
        Args:
            total_distance (float): The total distance the robot travelled in the room starting from the center of the orange door (color sensor)
            delivery_count (float): The number of blocks dropped
        """
            
        # Determine how much the color sensor must move. 
        # If the deliver_count is 0 (no block dropped yet), the angle is 30. Else, the robot must move of 50
        angle_movement = 0
        if (delivery_counter == 0):
            angle_movement = 27
            angle_movement = 30
        else:
            angle_movement = 50


        # Determine the new positon of the color sensor arm to allow the dropping
        drop_angle = 0
        initial_color_angle = self.scanner.motor_color_sensor.get_position() #storing the initial position of the color arm
        if initial_color_angle < 0:
            drop_angle = initial_color_angle + angle_movement 
        else:
            drop_angle = initial_color_angle - angle_movement

        #reducing the speed of the motor to make it smoother and set the new position of the color arm
        self.scanner.motor_color_sensor.set_dps(self.scanner.MOTOR_DPS - 100)

        if (self.emergency_stop):
            self.stop()
            return
        self.scanner.motor_color_sensor.set_position(drop_angle)
        if (self.emergency_stop):
            self.stop()
            return
        

        time.sleep(2.5)      

        #stop the arm
        self.scanner.motor_color_sensor.set_dps(0)

        #move the arm back to its exact initial angle
        self.scanner.motor_color_sensor.set_dps(self.scanner.MOTOR_DPS - 100)

        if (self.emergency_stop):
            self.stop()
            return 
        self.scanner.motor_color_sensor.set_position(initial_color_angle)
        if (self.emergency_stop):
            self.stop()
            return
        
        time.sleep(1.5)
        self.scanner.motor_color_sensor.set_dps(0)

        #reset both arms to position 0 at the same time
        self.scanner.reset_both_motors_to_initial_position()
        time.sleep(1)

        # Move robot the remaining distance back toward where the robot entered
        remaining = abs(self.DISTANCE_ENTER - (total_distance + self.DISTANCE_PER_SCANNING)) #include first half of orange door in calculations as the robot enters 9 cm from the extremity of the orange door)
        # If the robot didn't exceed the DISTANCE_ENTER, make it advance
        if (total_distance < self.DISTANCE_ENTER):
            self.move_robot(remaining, 150)
        # Make the robot backup
        else:
            self.move_robot(-remaining, 150)
        time.sleep(1)



    def scan_room(self, delivery_counter):
        """
        Function that moves the robot and scan through the whole room
        Args:
            delivery_count (float): The number of blocks dropped
        Returns:
            Boolean: Return the if a block was dropped or not
        """
            
        # Initialize the wheels and the total_distance to 0
        total_distance = 0
        self.RIGHT_WHEEL.set_dps(0)
        self.LEFT_WHEEL.set_dps(0)
        self.LEFT_WHEEL.set_position_relative(0)
        self.RIGHT_WHEEL.set_position_relative(0)
        time.sleep(0.05)
        position = "left"
        
        
        try:
            # The robot enters at 9 cm from the orange door, so make it backup to the middle of the orange dorr
            self.move_robot(-(self.DISTANCE_ENTER - self.DISTANCE_PER_SCANNING), 200)
            time.sleep(2)
            
            
            while True:
                # If the robot travelled the whole room, it finished scanning it so it needs to go back to the robot's entrance position
                if (total_distance>= self.MAX_ROOM_DISTANCE):
                    self.move_back_after_scanning(total_distance)
                    counter = 0
                    position = "left"
                    return False  # No green detected so no block dropped

                # Else, the robot is still scanning the room
                # It needs to advance of a DISTANCE_PER_SCANNING and wait 1.5 second to ensure it finished advancing, 
                # Then scan the width with the arms
                self.move_robot(self.DISTANCE_PER_SCANNING, 150)
                total_distance += self.DISTANCE_PER_SCANNING
                time.sleep(1.5)
        
                color = self.scanner.main_pendulum(position)
                if (position == "left"):
                    position = "right"
                else:
                    position = "left"
                
                #counter+=1
                
            

                if color == "red":
                    self.RIGHT_WHEEL.set_dps(0)
                    self.LEFT_WHEEL.set_dps(0)
                    time.sleep(0.3)
                    #reset both arms to position 0 at the same time
                    self.scanner.reset_both_motors_to_initial_position()
                    time.sleep(0.2)
                    # Advance the robot to the entrance position. If red was detected, it should have be from a distance of 3 DISTANCE_PER_SCANNING from the extremity of the room
                    self.move_robot(self.DISTANCE_ENTER - self.DISTANCE_PER_SCANNING*3, 150)
                    position = "left"
                    counter = 0
                    
                    return False # No green detected so no block dropped


                # If the color detected by the scanning is green, both wheels should stop moving
                # Then the delivery should proceed
                elif color == "green":
                    self.RIGHT_WHEEL.set_dps(0)
                    self.LEFT_WHEEL.set_dps(0)   
                    self.package_delivery(total_distance, delivery_counter)
                    total_distance = 0 # Once done moving back, set the total_distance to 0
                    counter = 0
                    position = "left"
                    
                    return True # Green detected so block dropped -> True


        except BaseException as error:
            print("Error during scan_room:", error)
            counter = 0
            BP.reset_all()  


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
    motor_color_sensor = Motor("A")
    motor_block = Motor("D")
    COLOR_SENSOR = EV3ColorSensor(3) 
    LEFT_WHEEL = Motor("B")
    RIGHT_WHEEL = Motor("C")
    scanner = RobotScannerOfRoom( motor_color_sensor, motor_block, COLOR_SENSOR, RIGHT_WHEEL, LEFT_WHEEL)
    scanner.scan_room(1)