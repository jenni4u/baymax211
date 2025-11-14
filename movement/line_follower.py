from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import math
from typing import List
import time
# We follow the left edge of the line 

# === Constants ===    
BASE_SPEED     : int   = -120
KP             : float = -1.3                   #adjusts sharpness of turns,                   the less the smoother
TARGET         : float = 35.0               # Color sensor is halfway between black and white, at the edge of a line
MAX_CORRECTION : int   = 100
BLACK_THRESHOLD: int   = 10      # color sensor is placed at exact middle of line
WHITE_THRESHOLD: int   = 36      # color sensor is on full white

# MOVEMENT PARAMETERS
DIAMETER  : float = 4.0 #radius of wheel in cm
CM_PER_DEG: float = (math.pi * DIAMETER) / 360  # Conversion factor from cm to degrees for 2 cm radius wheels

# === Intersection pattern ===
# False = ignore and go straight
# True = take 90° right turn
intersection_pattern_north: List[bool] = [False, True, True, False, True, True, False, True, True, False, True]         #This is assuming we are starting facing North
intersection_pattern_south: List[bool] = []                                                                              #This is assuming we are starting facing East
intersections_counter     : int        = 0
counter                   : int        = 0


def get_reflected_light_reading(color_sensor: EV3ColorSensor, scans: int = 3) -> float:
    """
    Average several color sensor readings for stability.
    
    Args:
        color_sensor: EV3ColorSensor instance.
        scans: Number of readings to average.
    Returns:
        Average reflected light value (0–100 scale).
    """
    total = 0
    for i in range(scans):
        total += color_sensor.get_red()
    return total / scans


# def turn_right_90(left_motor: Motor,
#                   right_motor: Motor, 
#                   color_sensor: EV3ColorSensor, 
#                   target: float = TARGET
#                   ) -> float:
#     """ 
#     Performs a 90° right turn using the color sensor to detect the line 
    
#     Args:
#         left_motor: Motor instance for the left wheel.
#         right_motor: Motor instance for the right wheel.
#         color_sensor: EV3ColorSensor instance.
#         target: Reflected light value to detect the line.
#     Returns: time taken to do the turn for undo function
#     """
#     # Rotate in place until black is detected again
#     curr_time = time.time()
#     while True:
#         left_motor.set_dps(100)
#         right_motor.set_dps(-100)
#         if color_sensor.get_red() <= target:
#             break
#     done_time = time.time()
#     time_taken = done_time - curr_time
#      # Move forward a bit to stabilize onto the new line
#     left_motor.set_dps(120)
#     right_motor.set_dps(120)
#     busy_sleep(0.2)

#     left_motor.set_dps(0)
#     right_motor.set_dps(0)

#     return time_taken

# def undo_turn_right_90( left_motor  : Motor,
#                         right_motor : Motor,
#                         time_taken  : float,
#                     ) -> None:
#     """ 
#     Performs a 90° left and back
    
#     Args:
#         left_motor: Motor instance for the left wheel.
#         right_motor: Motor instance for the right wheel.
#         color_sensor: EV3ColorSensor instance.
#         target: Reflected light value to detect the line.
#     """
#     left_motor.set_dps(-120)
#     right_motor.set_dps(-120)
#     busy_sleep(0.2)

#     start_time = time.time()
#     while (time.time() - start_time) < time_taken:
#         left_motor.set_dps(-100)
#         right_motor.set_dps(100)

#     left_motor.set_dps(0)
#     right_motor.set_dps(0)


def turn_right_on_self(left_motor: Motor, 
                       right_motor: Motor, 
                       diameter_axis: int = 12.00, 
                       radius: int = DIAMETER/2, 
                       dps: int = BASE_SPEED) -> None:
    """
    Turns the robot 90 degrees to the right on the spot.
    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        diameter_axis: Distance between the two wheels (cm).
        radius: Radius of the wheels (cm).
        rps: Rotations per second for the motors.
    """
    time_needed = (95 * diameter_axis) / (2 * abs(dps) * radius)
    stop_time = time.time() + time_needed
    while time.time() < stop_time:
        left_motor.set_dps(dps)
        right_motor.set_dps(-dps)
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    busy_sleep(1)
    
