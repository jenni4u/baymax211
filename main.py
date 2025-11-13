from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep
from movement.line_follower import move_straight, turn_right_90

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
color_sensor = EV3ColorSensor(1, mode="red")              

wait_ready_sensors(True)

move_straight(left_motor, right_motor, color_sensor, distance=50)
turn_right_90(left_motor, right_motor, color_sensor)
