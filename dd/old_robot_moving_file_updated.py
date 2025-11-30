from utils.brick import Motor, BP, wait_ready_sensors, TouchSensor
import math
import time
import old_pendulum_file_updated as pendulum_mvt
import threading

#-------- MOVEMENT PARAMETERS -----------#
RADIUS = 2 #radius of wheel in cm
DISTTODEG = 360 / (2 * math.pi * RADIUS)

#-------- CONSTANTS -----------#
DPS = 50
MAX_ROOM_DISTANCE = 22
DISTANCE_PER_SCANNING = 2.8/2
DISTANCE_ENTER = 9

#------------- SETUP -------------#
emergency_stop = False
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")
TOUCH_SENSOR = TouchSensor(4)
wait_ready_sensors()
pendulum_mvt.motor_color_sensor.reset_encoder()
pendulum_mvt.motor_block.reset_encoder()
RIGHT_WHEEL.reset_encoder()
LEFT_WHEEL.reset_encoder()

# ============================================
# EMERGENCY STOP HELPERS  (MINIMAL ADDITIONS)
# ============================================
def wheels_stop():
    RIGHT_WHEEL.set_dps(0)
    LEFT_WHEEL.set_dps(0)

def emergency_triggered():
    return pendulum_mvt.emergency_stop  # use pendulum’s global flag

def safe_sleep(t):
    """Sleep in chunks so emergency stop interrupts immediately."""
    for _ in range(int(t * 20)):
        if emergency_triggered():
            wheels_stop()
            pendulum_mvt.stop_all_arms()
            return
        time.sleep(0.05)

#-------- MOVE THE ROBOT ------------#
def move_robot(distance, dps):

    ### EMERGENCY
    if emergency_triggered():
        wheels_stop()
        pendulum_mvt.stop_all_arms()
        return

    RIGHT_WHEEL.set_dps(dps)
    LEFT_WHEEL.set_dps(dps)

    LEFT_WHEEL.set_position_relative(-distance * DISTTODEG)
    RIGHT_WHEEL.set_position_relative(-distance * DISTTODEG)

    ### EMERGENCY DURING MOTION
    for _ in range(40):
        if emergency_triggered():
            wheels_stop()
            pendulum_mvt.stop_all_arms()
            return
        time.sleep(0.05)


def move_back_after_scanning(total_distance):

    wheels_stop()

    ### EMERGENCY
    if emergency_triggered():
        pendulum_mvt.stop_all_arms()
        return

    pendulum_mvt.reset_both_motors_to_initial_position()
    safe_sleep(1)

    if emergency_triggered():
        return

    move_robot(-(total_distance - DISTANCE_ENTER), 250)


def package_delivery(total_distance, delivery_counter):

    ### EMERGENCY
    if emergency_triggered():
        wheels_stop()
        pendulum_mvt.stop_all_arms()
        return

    drop_angle = 0
    initial_color_angle = pendulum_mvt.motor_color_sensor.get_position()

    if delivery_counter == 0:
        angle_movement = 30
    else:
        angle_movement = 50
        
    if initial_color_angle < 0:
        drop_angle = initial_color_angle + angle_movement
    else:
        drop_angle = initial_color_angle - angle_movement

    pendulum_mvt.motor_color_sensor.set_dps(50)
    pendulum_mvt.motor_color_sensor.set_position(drop_angle)
    safe_sleep(2.5)

    if emergency_triggered():
        pendulum_mvt.stop_all_arms()
        return

    pendulum_mvt.motor_color_sensor.set_dps(0)

    pendulum_mvt.motor_color_sensor.set_dps(pendulum_mvt.MOTOR_DPS - 100)
    pendulum_mvt.motor_color_sensor.set_position(initial_color_angle)
    safe_sleep(1.5)

    pendulum_mvt.motor_color_sensor.set_dps(0)

    pendulum_mvt.reset_both_motors_to_initial_position()
    safe_sleep(1)

    if emergency_triggered():
        return

    remaining = abs(DISTANCE_ENTER - (total_distance + DISTANCE_PER_SCANNING))

    if total_distance < DISTANCE_ENTER:
        move_robot(remaining, 150)
    else:
        move_robot(-remaining, 150)

    safe_sleep(1)


def scan_room(delivery_counter):

    total_distance = 0
    wheels_stop()
    LEFT_WHEEL.set_position_relative(0)
    RIGHT_WHEEL.set_position_relative(0)
    time.sleep(0.05)

    position = "left"

    try:
        count_orange = 0
        RIGHT_WHEEL.set_dps(150)
        LEFT_WHEEL.set_dps(150)

        while count_orange < 5 and not emergency_triggered():

            try:
                R, G, B, L = pendulum_mvt.COLOR_SENSOR.get_value()
                color = pendulum_mvt.color_detection_algorithm.classify_the_color(R, G, B)
                if color == "orange":
                    count_orange += 1
                else:
                    count_orange = 0
            except Exception:
                pass

            time.sleep(0.05)

        wheels_stop()

        while True:

            ### EMERGENCY
            if emergency_triggered():
                wheels_stop()
                pendulum_mvt.stop_all_arms()
                break

            if total_distance >= MAX_ROOM_DISTANCE:
                move_back_after_scanning(total_distance)
                break

            move_robot(DISTANCE_PER_SCANNING, 150)
            total_distance += DISTANCE_PER_SCANNING
            safe_sleep(1.5)

            if emergency_triggered():
                break

            color = pendulum_mvt.main_pendulum(position)

            if position == "right":
                position = "left"
            else:
                position = "right"

            if color == "red":
                wheels_stop()
                safe_sleep(1.5)
                pendulum_mvt.reset_both_motors_to_initial_position()
                safe_sleep(1)
                move_robot(DISTANCE_ENTER - DISTANCE_PER_SCANNING*3, 150)
                break

            elif color == "green":
                wheels_stop()
                package_delivery(total_distance, delivery_counter)
                total_distance = 0
                break

    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()

def monitor_touch_sensor():
    """Continuously monitor the touch sensor and trigger emergency stop."""
    while True:
        if TOUCH_SENSOR.is_pressed():
            print("TOUCH SENSOR PRESSED! Emergency stop triggered!")
            # Set emergency stop flags
            global emergency_stop
            emergency_stop = True
            pendulum_mvt.emergency_stop = True
            # Your helper function will handle stopping wheels and pendulum
            wheels_stop()            # stops the wheels
            pendulum_mvt.stop_all_arms()  # stops both pendulum motors
            break
        time.sleep(0.05)

if __name__ == "__main__":
    touch_thread = threading.Thread(target=monitor_touch_sensor)
    touch_thread.daemon = True
    touch_thread.start()
    scan_room(0)
