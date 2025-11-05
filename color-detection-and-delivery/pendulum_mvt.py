from utils.brick import Motor, TouchSensor, BP, wait_ready_sensors, EV3UltrasonicSensor
from brickpi3 import SensorError
import time

#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
FIRST_POSITION = -45
SECOND_POSITION = 45
MOTOR_DPS = 250
TIME_SLEEP = 0.5

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
            print("Button pressed!") 
            motor.set_dps(MOTOR_DPS)
            motor.set_position(INITIAL_POSITION)
            time.sleep(TIME_SLEEP)
            motor.set_position(FIRST_POSITION)
            time.sleep(TIME_SLEEP)
            motor.set_position(INITIAL_POSITION)
            time.sleep(TIME_SLEEP)
            motor.set_position(SECOND_POSITION)

        except SensorError as error:
            print("Sensor error:", error)
            break
except BaseException as error:
    BP.reset_all()