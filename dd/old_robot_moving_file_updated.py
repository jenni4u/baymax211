from utils.brick import Motor, BP, wait_ready_sensors, TouchSensor, reset_brick
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
DISTANCE_ENTER = 6.5

#------------- SETUP -------------#
emergency_stop = False
right_motor = Motor("C")
left_motor = Motor("B")
touch_sensor = TouchSensor(4)
wait_ready_sensors()
pendulum_mvt.scanner_motor.reset_encoder()
pendulum_mvt.drop_motor.reset_encoder()
right_motor.reset_encoder()
left_motor.reset_encoder()

# ============================================
# EMERGENCY STOP HELPERS  (MINIMAL ADDITIONS)
# ============================================
def wheels_stop():
    right_motor.set_dps(0)
    left_motor.set_dps(0)
    pendulum_mvt.drop_motor.set_dps(0)
    pendulum_mvt.scanner_motor.set_dps(0)

def emergency_triggered():
    return pendulum_mvt.emergency_stop  # use pendulum’s global flag

def safe_sleep(t):
    """Sleep in chunks so emergency stop interrupts immediately."""
    for _ in range(int(t * 20)):
        if emergency_triggered():
            wheels_stop()
            pendulum_mvt.emergency_stop_arms()
            return
        time.sleep(0.05)

#-------- MOVE THE ROBOT ------------#
def move_robot(distance, dps):

    ### EMERGENCY
    if emergency_triggered():
        wheels_stop()
        pendulum_mvt.emergency_stop_arms()
        return

    right_motor.set_dps(dps)
    left_motor.set_dps(dps)

    left_motor.set_position_relative(-distance * DISTTODEG)
    right_motor.set_position_relative(-distance * DISTTODEG)


def move_back_after_scanning(total_distance):

    wheels_stop()

    ### EMERGENCY
    if emergency_triggered():
        pendulum_mvt.emergency_stop_arms()
        return

    pendulum_mvt.reset_both_motors_to_initial_position()
    safe_sleep(1)

    if emergency_triggered():
        return

    move_robot(-(total_distance + DISTANCE_PER_SCANNING - DISTANCE_ENTER), 250) 


def package_delivery(total_distance, delivery_counter):

    ### EMERGENCY
    if emergency_triggered():
        wheels_stop()
        pendulum_mvt.emergency_stop_arms()
        return

    drop_angle = 0
    initial_color_angle = pendulum_mvt.scanner_motor.get_position()

    if delivery_counter == 0:
        angle_movement = 30
    else:
        angle_movement = 50
        
    if initial_color_angle < 0:
        drop_angle = initial_color_angle + angle_movement
    else:
        drop_angle = initial_color_angle - angle_movement

    #pendulum_mvt.scanner_motor.set_dps(50)
    pendulum_mvt.scanner_motor.set_position(drop_angle)
    safe_sleep(1.5)

    if emergency_triggered():
        pendulum_mvt.emergency_stop_arms()
        return

    pendulum_mvt.scanner_motor.set_dps(0)

    #pendulum_mvt.scanner_motor.set_dps(50)
    pendulum_mvt.scanner_motor.set_position(initial_color_angle)
    safe_sleep(1.5)

    pendulum_mvt.scanner_motor.set_dps(0)

    pendulum_mvt.reset_both_motors_to_initial_position()
    safe_sleep(1)

    if emergency_triggered():
        return

    remaining = abs(DISTANCE_ENTER - (total_distance + DISTANCE_PER_SCANNING))

    if total_distance < DISTANCE_ENTER:
        move_robot(remaining, 150)
    else:
        move_robot(-remaining, 150)

    
    safe_sleep(0.05 + remaining * DISTTODEG / 150)
    


def scan_room(delivery_counter):

    total_distance = 0
    wheels_stop()
    left_motor.set_position_relative(0)
    right_motor.set_position_relative(0)
    time.sleep(0.05)

    position = "left"

    try:
        count_orange = 0
        right_motor.set_dps(150)
        left_motor.set_dps(150)

        while count_orange < 3 and not emergency_triggered():

            try:
                R, G, B, L = pendulum_mvt.color_sensor.get_value()
                color = pendulum_mvt.color_detection_algorithm.classify_the_color(R, G, B)
                if color == "orange":
                    print(color)
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
                pendulum_mvt.emergency_stop_arms()
                return False
                

            if total_distance >= MAX_ROOM_DISTANCE:
                move_back_after_scanning(total_distance)
                return False
                

            move_robot(DISTANCE_PER_SCANNING, 150)
            total_distance += DISTANCE_PER_SCANNING
            safe_sleep(0.05 + DISTANCE_PER_SCANNING * DISTTODEG / 150)
            

            if emergency_triggered():
                return False
                

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
                move_robot(DISTANCE_ENTER - total_distance - DISTANCE_PER_SCANNING, 150) 
                return False
                

            elif color == "green":
                wheels_stop()
                package_delivery(total_distance, delivery_counter)
                total_distance = 0
                return True 
                

    except BaseException as error:
        print("Error during scan_room:", error)
        BP.reset_all()

def monitor_touch_sensor():
    """Continuously monitor the touch sensor and trigger emergency stop."""
    while True:
        if touch_sensor.is_pressed():
            print("TOUCH SENSOR PRESSED! Emergency stop triggered!")
            # Set emergency stop flags
            global emergency_stop
            emergency_stop = True
            pendulum_mvt.emergency_stop = True
            # Your helper function will handle stopping wheels and pendulum
            wheels_stop()            # stops the wheels
            pendulum_mvt.emergency_stop_arms()  # stops both pendulum motors
            reset_brick()
            break
        time.sleep(0.05)

if __name__ == "__main__":
    touch_thread = threading.Thread(target=monitor_touch_sensor)
    touch_thread.daemon = True
    touch_thread.start()
    scan_room(0)
