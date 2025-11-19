from utils.brick import Motor, TouchSensor, BP, wait_ready_sensors, EV3ColorSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time

#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 50
TIME_SLEEP = 1.5

#----- Color detection object -----#
csa = ColorDetectionAlgorithm()
COLOR_SENSOR = EV3ColorSensor(1)
color_found = False

#------------- SETUP -------------#
#ULTRASOUND_SENSOR = EV3UltrasonicSensor(2)
#TOUCH_SENSOR = TouchSensor(1)
motor_pendulum = Motor("D") 
motor_block1 = Motor(3)  
motor_block2 = Motor(4)  
wait_ready_sensors()
motor_pendulum.reset_encoder()
motor_block1.reset_encoder()
motor_block2.reset_encoder()


#---------- COLOR CLASSIFICATION ----------#
def color_sample():
    counter_green = 0
    counter_red = 0

    for _ in range(int(TIME_SLEEP / 0.05)):
        try:
            values = COLOR_SENSOR.get_value()
            if values:
                R, G, B, L = values
                color = csa.classify_the_color(R, G, B)
                #print(color)
                if color == "green" or color == "red":
                    return color
                

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

def set_position_arms(position):
    print("setting position arms")
    motor_pendulum.set_position(position)
    print("setting position arms 1")
    motor_block1.set_position(position)
    print("setting position arms 2")
    motor_block2.set_position(position)
    print("setting position arms 3")

def set_dps_arms(dps):
    print("setting dps arms")
    motor_pendulum.set_dps(dps)
    print("setting dps arms 1")
    motor_block1.set_dps(dps)
    print("setting dps arms 2")
    motor_block2.set_dps(dps)
    print("setting dps arms 3")

def set_power_arms(power):
    print("setting power arms")
    motor_pendulum.set_dps(power)
    print("setting power arms 1")
    motor_block1.set_dps(power)
    print("setting power arms 2")
    motor_block2.set_dps(power)
    print("setting power arms 3")

def detected_color_algorithm(position, dps, power) :
    print("setting detected color algo")
    set_position_arms(position)
    time.sleep(1)
    set_dps_arms(dps)
    set_power_arms(power)


#---------- MAIN FUNCTION ----------#
def find_color(): #find_color()
    detected_color = None

    print('System is Ready!')

    try: 
        #if TOUCH_SENSOR.is_pressed(): 
        set_dps_arms(MOTOR_DPS)
        set_position_arms(LEFT_POSITION)

        detected_color = color_sample()
        if detected_color:
            detected_color_algorithm(INITIAL_POSITION, 0, 0)
            return detected_color


        set_position_arms(INITIAL_POSITION)
  
        detected_color = color_sample()
        if detected_color:
            detected_color_algorithm(INITIAL_POSITION, 0, 0)
            return detected_color


        set_position_arms(RIGHT_POSITION)
    
        detected_color = color_sample()
        if detected_color:
            detected_color_algorithm(INITIAL_POSITION, 0, 0)
            return detected_color


        set_position_arms(INITIAL_POSITION)


        detected_color = color_sample()
        if detected_color:
            detected_color_algorithm(INITIAL_POSITION, 0, 0)
            return detected_color
            
            
    except SensorError as error:
        print("Sensor error:", error)
            
    except KeyboardInterrupt:
        set_dps_arms(MOTOR_DPS)
        set_position_arms(INITIAL_POSITION)
        time.sleep(1)
        BP.reset_all()


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
    find_color()