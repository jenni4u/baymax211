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



#---------- MAIN FUNCTION ----------#
def move_motor_pendulum(): #find_color()
    detected_color = None

    print('System is Ready!')

    try: 
        #if TOUCH_SENSOR.is_pressed(): 
        
        motor_pendulum.set_dps(MOTOR_DPS)
        motor_pendulum.set_position(LEFT_POSITION)

  
    
        detected_color = color_sample()
        if detected_color:
            motor_pendulum.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_pendulum.set_dps(0)
            motor_pendulum.set_power(0)
        

            return detected_color


        motor_pendulum.set_position(INITIAL_POSITION)

        detected_color = color_sample()
        if detected_color:
            motor_pendulum.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_pendulum.set_dps(0)
            motor_pendulum.set_power(0)
            return detected_color


        motor_pendulum.set_position(RIGHT_POSITION)
    
        detected_color = color_sample()
        if detected_color:
            motor_pendulum.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_pendulum.set_dps(0)
            motor_pendulum.set_power(0)

            return detected_color



        motor_pendulum.set_position(INITIAL_POSITION)



        detected_color = color_sample()
        if detected_color:
            motor_pendulum.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_pendulum.set_dps(0)
            motor_pendulum.set_power(0)

            return detected_color
            
            
    except SensorError as error:
        print("Sensor error:", error)
            
    except KeyboardInterrupt:
        motor_pendulum.set_dps(MOTOR_DPS)
        motor_pendulum.set_position(INITIAL_POSITION)
        time.sleep(1)
        BP.reset_all()


def move_motor_block(): #find_color()
    detected_color = None

    print('System is Ready!')

    try: 
        #if TOUCH_SENSOR.is_pressed(): 
        
        motor_block.set_dps(MOTOR_DPS)
        motor_block.set_position(LEFT_POSITION)
  
    
        detected_color = color_sample()
        if detected_color:
            motor_block.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_block.set_dps(0)
            motor_block.set_power(0)
            
            return detected_color


        motor_block.set_position(INITIAL_POSITION)

        detected_color = color_sample()
        if detected_color:
            motor_block.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_block.set_dps(0)
            motor_block.set_power(0)
            
            return detected_color



        motor_block.set_position(RIGHT_POSITION)
    
        detected_color = color_sample()
        if detected_color:
            motor_block.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_block.set_dps(0)
            motor_block.set_power(0)

            return detected_color


        motor_block.set_position(INITIAL_POSITION) 


        detected_color = color_sample()
        if detected_color:
            motor_block.set_position(INITIAL_POSITION)
            time.sleep(1)
            motor_block.set_dps(0)
            motor_block.set_power(0)

            return detected_color
            
            
    except SensorError as error:
        print("Sensor error:", error)
            
    except KeyboardInterrupt:
        motor_block.set_dps(MOTOR_DPS)
        motor_block.set_position(INITIAL_POSITION)
        time.sleep(1)
        BP.reset_all()

def main_pendulum():
    motor_pendulum_thread = threading.Thread(target=move_motor_pendulum)
    motor_block_thread = threading.Thread(target=move_motor_block)
     
    #     # Start them
    motor_pendulum_thread.start()
    motor_block_thread.start()
        

    while True:
        time.sleep(2)
    


#------------- RUNNING MAIN -------------#
if __name__ == "__main__":
 
        
        # Create threads each cycle
        motor_pendulum_thread = threading.Thread(target=move_motor_pendulum)
        motor_block_thread = threading.Thread(target=move_motor_block)
     
    #     # Start them
        motor_pendulum_thread.start()
        motor_block_thread.start()
        
        

        #while True:
            #time.sleep(2)
