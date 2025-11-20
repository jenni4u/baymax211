from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import line_follower as lf

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
color_sensor = EV3ColorSensor(3, mode="red")    

# INTERSECTION PATTERN
ROOM = 0
ST_ROOM = 1
NEW_EDGE = 2
INTERSECTION_PATTERN = [ST_ROOM, NEW_EDGE, ROOM,    # False = ignore and go straight
                        ST_ROOM, NEW_EDGE, ROOM,    # True = take 90° right turn
                        ST_ROOM, NEW_EDGE, ROOM,    # This is assuming we are starting facing North
                        ST_ROOM, ROOM]         
INTERSECTION_PATTERN_SOUTH = []   

wait_ready_sensors(True)


# i = 0
# while i < len(intersection_pattern):
#     lf.line_follower(left_motor, right_motor, color_sensor)
#     if intersection_pattern[i] == lf.ROOM:
#         print("At meeting room, turning right 90 degrees")
#         lf.simple_move_straight(17.5, left_motor, right_motor, color_sensor)
#         lf.turn_right_on_self(left_motor, right_motor)
#         lf.undo_turn_right_on_self(left_motor, right_motor)
#     elif intersection_pattern[i] == lf.NEW_EDGE:
#         print("At new edge, smooth turning right")
#         lf.simple_move_straight(8.5, left_motor, right_motor, color_sensor)
#         lf.smooth_turn(left_motor, right_motor)
#     elif intersection_pattern[i] == lf.ST_ROOM:
#         print("At storage room, skipping for now")
#         busy_sleep(2)
#     i += 1

lf.line_follower(left_motor, right_motor, color_sensor)
lf.move_straight_distance(17.5, left_motor, right_motor, color_sensor)
lf.turn_left_on_self(left_motor, right_motor)
lf.move_forward(-6.5, left_motor, right_motor)
lf.move_forward(6.5, left_motor, right_motor)
lf.undo_turn_left_on_self(left_motor, right_motor)
lf.line_follower(left_motor, right_motor, color_sensor)



#turn_right_90(left_motor, right_motor, color_sensor)

#line_follower.simple_move_straight(left_motor, right_motor, color_sensor, 17.5)
#line_follower.turn_right_on_self(left_motor, right_motor)
#line_follower.undo_turn_right_on_self(left_motor, right_motor)
