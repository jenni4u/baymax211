from utils.brick import Motor, TouchSensor, BP, wait_ready_sensors, EV3ColorSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading

#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 50
TIME_SLEEP = 1.5

#----- Color detection object -----#
csa = ColorDetectionAlgorithm()
COLOR_SENSOR = EV3ColorSensor(3)
color_found = False

#------------- SETUP -------------#
#ULTRASOUND_SENSOR = EV3UltrasonicSensor(2)
#TOUCH_SENSOR = TouchSensor(1)
motor_pendulum = Motor("D") 
motor_block = Motor("A")  
#TEST = Motor("D")
wait_ready_sensors()
motor_pendulum.reset_encoder()
motor_block.reset_encoder()


#---------- COLOR CLASSIFICATION ----------#
def color_sample():
    counter_green = 0
    counter_red = 0

    global detected_color, stop

    while not stop:
        try:
            values = COLOR_SENSOR.get_value()
            if values:
                R, G, B, L = values
                color = csa.classify_the_color(R, G, B)
                #print(color)
                if color == "green" or color == "red":
                    detected_color = color
                    stop = True
                    return 
                

#                 if color == "green":
#                     count_green+=1
#                     count_red = 0
#                 elif color == "red":
#                     count_red+=1 
#                     count_green = 0
#                 else:
#                     count_green = 0
#                     count_red = 0
# 
#                 if (count_green >=5):
#                     return "green"
# 
#                 if (count_red >=5):
#                     return "red"
        except SensorError:
            print("Color sensor read error")

        time.sleep(0.05)
    return None



#---------- MAIN FUNCTION ----------#
def move_motor_pendulum(): #find_color()

    global stop


    print('System is Ready!')

    try: 
        #if TOUCH_SENSOR.is_pressed(): 
        
        motor_pendulum.set_dps(MOTOR_DPS)

        for pos in [LEFT_POSITION, INITIAL_POSITION, RIGHT_POSITION, INITIAL_POSITION]:
        
            if stop:
                break

            motor_pendulum.set_position(pos)
            time.sleep(1)

        motor_pendulum.set_dps(0)


            
            
    except SensorError as error:
        print("Sensor error:", error)
            
    except KeyboardInterrupt:
        motor_pendulum.set_dps(MOTOR_DPS)
        motor_pendulum.set_position(INITIAL_POSITION)
        time.sleep(1)
        BP.reset_all()


def move_motor_block(): #find_color()
    global stop_signal
    motor_block.set_dps(MOTOR_DPS)

    for pos in [LEFT_POSITION, INITIAL_POSITION, RIGHT_POSITION, INITIAL_POSITION]:
        
        if stop:
            break

        motor_block.set_position(pos)
        time.sleep(1)

    motor_block.set_dps(0)


def main_pendulum():
    global detected_color, stop
    detected_color = None
    stop = False

    try:

        color_thread = threading.Thread(target=color_sample)
        move_pendulum_thread = threading.Thread(target=move_motor_pendulum)
        move_block_thread = threading.Thread(target=move_motor_block)

        color_thread.start()
        move_pendulum_thread.start()
        move_block_thread.start()

        return detected_color

    except KeyboardInterrupt:
       
        motor_pendulum.set_dps(0)
        motor_block.set_dps(0)
        stop = True
        return None


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
 
    main_pendulum()
