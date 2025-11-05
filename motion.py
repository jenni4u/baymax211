from utils.brick import Motor, EV3GyroSensor, wait_ready_sensors
import math

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

# Initialize motors
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
gyro = EV3GyroSensor(1)

wait_ready_sensors()
print("System is ready!")

def reset():
    """Reset the robot's motors and settings."""
    RIGHT_WHEEL.set_limits(100, dps=DPS)
    LEFT_WHEEL.set_limits(100, dps=DPS)

def move_forward(distance):
    """Move the robot forward by a certain distance."""
    distance = -distance
    reset()    

    # rotate wheels
    LEFT_WHEEL.set_position_relative(distance * DISTTODEG)
    RIGHT_WHEEL.set_position_relative(distance * DISTTODEG)
    

def check_entrance(direction):
    """Turn the robot to position color sensor on the entrance.
    1 for right, 0 for left.
    """
    reset()

    # initialize moving wheel
    if direction:
        wheel = LEFT_WHEEL
    else:
        wheel = RIGHT_WHEEL

    wheel.set_position_relative(CHECK_TURN * DISTTODEG) # Rotate wheel

def post_entrance(direction):
    """Turn the robot to position color sensor on the entrance.
    1 for right, 0 for left.
    """
    reset()
    
    # initialize moving wheel
    if direction:
        wheel = LEFT_WHEEL
    else:
        wheel = RIGHT_WHEEL

    wheel.set_position_relative(-CHECK_TURN * DISTTODEG) # Rotate wheel

def turn(direction):
    """
    Turn the robot 90 degrees in the specified direction.
    1 for right, 0 for left.
    """
    # Calculate the distance each wheel needs to travel for a 90 degree turn
    inner_turn = 0.25 * (2 * math.pi * INNER_RADIUS)
    outer_turn = 0.25 * (2 * math.pi * OUTER_RADIUS)
    
    # initialize inner and outer wheels
    if direction: #right
        inner_wheel = RIGHT_WHEEL
        outer_wheel = LEFT_WHEEL

        # adjustment factors
        inner_turn = 0.98*inner_turn
        outer_turn = 1.07*outer_turn
        
    else: #left
        inner_wheel = LEFT_WHEEL
        outer_wheel = RIGHT_WHEEL

        # adjustment factors
        inner_turn = 1*inner_turn
        outer_turn = 1.03*outer_turn

    # calculate a imaginary center wheel dps for reference
    reference_turn = 0.25 * (2 * math.pi * CENTER)
    time = reference_turn * DISTTODEG / DPS

    # calculate inner and outer wheel dps
    inner_dps = inner_turn * DISTTODEG / time   
    outer_dps = outer_turn * DISTTODEG / time    

    # set wheel dps limits for turn
    inner_wheel.set_limits(dps=inner_dps)
    outer_wheel.set_limits(dps=outer_dps)

    # rotate wheels for preset turn
    inner_wheel.set_position_relative(-inner_turn * DISTTODEG)
    outer_wheel.set_position_relative(-outer_turn * DISTTODEG)

    # continuous turning
    """
    inner_wheel.set_dps(-inner_dps)
    outer_wheel.set_dps(-outer_dps)
    """

def turnWSensor(direction): 
    """
    Turn the robot 90 degrees in the specified direction.
    1 for right, 0 for left.
    """
    # Calculate the distance each wheel needs to travel for a 90 degree turn
    inner_turn = 0.25 * (2 * math.pi * INNER_RADIUS)
    outer_turn = 0.25 * (2 * math.pi * OUTER_RADIUS)
    
    # initialize inner and outer wheels
    if direction: #right
        inner_wheel = RIGHT_WHEEL
        outer_wheel = LEFT_WHEEL

        # adjustment factors
        inner_turn = 0.98*inner_turn
        outer_turn = 1.07*outer_turn
        
    else: #left
        inner_wheel = LEFT_WHEEL
        outer_wheel = RIGHT_WHEEL

        # adjustment factors
        inner_turn = 1*inner_turn
        outer_turn = 1.03*outer_turn

    # calculate a imaginary center wheel dps for reference
    reference_turn = 0.25 * (2 * math.pi * CENTER)
    time = reference_turn * DISTTODEG / DPS

    # calculate inner and outer wheel dps
    inner_dps = inner_turn * DISTTODEG / time   
    outer_dps = outer_turn * DISTTODEG / time    

    # set wheel dps limits for turn
    inner_wheel.set_limits(dps=inner_dps)
    outer_wheel.set_limits(dps=outer_dps)

    # rotate wheels for preset turn
    inner_wheel.set_position_relative(-inner_turn * DISTTODEG)
    outer_wheel.set_position_relative(-outer_turn * DISTTODEG)

    print(gyro.get_abs_measure()) 

    # continuous turning
    """
    inner_wheel.set_dps(-inner_dps)
    outer_wheel.set_dps(-outer_dps)
    """

turnWSensor(1)