from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, TouchSensor, busy_sleep
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils


#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 120
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
    print(f"Detected color: {color}")
    print("Stopping arms movement.")


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

                if color == "green":
                    count_green += 1
                    count_red = 0
                elif color == "red":
                    count_red += 1
                    count_green = 0
                else:
                    count_green = 0
                    count_red = 0

                if count_green >= 3:
                    color="green"
                    stop_the_arms_movement(color)
                    sounds_utils.play_wav("success.wav")
                    return  # Exit immediately after detecting green

                if count_red >= 3:
                    color = "red"
                    stop_the_arms_movement(color)
                    return  # Exit immediately after detecting red

        except SensorError:
            print("Color sensor read error")
        
        # Small delay to prevent overwhelming the sensor and bus
        time.sleep(0.01)

    return None


#============================================================
# MOTOR MOVEMENT (INTERRUPTIBLE)
#============================================================
def move_both_motors(position):
    """Move both scanner and drop motors simultaneously."""
    global stopped_color_detection, emergency_stop, stopped_scanner_motor, stopped_drop_motor

    print("System is Ready!")

    if emergency_stop or stopped_color_detection:
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        return

    time.sleep(0.01)

    if emergency_stop:
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        return

    # Start both motors moving simultaneously
    if position == "right":
        scanner_motor.set_dps(-MOTOR_DPS)
        drop_motor.set_dps(-MOTOR_DPS)
        
        # Wait until both reach target position
        while True:
            if stopped_color_detection or emergency_stop:
                scanner_motor.set_dps(0)
                drop_motor.set_dps(0)
                return
            
            scanner_reached = scanner_motor.get_position() <= LEFT_POSITION
            drop_reached = drop_motor.get_position() <= LEFT_POSITION
            
            if scanner_reached and drop_reached:
                break
            
            busy_sleep(0.025)
        
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        
      

    elif position == "left":
        scanner_motor.set_dps(MOTOR_DPS)
        drop_motor.set_dps(MOTOR_DPS)
        
        # Wait until both reach target position
        while True:
            if stopped_color_detection or emergency_stop:
                scanner_motor.set_dps(0)
                drop_motor.set_dps(0)
                return
            
            scanner_reached = scanner_motor.get_position() >= RIGHT_POSITION
            drop_reached = drop_motor.get_position() >= RIGHT_POSITION
            
            if scanner_reached and drop_reached:
                break
            
            busy_sleep(0.01)
        
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
    
    # Mark both motors as stopped
    stopped_scanner_motor = True
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
        motors_thread = threading.Thread(target=move_both_motors, args=(position,))

        color_thread.start()
        motors_thread.start()

        color_thread.join()
        motors_thread.join()
        
        # Explicit cleanup to prevent resource accumulation
        time.sleep(0.05)  # Allow threads to fully terminate
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)

        print("done")
        return detected_color

    except SensorError:
        print("error")


#============================================================
# RESET MOTORS (INTERRUPTIBLE)
#============================================================
def reset_both_motors_to_initial_position():
    """Reset both motors to initial position (0 degrees) simultaneously."""
    global emergency_stop

    if emergency_stop:
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        return

    # Determine direction for each motor
    scanner_pos = scanner_motor.get_position()
    drop_pos = drop_motor.get_position()
    
    scanner_reached = abs(scanner_pos) < 3
    drop_reached = abs(drop_pos) < 3
    # Start both motors moving toward 0
    
    if scanner_reached or drop_reached:
        return
    
    if scanner_pos > 0:
        scanner_motor.set_dps(-25)
    else:
        scanner_motor.set_dps(25)
    
    if drop_pos > 0:
        drop_motor.set_dps(-25)
    else:
        drop_motor.set_dps(25)

    
    # Wait until both reach initial position (detect sign change crossing zero)
    while True:
        if emergency_stop:
            scanner_motor.set_dps(0)
            drop_motor.set_dps(0)
            return
        
        scanner_curr_pos = scanner_motor.get_position()
        drop_curr_pos = drop_motor.get_position()
        
        # Check if motor has crossed zero (sign changed from initial position)
        scanner_reached = (scanner_pos > 0 and scanner_curr_pos <= 0) or (scanner_pos < 0 and scanner_curr_pos >= 0)
        drop_reached = (drop_pos > 0 and drop_curr_pos <= 0) or (drop_pos < 0 and drop_curr_pos >= 0)
        
        if scanner_reached and drop_reached:
            scanner_motor.set_dps(0)
            drop_motor.set_dps(0)
            break
        
        time.sleep(0.01)
    
    


#============================================================
if __name__ == "__main__":
    main_pendulum("left")
