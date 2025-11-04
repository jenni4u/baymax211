from utils.brick import Motor, wait_ready_sensors
import math

RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
wait_ready_sensors()
print("System is ready!")

# MOVEMENT PARAMETERS
DISTTODEG = 360 / (2 * math.pi * RADIUS)  # Conversion factor from cm to degrees for 2 cm radius wheels
RADIUS = 2 #radius of wheel in cm

# TURNING PARAMETERS
DISTANCE_WHEEL_FROM_CENTER = 6 #distance between wheels in cm
CENTER = 12
INNER_RADIUS = CENTER - DISTANCE_WHEEL_FROM_CENTER 
OUTER_RADIUS = CENTER + DISTANCE_WHEEL_FROM_CENTER

# CONTROL PARAMETERS
DPS = 300
CHECK_TURN = -10 # distance outer wheel travels in entrance check turn

# Set wheel speed limits
RIGHT_WHEEL.set_limits(dps=DPS)
LEFT_WHEEL.set_limits(dps=DPS)


def move_forward(distance):
    """Move the robot forward by a certain distance."""
    distance = -distance

    # rotate wheels
    LEFT_WHEEL.set_position_relative(distance * DISTTODEG)
    RIGHT_WHEEL.set_position_relative(distance * DISTTODEG)
    

def right_half_turn(direction):
    """Turn the robot to position color sensor on the entrance.
    1 for right, 0 for left.
    """
    # initialize moving wheel
    if direction:
        wheel = LEFT_WHEEL
    else:
        wheel = RIGHT_WHEEL
        
    wheel.set_position_relative(CHECK_TURN * DISTTODEG) # Rotate wheel


def turn(distance, direction):
    """
    Turn the robot 90 degrees in the specified direction.
    1 for right, 0 for left.
    """
    distance = -distance

    # Calculate the distance each wheel needs to travel for a 90 degree turn
    inner_turn = 0.25 * (2 * math.pi * INNER_RADIUS)
    outer_turn = 0.25 * (2 * math.pi * OUTER_RADIUS)

    # calculate a imaginary center wheel dps for reference
    reference_turn = 0.25 * (2 * math.pi * CENTER)
    time = reference_turn * DISTTODEG / DPS

    # calculate inner and outer wheel dps
    inner_dps = inner_turn * DISTTODEG / time   
    outer_dps = outer_turn * DISTTODEG / time

    # initialize inner and outer wheels
    if direction:
        inner_wheel = LEFT_WHEEL
        outer_wheel = RIGHT_WHEEL
    else:
        inner_wheel = RIGHT_WHEEL
        outer_wheel = LEFT_WHEEL

    # set wheel dps limits for turn
    inner_wheel.set_limits(dps=inner_dps)
    outer_wheel.set_limits(dps=outer_dps)

    # rotate wheels
    inner_wheel.set_position_relative(inner_turn * DISTTODEG)
    outer_wheel.set_position_relative(outer_turn * DISTTODEG)
    
    # reset wheel DPS
    inner_wheel.set_limits(dps=DPS)
    outer_wheel.set_limits(dps=DPS)
