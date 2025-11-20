from utils.brick import Motor, TouchSensor, BP, wait_ready_sensors, EV3ColorSensor
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
from utils.sound import play_success


#----------- CONSTANTS -----------#
INITIAL_POSITION = 0
LEFT_POSITION = -45
RIGHT_POSITION = 45
MOTOR_DPS = 150
TIME_SLEEP = 1.5

#SOUND_GREEN = sound.Sound(duration=1, pitch="C5", volume=100)

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
    count_green = 0
    count_red = 0

    global detected_color, stop

    while not stop and not motor_block_done and not motor_pendulum_done:
        try:
            values = COLOR_SENSOR.get_value()
            if values:
                R, G, B, L = values
                color = csa.classify_the_color(R, G, B)
                print(color)
                if color == "green":
                    count_green+=1
                    print(count_green)
                    count_red = 0
                elif color == "red":
                    count_red+=1 
                    count_green = 0
                else:
                    count_green = 0
                    count_red = 0
  
                if (count_green >=5):
                    color = "green"
                    detected_color = color
                    stop = True
                    motor_pendulum.set_dps(0)
                    motor_block.set_dps(0)
                    play_success
                    
                else:
                    color = None
  
                if (count_red >=5):
                    color = "red"
                    detected_color = color
                    stop = True
                    motor_pendulum.set_dps(0)
                    motor_block.set_dps(0)
                
                else:
                    color = None
               
                     
                
        except SensorError:
            print("Color sensor read error")

        
    return None



def move_motor_pendulum(): 

    global stop, motor_pendulum_done


    print('System is Ready!')

    #if TOUCH_SENSOR.is_pressed(): 
        
    motor_pendulum.set_dps(MOTOR_DPS)
    
    if stop:
        motor_pendulum.set_dps(0)
        
    elif(motor_pendulum.get_position() >= 0) :
        motor_pendulum.set_position(LEFT_POSITION)
        time.sleep(1)
    else :
        motor_pendulum.set_position(RIGHT_POSITION)
        time.sleep(1)


    motor_pendulum.set_dps(0)
    motor_pendulum_done = True
        
def move_motor_block(): 

    global stop, motor_block_done


    print('System is Ready!')

     
    #if TOUCH_SENSOR.is_pressed(): 
        
    motor_block.set_dps(MOTOR_DPS)

    if stop:
        motor_block.set_dps(0)
        
    elif(motor_block.get_position() >= 0) :
        motor_block.set_position(LEFT_POSITION)
        time.sleep(1)
    else :
        motor_block.set_position(RIGHT_POSITION)
        time.sleep(1)


    motor_block.set_dps(0)
    motor_block_done = True   
        



def main_pendulum():
    global detected_color, stop, motor_pendulum_done, motor_block_done
    detected_color = None
    stop = False
    motor_pendulum_done = False
    motor_block_done = False

    try:

        color_thread = threading.Thread(target=color_sample)
        move_pendulum_thread = threading.Thread(target=move_motor_pendulum)
        move_block_thread = threading.Thread(target=move_motor_block)

        color_thread.start()
        move_pendulum_thread.start()
        move_block_thread.start()
        
        color_thread.join()
        
        move_pendulum_thread.join()
        move_block_thread.join()
        
    
        print("done")

        return detected_color

        
    except SensorError as error:
       
        print("error")



#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
 
    main_pendulum()
