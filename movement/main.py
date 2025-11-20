from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import line_follower as lf

# === Initialization ===
LEFT_MOTOR = Motor("B")
RIGHT_MOTOR = Motor("C")
COLOR_SENSOR = EV3ColorSensor(1, mode="red")    

# INTERSECTION PATTERN
ROOM = 0        # Meeting Room
ST_ROOM = 1     # Storage Room
NEW_EDGE = 2    # at corner
DEADEND = 3
# INTERSECTION_PATTERN = [ST_ROOM, NEW_EDGE, ROOM,    # This is assuming we are starting facing North
#                         ST_ROOM, NEW_EDGE, ROOM,    
#                         ST_ROOM, NEW_EDGE, ROOM,    
#                         ST_ROOM, ROOM]         
INTERSECTION_PATTERN = [ROOM, ST_ROOM, ROOM,
                        NEW_EDGE, DEADEND, ROOM,
                        NEW_EDGE, ST_ROOM, ROOM,
                        NEW_EDGE, DEADEND]   

wait_ready_sensors(True)

i = 0
while i < len(INTERSECTION_PATTERN):
    lf.line_follower(LEFT_MOTOR, RIGHT_MOTOR, COLOR_SENSOR)
    if INTERSECTION_PATTERN[i] == lf.ROOM:
        print("At meeting room, turning right 90 degrees")
        lf.simple_move_straight(17.5, LEFT_MOTOR, RIGHT_MOTOR, COLOR_SENSOR)
        lf.turn_right_on_self(LEFT_MOTOR, RIGHT_MOTOR)
        lf.undo_turn_right_on_self(LEFT_MOTOR, RIGHT_MOTOR)
    elif INTERSECTION_PATTERN[i] == lf.NEW_EDGE:
        print("At new edge, smooth turning right")
        lf.simple_move_straight(8.5, LEFT_MOTOR, RIGHT_MOTOR, COLOR_SENSOR)
        lf.smooth_turn(LEFT_MOTOR, RIGHT_MOTOR, COLOR_SENSOR)
    elif INTERSECTION_PATTERN[i] == lf.ST_ROOM:
        print("At storage room, skipping for now")
        busy_sleep(2)
    i += 1







