from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import line_follower as lf

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
color_sensor = EV3ColorSensor(1, mode="red")    

intersection_pattern = lf.intersection_pattern_north

wait_ready_sensors(True)

i = 0
while i < len(intersection_pattern):
    lf.line_follower(left_motor, right_motor, color_sensor)
    if intersection_pattern[i] == lf.ROOM:
        print("At meeting room, turning right 90 degrees")
        lf.simple_move_straight(17.5, left_motor, right_motor, color_sensor)
        lf.turn_right_on_self(left_motor, right_motor)
        lf.undo_turn_right_on_self(left_motor, right_motor)
    elif intersection_pattern[i] == lf.NEW_EDGE:
        print("At new edge, smooth turning right")
        lf.simple_move_straight(8.5, left_motor, right_motor, color_sensor)
        lf.smooth_turn(left_motor, right_motor)
    elif intersection_pattern[i] == lf.ST_ROOM:
        print("At storage room, skipping for now")
        busy_sleep(2)
    i += 1


#turn_right_90(left_motor, right_motor, color_sensor)

#line_follower.simple_move_straight(left_motor, right_motor, color_sensor, 17.5)
#line_follower.turn_right_on_self(left_motor, right_motor)
#line_follower.undo_turn_right_on_self(left_motor, right_motor)
