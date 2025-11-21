from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import math
import time
# We follow the left edge of the line 


# CONTROL PARAMETERS
BASE_SPEED = -120       # default wheel DPS
KP = -1.3               # adjusts sharpness of turns, the less the smoother
TARGET = 20.0           # Color sensor is halfway between black and white, at the edge of a line
TARGET_THRESHOLD = 10   # acceptable error range from target
MAX_CORRECTION = 100
BLACK_THRESHOLD = 10   # color sensor is placed at exact middle of line
WHITE_THRESHOLD = 36    # color sensor is on full white
INTERSECTION = 7
ROOM = 0
ST_ROOM = 1
NEW_EDGE = 2

# MOVEMENT PARAMETERS
DIAMETER = 4.0                          #radius of wheel in cm
CM_PER_DEG = (math.pi * DIAMETER) / 360 # Conversion factor from cm to degrees for 2 cm radius wheels
DISTTODEG = 360 / (math.pi * DIAMETER)  # Conversion factor from cm to degrees for 2 cm radius wheels

# MOTORS & SENSORS
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
COLOR_SENSOR = EV3ColorSensor(3)
wait_ready_sensors()
print("System is ready!")

# INTERSECTION PATTERN
intersection_pattern_north = [ST_ROOM, NEW_EDGE, ROOM,    # False = ignore and go straight
                              ST_ROOM, NEW_EDGE, ROOM,    # True = take 90° right turn
                              ST_ROOM, NEW_EDGE, ROOM,    # This is assuming we are starting facing North
                              ST_ROOM, ROOM]         
intersection_pattern_south = []                                                                              #This is assuming we are starting facing East
intersections_counter = 0
counter = 0


def get_reflected_light_reading(color_sensor: EV3ColorSensor = COLOR_SENSOR, scans: int = 3) -> float:
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


def stop(left_motor: Motor = LEFT_WHEEL, 
         right_motor: Motor = RIGHT_WHEEL) -> None:
    """Stops the robot."""
    left_motor.set_dps(0)
    right_motor.set_dps(0)

def move_forward(distance,
                 left_wheel: Motor = LEFT_WHEEL,
                 right_wheel: Motor= RIGHT_WHEEL) -> None:
    """Move the robot forward by a certain distance."""
    # set motor limits (use absolute DPS for limits)
    right_wheel.set_limits(100, dps=abs(BASE_SPEED))
    left_wheel.set_limits(100, dps=abs(BASE_SPEED))

    # convert absolute distance (cm) to wheel degrees
    degrees = abs(distance) * DISTTODEG

    if distance >= 0:
        # forward: use same sign convention as previous implementation
        left_wheel.set_position_relative(-degrees)
        right_wheel.set_position_relative(-degrees)
    else:
        # reverse: rotate wheels in opposite direction
        left_wheel.set_position_relative(degrees)
        right_wheel.set_position_relative(degrees)
    busy_sleep(2)

