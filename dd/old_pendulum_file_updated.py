from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, TouchSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
from playsound3 import playsound


#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 150
TIME_SLEEP = 1.5
COLOR_SENSOR = EV3ColorSensor(3)
TOUCH_SENSOR = TouchSensor(4)

#------------- SETUP -------------#
motor_color_sensor = Motor("A") 
motor_block = Motor("D")  
wait_ready_sensors()
motor_color_sensor.reset_encoder()
motor_block.reset_encoder()


# COLOR CLASSIFICATION
color_detection_algorithm = ColorDetectionAlgorithm()


#------------- GLOBAL CONTROL FLAGS -------------#
emergency_stop = False
stopped_motor_block = False
stopped_motor_color_sensor = False



#============================================================
# STOP LOGIC
#============================================================
def stop_the_arms_movement(color):
    global detected_color, stopped_color_detection, emergency_stop

    detected_color = color
    stopped_color_detection = True
    emergency_stop = True

    motor_color_sensor.set_dps(0)
    motor_block.set_dps(0)


def emergency_stop_arms():
    global emergency_stop
    emergency_stop = True
    motor_color_sensor.set_dps(0)
    motor_block.set_dps(0)


#============================================================
# COLOR SENSOR SAMPLING
#============================================================
def color_sample():
    global detected_color, stopped_color_detection

    count_green = 0
    count_red = 0

    while (not emergency_stop
           and not stopped_color_detection
           and not stopped_motor_block
           and not stopped_motor_color_sensor):

        if emergency_stop:
            motor_color_sensor.set_dps(0)
            motor_block.set_dps(0)
            return None

        try:
            values = COLOR_SENSOR.get_value()
            if not values:
                continue

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
                stop_the_arms_movement("green")
                sounds_utils.play_wav("balalala.wav")
                return "green"

            if count_red >= 5:
                stop_the_arms_movement("red")
                return "red"

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

        # INTERRUPTIBLE wait
#         while abs(motor.get_position() - target) > 3:
#             if emergency_stop or stopped_color_detection:
#                 motor.set_dps(0)
#                 return
#             time.sleep(0.01)

    if position == "left":
        
        motor.set_position(RIGHT_POSITION)
        
        for _ in range(100):
                if stopped_color_detection or emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)
    
    

        # INTERRUPTIBLE wait
#         while abs(motor.get_position() - target) > 3:
#             if emergency_stop or stopped_color_detection:
#                 motor.set_dps(0)
#                 return
#             time.sleep(0.01)


#============================================================
# PENDULUM ARM
#============================================================
def move_motor_pendulum(position):
    global stopped_motor_color_sensor

    if emergency_stop:
        motor_color_sensor.set_dps(0)
        return

    move_motor(motor_color_sensor, position)

    motor_color_sensor.set_dps(0)
    #stopped_motor_color_sensor = True


#============================================================
# BLOCK ARM
#============================================================
def move_motor_block(position):
    global stopped_motor_block

    if emergency_stop:
        motor_block.set_dps(0)
        return

    move_motor(motor_block, position)

    motor_block.set_dps(0)
    #stopped_motor_block = True


#============================================================
# RUN ALL THREADS TOGETHER
#============================================================
def main_pendulum(position):
    global detected_color, emergency_stop
    global stopped_color_detection, stopped_motor_block, stopped_motor_color_sensor

    detected_color = None
    stopped_color_detection = False
    stopped_motor_block = False
    stopped_motor_color_sensor = False
    emergency_stop = False

    try:
        color_thread = threading.Thread(target=color_sample)
        pendulum_thread = threading.Thread(target=move_motor_pendulum, args=(position,))
        block_thread = threading.Thread(target=move_motor_block, args=(position,))

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

    motor.set_dps(50)
    motor.set_position(INITIAL_POSITION)

    # INTERRUPTIBLE wait
    while abs(motor.get_position() - INITIAL_POSITION) > 3:
        if emergency_stop:
            motor.set_dps(0)
            return
        time.sleep(0.01)

    motor.set_dps(0)


def reset_both_motors_to_initial_position():
    global emergency_stop

    if emergency_stop:
        motor_color_sensor.set_dps(0)
        motor_block.set_dps(0)
        return

    t1 = threading.Thread(target=reset_motor_to_initial_position, args=(motor_color_sensor,))
    t2 = threading.Thread(target=reset_motor_to_initial_position, args=(motor_block,))

    t1.start()
    t2.start()

    # INTERRUPTIBLE wait for both
    while t1.is_alive() or t2.is_alive():
        if emergency_stop:
            motor_color_sensor.set_dps(0)
            motor_block.set_dps(0)
            return
        time.sleep(0.01)

    t1.join()
    t2.join()


#============================================================
if __name__ == "__main__":
    main_pendulum()
