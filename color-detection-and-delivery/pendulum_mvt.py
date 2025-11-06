from utils.brick import Motor, TouchSensor, BP, wait_ready_sensors, EV3ColorSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time

#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 50
TIME_SLEEP = 1

#----- Color detection object -----#
csa = ColorDetectionAlgorithm()
COLOR_SENSOR = EV3ColorSensor(4)
counter_green = 0
counter_red = 0
detected_color = None
color_found = False

#------------- SETUP -------------#
#ULTRASOUND_SENSOR = EV3UltrasonicSensor(2)
#TOUCH_SENSOR = TouchSensor(1)
motor = Motor("D")


#---------- COLOR CLASSIFICATION ----------#
def color_sample():
    for _ in range(int(TIME_SLEEP / 0.05)):
        values = COLOR_SENSOR.get_value()

        if values:
            R, G, B, L = values
            color = csa.classify_the_color(R, G, B)
            print(color)

            if color == "green":
                count_green+=1
                count_red = 0
            elif color == "red":
                count_red+=1 
                count_green = 0
            else:
                count_green = 0
                count_red = 0

            if (count_green >=5) or (count_red >=5):
                return color
        time.sleep(0.05)
    return None

#---------- MAIN FUNCTION ----------#
def main():
    wait_ready_sensors()
    motor.reset_encoder()
    print('System is Ready!')
    try:
        while True:
            try: 
                #if TOUCH_SENSOR.is_pressed():

                if color_found:
                    motor.set_dps(0)
                    time.sleep(0.1)
                    continue
                        
                motor.set_dps(MOTOR_DPS)
                motor.set_position(LEFT_POSITION)
                detected_color = color_sample()
                if detected_color == "green" or detected_color == "red":
                    color_found = True
                    continue


                motor.set_position(INITIAL_POSITION)
                detected_color = color_sample()
                if detected_color == "green" or detected_color == "red":
                    color_found = True
                    continue


                motor.set_position(RIGHT_POSITION)
                detected_color = color_sample()
                if detected_color == "green" or detected_color == "red":
                    color_found = True
                    continue


                motor.set_position(INITIAL_POSITION)
                detected_color = color_sample()
                if detected_color == "green" or detected_color == "red":
                    color_found = True
                    continue
                    
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

#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
    main()