def line_follower_distance(distance: float,
                         left_motor: Motor = LEFT_WHEEL, 
                         right_motor: Motor = RIGHT_WHEEL,
                         color_sensor: EV3ColorSensor = COLOR_SENSOR,
                         speed: float = BASE_SPEED,
                         target: float = TARGET
                         ) -> None:
    """
    Follows line for a specified distance. The robot moves straight.
    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        distance: Distance to move in cm (positive for forward, negative for backward).
        speed: Speed of the motors.
    """
    forward = False
    if distance > 0:
        forward = True

    curr_degrees = (left_motor.get_encoder() + right_motor.get_encoder())/2
    print("curr_degrees: " + str(curr_degrees))
    degrees_to_achieve = curr_degrees - distance/CM_PER_DEG
    print("degrees_to_achieve: " + str(degrees_to_achieve))

    #Need to give it a little boost to get out of only black
    if forward:
        left_motor.set_dps(speed)
        right_motor.set_dps(speed)
    else:
        left_motor.set_dps(-speed)
        right_motor.set_dps(-speed)
    busy_sleep(0.5)
    left_motor.set_dps(0)
    right_motor.set_dps(0)

    if forward:
        #-1800 > -2400
        while (left_motor.get_encoder() + right_motor.get_encoder())/2 > degrees_to_achieve: #signs are flipped due to degrees being negative
            print("moving straight")
            print("Degrees left to achieve: " + str(((left_motor.get_encoder() + right_motor.get_encoder())/2 - degrees_to_achieve)))
            curr_val: float = get_reflected_light_reading(color_sensor, 3) 
            correction_factor: float = -(curr_val - target) * KP
            if correction_factor > 0:
                print("turning right")
            else:
                print("turning left")
            left_motor.set_dps(speed - correction_factor)
            right_motor.set_dps(speed + correction_factor)
            busy_sleep(0.03)               
        left_motor.set_dps(0)
        right_motor.set_dps(0)
        busy_sleep(2)
    else:
        #-1800 < -1200
        while (left_motor.get_encoder() + right_motor.get_encoder())/2 < degrees_to_achieve: 
            print("moving straight backwards")
            print("Degrees left to achieve: " + str((degrees_to_achieve - (left_motor.get_encoder() + right_motor.get_encoder())/2)))
            curr_val: float = get_reflected_light_reading(color_sensor, 3) 
            correction_factor: float = -(curr_val - target) * KP
            left_motor.set_dps(-speed - correction_factor)
            right_motor.set_dps(-speed + correction_factor)
            busy_sleep(0.03)               
        left_motor.set_dps(0)
        right_motor.set_dps(0)
        busy_sleep(2)

def line_follower(direction: bool = True,
                  left_motor: Motor = LEFT_WHEEL, 
                  right_motor: Motor = RIGHT_WHEEL, 
                  color_sensor: EV3ColorSensor = COLOR_SENSOR,
                  kp: float = KP, 
                  target: float = TARGET, 
                  base_speed: float = BASE_SPEED
                  ) -> None:
    """ 
    Follows line indefinitely until black threshold is crossed (intersection).
    Follows left edge of the line, half on line half on white is ideal position
    If sees too much black, will turn left 
    If sees too much white, will turn right 

    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        color_sensor: EV3ColorSensor instance.
        kp: Proportional gain for correction.
        target: Target reflected light value.
        base_speed: Base speed of the motors.
    """
    # Determine direction multiplier
    # if forward, keep dps as is, otherwise reverse
    if direction:
        direction = 1
    else:
        direction = -1

    left_motor.reset_encoder()
    right_motor.reset_encoder()

    curr_val: float = get_reflected_light_reading(color_sensor, 3)
    print("curr_val" + str(curr_val))
    
    while curr_val > BLACK_THRESHOLD:
          # Get current reflected light value
          curr_val: float = get_reflected_light_reading(color_sensor, 3)
          print("curr_val" + str(curr_val))
        
          # Calculate correction factor
          correction_factor: float = -(curr_val - target) * kp
          print("correction factor is: " + str(correction_factor))

          # Apply correction to motor speeds, corrected with direction
          left_motor.set_dps((base_speed - correction_factor) * direction)
          right_motor.set_dps((base_speed + correction_factor) * direction)
          busy_sleep(0.03)
          curr_val: float = get_reflected_light_reading(color_sensor, 3)
          print("curr_val" + str(curr_val))


    left_motor.set_dps(0)
    right_motor.set_dps(0)

