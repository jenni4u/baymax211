from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
import line_follower

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
color_sensor = EV3ColorSensor(1, mode="red")              

wait_ready_sensors(True)

line_follower.move_straight(left_motor, right_motor, color_sensor, 90)
#turn_right_90(left_motor, right_motor, color_sensor)

#line_follower.simple_move_straight(left_motor, right_motor, color_sensor, 17.5)
#line_follower.turn_right_on_self(left_motor, right_motor)
#line_follower.undo_turn_right_on_self(left_motor, right_motor)
