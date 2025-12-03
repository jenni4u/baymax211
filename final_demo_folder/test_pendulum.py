from utils.brick import Motor, BP, wait_ready_sensors, EV3ColorSensor, TouchSensor, busy_sleep
from brickpi3 import SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils
import old_pendulum_file_updated as pendulum_mvt

scanner_motor = Motor("A") 
drop_motor = Motor("D")  
wait_ready_sensors()
scanner_motor.reset_encoder()
drop_motor.reset_encoder()


if __name__ == "__main__":
    #main_pendulum("left")
    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)
    time.sleep(5)
    
    drop_motor.set_dps(0)
    print(scanner_motor.get_position())
    print(drop_motor.get_position())
    scanner_motor.set_dps(-50)
    drop_motor.set_dps(-50)
    while True:
        scanner_done = scanner_motor.get_position() <= -50
        drop_done = drop_motor.get_position() <= -50
        if (scanner_done):
            scanner_motor.set_dps(0)
        if (drop_done):
            drop_motor.set_dps(0)
        
        if(scanner_done and drop_done):
            break
    
#     drop_motor.set_position_relative(50)
#     busy_sleep(5)
    print("NEWWWW")
    print(scanner_motor.get_position())
    print(drop_motor.get_position())
    pendulum_mvt.reset_both_motors_to_initial_position()
#    busy_sleep(3)
#     print("ENDDDD")

   
    print(scanner_motor.get_position())
    print(drop_motor.get_position())