def turn_room(left_motor: Motor = LEFT_WHEEL, 
                       right_motor: Motor = RIGHT_WHEEL, 
                       diameter_axis: int = 12.00, 
                       radius: float = DIAMETER/2, 
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
    # move forward to position robot for turn
    line_follower_distance(17.5)
    time_needed = (90 * diameter_axis) / (2 * abs(dps) * radius)
    stop_time = time.time() + time_needed
    while time.time() < stop_time:
        left_motor.set_dps(-dps)
        right_motor.set_dps(dps)
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    busy_sleep(1)

def turn_storage_room(left_motor: Motor = LEFT_WHEEL,
                            right_motor: Motor = RIGHT_WHEEL,
                            color_sensor: EV3ColorSensor = COLOR_SENSOR,
                            dps: int = BASE_SPEED,
                            ) -> float:
    line_follower_distance(17.5)
    while color_sensor.get_red() > BLACK_THRESHOLD:
        left_motor.set_dps(-dps)
        right_motor.set_dps(dps)
        busy_sleep(0.02)
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    while color_sensor.get_red() < TARGET:
        left_motor.set_dps(-dps)
        right_motor.set_dps(dps)
        busy_sleep(0.02)
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    

def undo_turn_room(left_motor: Motor = LEFT_WHEEL,
                            right_motor: Motor = RIGHT_WHEEL, 
                            diameter_axis: int = 12.00, 
                            radius: int = DIAMETER/2, 
                            dps: int = BASE_SPEED) -> None:
    """
    Turns the robot 90 degrees to the left on the spot (undo right turn).
    Args:
        left_motor: Motor instance for the left wheel.
        right_motor: Motor instance for the right wheel.
        diameter_(axis: Distance between the two wheels (cm).
        radius: Radius of the wheels (cm).
        rps: Rotations per second for the motors.
    """
    time_needed = (90 * diameter_axis) / (2 * abs(dps) * radius)
    stop_time = time.time() + time_needed
    while time.time() < stop_time:
        left_motor.set_dps(dps)
        right_motor.set_dps(-dps)
    left_motor.set_dps(0)
    right_motor.set_dps(0)
    busy_sleep(1)



def smooth_turn(left_motor: Motor = LEFT_WHEEL, 
                right_motor: Motor = RIGHT_WHEEL,
                color_sensor: EV3ColorSensor = COLOR_SENSOR):
    """
    Turn the robot to the left until the color sensor detects the line again.
    """
    #TODO: measure proper distance to move forward before turning
    # the axis of the wheels should be lined up with the grey line of the tile
    move_forward(8.5)

    #TODO: clean variables up and put them on top
    # TURNING PARAMETERS
    DISTANCE_WHEEL_FROM_CENTER = 5.51 #distance between wheels in cm
    CENTER = 12
    INNER_RADIUS = CENTER - DISTANCE_WHEEL_FROM_CENTER 
    OUTER_RADIUS = CENTER + DISTANCE_WHEEL_FROM_CENTER

    # Calculate the distance each wheel needs to travel for a 90 degree turn
    inner_turn = 0.25 * (2 * math.pi * INNER_RADIUS)
    outer_turn = 0.25 * (2 * math.pi * OUTER_RADIUS)
    
    # for turning LEFT
    # initialize inner and outer wheels
    inner_wheel = left_motor
    outer_wheel = right_motor

    # adjustment factors
    inner_turn = 1*inner_turn
    outer_turn = 1.03*outer_turn

    # calculate a imaginary center wheel dps for reference
    reference_turn = 0.25 * (2 * math.pi * CENTER)
    time_turn = reference_turn * DISTTODEG / BASE_SPEED

    # calculate inner and outer wheel dps
    inner_dps = inner_turn * DISTTODEG / time_turn   
    outer_dps = outer_turn * DISTTODEG / time_turn    

    # set wheel dps limits for turn
    inner_wheel.set_dps(dps=inner_dps)
    outer_wheel.set_dps(dps=outer_dps)
    busy_sleep(2) # wait for robot to move off the line
    turning = True
    while turning:
        curr_val = get_reflected_light_reading(color_sensor, 3)
        
        # stop turning once target point has been reached
        # kept flexible
        if curr_val < BLACK_THRESHOLD: 
            # continue turning until we find target spot again
            while curr_val < TARGET - TARGET_THRESHOLD:
                curr_val = get_reflected_light_reading(color_sensor, 3)
                continue     

            turning = False
            stop()
            print("stopped")

            #TODO: remove below, left for testing
            # print("moving forward to stabilize on line")
            # line_follower()
            # print("line_follower stopped")
            # move_straight_distance(5)


