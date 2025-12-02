from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, TouchSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils


#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 150
TIME_SLEEP = 1.5
color_sensor = EV3ColorSensor(3)
touch_sensor = TouchSensor(4)

#------------- SETUP -------------#
scanner_motor = Motor("A") 
drop_motor = Motor("D")  
wait_ready_sensors()
scanner_motor.reset_encoder()
drop_motor.reset_encoder()


# COLOR CLASSIFICATION
color_detection_algorithm = ColorDetectionAlgorithm()


#------------- GLOBAL CONTROL FLAGS -------------#
emergency_stop = False
stopped_drop_motor = False
stopped_scanner_motor = False



#============================================================
# STOP LOGIC
#============================================================
def stop_the_arms_movement(color):
    global detected_color, stopped_color_detection

    detected_color = color
    stopped_color_detection = True


    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)


def emergency_stop_arms():
    global emergency_stop
    emergency_stop = True
    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)


#============================================================
# COLOR SENSOR SAMPLING
#============================================================
def color_sample():
    global detected_color, stopped_color_detection

    count_green = 0
    count_red = 0

    while (not emergency_stop
           and not stopped_color_detection
           and not stopped_drop_motor
           and not stopped_scanner_motor):

        if emergency_stop:
            scanner_motor.set_dps(0)
            drop_motor.set_dps(0)
            return None

        try:
            values = color_sensor.get_value()
            if values:

                # Classify the color
                R, G, B, L = values
                color = color_detection_algorithm.classify_the_color(R, G, B)
                print(color)

                if color == "green":
                    count_green += 1
                    count_red = 0
                elif color == "red":
                    count_red += 1
                    count_green = 0
                else:
                    count_green = 0
                    count_red = 0

                if count_green >= 5:
                    color="green"
                    stop_the_arms_movement(color)
                    sounds_utils.play_wav("success.wav")
                else:
                    color = None

                if count_red >= 5:
                    color = "red"
                    stop_the_arms_movement(color)
                else:
                    color = None

        except SensorError:
            print("Color sensor read error")

    return None


#============================================================
# MOTOR MOVEMENT (INTERRUPTIBLE)
#============================================================
def move_motor(motor, position):
    global stopped_color_detection, emergency_stop

    print("System is Ready!")

    if emergency_stop or stopped_color_detection:
        motor.set_dps(0)
        return

    motor.set_dps(MOTOR_DPS)
    time.sleep(0.01)

    if emergency_stop:
        motor.set_dps(0)
        return

    if position == "right":
        
        motor.set_position(LEFT_POSITION)
        
        for _ in range(100):
                if stopped_color_detection or emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)

    if position == "left":
        
        motor.set_position(RIGHT_POSITION)
        
        for _ in range(100):
                if stopped_color_detection or emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)
    
    


#============================================================
# PENDULUM ARM
#============================================================
def move_motor_pendulum(position):
    global stopped_scanner_motor

    if emergency_stop:
        scanner_motor.set_dps(0)
        return

    move_motor(scanner_motor, position)

    scanner_motor.set_dps(0)
    stopped_scanner_motor = True


#============================================================
# BLOCK ARM
#============================================================
def move_drop_motor(position):
    global stopped_drop_motor

    if emergency_stop:
        drop_motor.set_dps(0)
        return

    move_motor(drop_motor, position)

    drop_motor.set_dps(0)
    stopped_drop_motor = True


#============================================================
# RUN ALL THREADS TOGETHER
#============================================================
def main_pendulum(position):
    global detected_color, emergency_stop
    global stopped_color_detection, stopped_drop_motor, stopped_scanner_motor

    detected_color = None
    stopped_color_detection = False
    stopped_drop_motor = False
    stopped_scanner_motor = False
    emergency_stop = False

    try:
        color_thread = threading.Thread(target=color_sample)
        pendulum_thread = threading.Thread(target=move_motor_pendulum, args=(position,))
        block_thread = threading.Thread(target=move_drop_motor, args=(position,))

        color_thread.start()
        pendulum_thread.start()
        block_thread.start()

        color_thread.join()
        pendulum_thread.join()
        block_thread.join()

        print("done")
        return detected_color

    except SensorError:
        print("error")


#============================================================
# RESET MOTORS (INTERRUPTIBLE)
#============================================================
def reset_motor_to_initial_position(motor):
    global emergency_stop

    if emergency_stop:
        motor.set_dps(0)
        return
    
    motor.set_position_kp(5)   # lower force
    motor.set_position_kd(50)  # damping
    motor.set_position(INITIAL_POSITION)

    # INTERRUPTIBLE wait
    for _ in range(100):
        if stopped_color_detection or emergency_stop:
            motor.set_dps(0)
            return
        time.sleep(0.01)
                
 

    motor.set_dps(0)


def reset_both_motors_to_initial_position():
    global emergency_stop

    if emergency_stop:
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        return

    t1 = threading.Thread(target=reset_motor_to_initial_position, args=(scanner_motor,))
    t2 = threading.Thread(target=reset_motor_to_initial_position, args=(drop_motor,))

    t1.start()
    t2.start()

    # INTERRUPTIBLE wait for both
    while t1.is_alive() or t2.is_alive():
        if emergency_stop:
            scanner_motor.set_dps(0)
            drop_motor.set_dps(0)
            return
        time.sleep(0.01)

    t1.join()
    t2.join()


#============================================================
if __name__ == "__main__":
    main_pendulum("left")