def undo_turn_right_on_self(left_motor: Motor,
                            right_motor: Motor, 
                            diameter_axis: int = 12.00, 
                            radius: int = DIAMETER/2, 
                            dps: int = BASE_SPEED) -> None:
    """
    Turns the robot 90 degrees to the left on the spot (undo right turn).
    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        diameter_axis: Distance between the two wheels (cm).
        radius: Radius of the wheels (cm).
        rps: Rotations per second for the motors.
    """
    time_needed = (95 * diameter_axis) / (2 * abs(dps) * radius)
    stop_time = time.time() + time_needed
    while time.time() < stop_time:
        left_motor.set_dps(-dps)
        right_motor.set_dps(dps)
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    busy_sleep(1)


def simple_move_straight(left_motor: Motor, 
                         right_motor: Motor,
                         color_sensor: EV3ColorSensor, 
                         distance: float, 
                         speed: float = BASE_SPEED,
                         target: float = TARGET
                         ) -> None:
    """
    Moves the robot straight for a specified distance.
    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        distance: Distance to move in cm (positive for forward, negative for backward).
        speed: Speed of the motors.
    """
    curr_degrees = (left_motor.get_encoder() + right_motor.get_encoder())/2
    print("curr_degrees: " + str(curr_degrees))
    degrees_to_achieve = curr_degrees - distance/CM_PER_DEG
    print("degrees_to_achieve: " + str(degrees_to_achieve))

    #Need to give it a little boost to get out of only black
    left_motor.set_dps(speed)
    right_motor.set_dps(speed)
    busy_sleep(0.5)
    left_motor.set_dps(0)
    right_motor.set_dps(0)

    while (left_motor.get_encoder() + right_motor.get_encoder())/2 > degrees_to_achieve: #signs are flipped due to degrees being negative
         print("moving straight")
         print("Degrees left to achieve: " + str(((left_motor.get_encoder() + right_motor.get_encoder())/2 - degrees_to_achieve)))
         curr_val: float = get_reflected_light_reading(color_sensor, 3) 
         correction_factor: float = (curr_val - TARGET) * KP
         left_motor.set_dps(speed - correction_factor)
         right_motor.set_dps(speed + correction_factor)
         busy_sleep(0.03)               
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    busy_sleep(2)

    

def move_straight(left_motor: Motor, 
                  right_motor: Motor, 
                  color_sensor: EV3ColorSensor, 
                  distance: float, 
                  kp: float = KP, 
                  target: float = TARGET, 
                  base_speed: float = BASE_SPEED
                  ) -> None:
    """ 
    Follows left edge of the line, half on line half on white is ideal position
    If sees too much black, will turn left 
    If sees too much white, will turn right 

    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        color_sensor: EV3ColorSensor instance.
        distance: Distance to move in cm (positive for forward, negative for backward).
        kp: Proportional gain for correction.
        target: Target reflected light value.
        base_speed: Base speed of the motors.
    """
    
    left_motor.reset_encoder()
    right_motor.reset_encoder()
    curr_dist: float = 0.0
    
    while curr_dist < distance:
          curr_val: float = get_reflected_light_reading(color_sensor, 3)
          print("curr_val" + str(curr_val))
          if curr_val < 15:
              simple_move_straight(left_motor, right_motor, color_sensor, 17.5)              
              turn_right_on_self(left_motor, right_motor)
              undo_turn_right_on_self(left_motor, right_motor)
            
          correction_factor: float = (curr_val - target) * kp
          print("correction factor is: " + str(correction_factor))

          left_motor.set_dps(base_speed - correction_factor)
          right_motor.set_dps(base_speed + correction_factor)
          busy_sleep(0.05)               #maybe change this 
          
          # update curr_dist
          left_deg = left_motor.get_encoder()
          right_deg = right_motor.get_encoder()
          curr_dist = -(((left_deg + right_deg) / 2) * CM_PER_DEG)
          print("curr_dist is:" + str(curr_dist))
          
          
    left_motor.set_dps(0)
    right_motor.set_dps(0)





     