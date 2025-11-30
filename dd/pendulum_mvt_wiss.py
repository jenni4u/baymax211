from utils.brick import Motor, EV3ColorSensor, SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils

class PendulumScanner:
    #----------- CONSTANTS -----------#
    INITIAL_POSITION = 0
    # The motor_block moves more than the motor_color_arm so its pendulum movement will be less (from -40 to 40)
    LEFT_POSITION = -50
    LEFT_POSITION_2 = -45
    RIGHT_POSITION = 45
    RIGHT_POSITION_2 = 50

    MOTOR_DPS = 150
    TIME_SLEEP = 1.5

    #------------- CONSTRUCTOR -------------#
    def __init__(self, motor_color_sensor, motor_block, color_sensor):

        # Motors for the arms
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block

        # Color sensor
        self.COLOR_SENSOR = color_sensor

        # Color classifier
        self.color_detection_algorithm = ColorDetectionAlgorithm()

        self.initial_color = self.motor_color_sensor.get_position()
        self.initial_block = self.motor_block.get_position()

        # Flags
        self.detected_color = None 
        self.stopped_color_detection = False
        self.stopped_motor_block = False
        self.stopped_motor_color_sensor = False
        
        self.emergency_stop = False



    #---------- COLOR CLASSIFICATION ----------#
    def stop_the_arms_movement(self, color):

        self.detected_color = color
        self.stopped_color_detection = True

        # Stop motors
        self.motor_color_sensor.set_dps(0)
        self.motor_block.set_dps(0)

        # --- REQUIRED FOR EMERGENCY STOP ---
        self.stopped_motor_color_sensor = True
        self.stopped_motor_block = True



    # ----- COLOR SENSOR -----
    def color_sample(self):

        count_green = 0
        count_red = 0

        while not self.stopped_color_detection and not self.stopped_motor_block and not self.stopped_motor_color_sensor:
            
            # EMERGENCY STOP CHECK
            if self.emergency_stop:
                self.stop_the_arms_movement("emergency")
                return "emergency"

            try:
                values = self.COLOR_SENSOR.get_value()
                if values:
                    R, G, B, L = values
                    color = self.color_detection_algorithm.classify_the_color(R, G, B)
                    print(color)

                    if color == "green" and count_green < 5:
                        count_green += 1
                        print(count_green)
                        count_red = 0

                    elif color == "red"and count_red < 5:
                        count_red += 1
                        count_green = 0

                    else:
                        count_green = 0
                        count_red = 0
                    if self.emergency_stop:
                        self.stop_the_arms_movement("emergency")
                        return "emergency"

                    if count_green >= 5:
                        self.stop_the_arms_movement("green")
                        sounds_utils.play_wav("balalala.wav")
                        return "green"

                    if count_red >= 5:
                        self.stop_the_arms_movement("red")
                        return "red"

            except SensorError:
                print("Color sensor read error")
            time.sleep(0.01)

        return None
             

    #---------- ARMS MOVEMENT ----------#
    def get_pos(self, motor):
        if motor == self.motor_color_sensor:
            return self.initial_color
        else:
            return self.initial_block
        

    
    # ----- MOTOR MOVEMENT -----
    def move_motor(self, motor, left, right, position): 

        print('System is Ready!')
        
        motor.set_dps(self.MOTOR_DPS)
        time.sleep(0.01)
        print(self.get_pos(motor))
        
        if self.stopped_color_detection:
            motor.set_dps(0)

        # -------- MOVEMENT LEFT/RIGHT WITH EMERGENCY CHECKS -------- #

        if (position == "right"):
            motor.set_position(self.get_pos(motor) + left)
            

            for _ in range(100):
                if self.stopped_color_detection or self.emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)

  
        if (position == "left"):
            #motor.set_position(right)
            motor.set_position(self.get_pos(motor) + right)

            for _ in range(100):
                if self.stopped_color_detection or self.emergency_stop:
                    motor.set_dps(0)
                    return
                time.sleep(0.01)



    def move_motor_pendulum(self, position):
        self.move_motor(self.motor_color_sensor, self.LEFT_POSITION, self.RIGHT_POSITION, position)
        self.motor_color_sensor.set_dps(0)
        self.stopped_motor_color_sensor = True



    def move_motor_block(self, position):
        self.move_motor(self.motor_block, self.LEFT_POSITION_2, self.RIGHT_POSITION_2, position)
        self.motor_block.set_dps(0)
        self.stopped_motor_block = True   
            



    #------------- JOIN THE 3 SYSTEMS -------------#
    def main_pendulum(self, position):

        self.detected_color = None
        self.stopped_color_detection = False
        self.stopped_motor_block = False
        self.stopped_motor_color_sensor = False

        try:
            color_thread = threading.Thread(target=self.color_sample)
            move_pendulum_thread = threading.Thread(target=self.move_motor_pendulum, args=(position,))
            move_block_thread = threading.Thread(target=self.move_motor_block, args=(position,))

            color_thread.start()
            move_pendulum_thread.start()
            move_block_thread.start()
            
            color_thread.join()      
            move_pendulum_thread.join()
            move_block_thread.join()
            
            print("done")
            return self.detected_color
        
        except SensorError as error:
            print("error")



    #----------- RESET ----------- #
    def reset_motor_to_initial_position(self, motor):
        motor.set_dps(30)
        motor.set_position(0)
        start_time = time.time()
        while time.time() - start_time < 1.5:
            if self.emergency_stop:
                self.stop_the_arms_movement("emergency")
                return
            time.sleep(0.01)
        motor.set_dps(0)

    def reset_both_motors_to_initial_position(self):
        t1 = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_color_sensor,))
        t2 = threading.Thread(target=self.reset_motor_to_initial_position, args=(self.motor_block,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
