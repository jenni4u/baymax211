from utils.brick import Motor, TouchSensor, BP, wait_ready_sensors, EV3ColorSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time

#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 50
TIME_SLEEP = 0.5

#----- Color detection object -----#
csa = ColorDetectionAlgorithm()
COLOR_SENSOR = EV3ColorSensor(4)
counter = 0
color = None

#------------- SETUP -------------#
#ULTRASOUND_SENSOR = EV3UltrasonicSensor(2)
#TOUCH_SENSOR = TouchSensor(1)
motor = Motor("D")
motor.reset_encoder()
wait_ready_sensors()
print('System is Ready!')

#if TOUCH_SENSOR.is_pressed():
#    print("Don't start with the button pressed!")
#    exit()

#---------- LOOP LOGIC ----------#
try:
    #First while loop check for button press to start the motor arm
    while True:
        try: 
            #if TOUCH_SENSOR.is_pressed():

            values = COLOR_SENSOR.get_value()
        
            if values:
                R, G, B, L = values
                color = csa.classify_the_color(R, G, B)
                if (color == "green" or color== "red"):
                    print(color)

                #if(color == "red" or color == "green"):
                    #break
                    
            motor.set_dps(MOTOR_DPS)
            motor.set_position(LEFT_POSITION)
            time.sleep(TIME_SLEEP)
            motor.set_position(INITIAL_POSITION)
            time.sleep(TIME_SLEEP)
            motor.set_position(RIGHT_POSITION)
            time.sleep(TIME_SLEEP)
            motor.set_position(INITIAL_POSITION)
            time.sleep(TIME_SLEEP)

        

        except SensorError as error:
            print("Sensor error:", error)
            break
        
except KeyboardInterrupt:
    motor.set_dps(MOTOR_DPS)
    motor.set_position(INITIAL_POSITION)
    time.sleep(1)
    BP.reset_all()
except BaseException as error:
    BP.reset_all()