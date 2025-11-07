from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import math
# We follow the left edge of the line 

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
color_sensor = EV3ColorSensor(1)                  

wait_ready_sensors(True)

# === Constants ===    
BASE_SPEED = -150           
KP = -1.3                   #adjusts sharpness of turns, the less the smoother
TARGET = 20.0               # Color sensor is halfway between black and white, at the edge of a line 
MAX_CORRECTION = 100
BLACK_THRESHOLD = 10      # color sensor is placed at exact middle of line 
WHITE_THRESHOLD = 36      # color sensor is on full white 

# MOVEMENT PARAMETERS
DIAMETER = 4 #radius of wheel in cm
CM_PER_DEG = (math.pi * DIAMETER) / 360  # Conversion factor from cm to degrees for 2 cm radius wheels

# === Intersection pattern ===
# False = ignore and go straight
# True = take 90° right turn
intersection_pattern_north = [False, True, True, False, True, True, False, True, True, False, True]         #This is assuming we are starting facing North 
intersection_pattern_south = []                                                                              #This is assuming we are starting facing East  
intersections_counter = 0

# === Other variables ===
last_black_time = 0

# === Helper: 90° right turn ===
def turn_right_90():
    # Rotate in place until black is detected again
    while True:
        left_motor.set_dps(100)
        right_motor.set_dps(-100)
        if color_sensor.get_red() < TARGET:
            break
     # Move forward a bit to stabilize onto the new line
    left_motor.set_dps(150)
    right_motor.set_dps(150)
    #sleep(0.4)
    left_motor.set_dps(0)
    right_motor.set_dps(0)


# === Main Loop ===
def move_straight(distance):
    """ Follows left edge of the line, half on line half on white is ideal position
    If sees too much black, will turn left 
    If sees too much white, will turn right 
    """
    
    left_motor.reset_encoder()
    right_motor.reset_encoder()
    curr_dist = 0
    
    while curr_dist < distance:
          curr_val = 0
          for i in range(3):             #maybe increase this 
              curr_val += color_sensor.get_red()
          curr_val = curr_val/3
          print("curr_val" + str(curr_val))
          correction_factor = (curr_val - TARGET) * KP
          print("correction factor is: " + str(correction_factor))
          left_motor.set_dps(BASE_SPEED + correction_factor)
          right_motor.set_dps(BASE_SPEED - correction_factor)
          busy_sleep(0.09)               #maybe change this 
          
          # update curr_dist
          left_deg = left_motor.get_encoder()
          right_deg = right_motor.get_encoder()
          curr_dist = -(((left_deg + right_deg) / 2) * CM_PER_DEG)
          print("curr_dist is:" + str(curr_dist))
          
          
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    
      

move_straight(86)





     