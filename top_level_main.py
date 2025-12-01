from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep, TouchSensor, reset_brick
from playsound3 import playsound
import return_home as rt
import old_robot_moving_file_updated as robot_scanner
import old_pendulum_file_updated as pendulum_scanner
#from robot_moving_in_the_room import RobotScannerOfRoom
import line_follower as lf
import threading
import time

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
scanner_motor = Motor("A")  # Assuming motor A is for the scanner
drop_motor = Motor("D")     # Assuming motor D is for dropping blocks
color_sensor = EV3ColorSensor(3)
touch_sensor = TouchSensor(4)

drop_motor.reset_encoder()
scanner_motor.reset_encoder()
drop_motor.set_position(0)
scanner_motor.set_position(0)

#scanner_room = RobotScannerOfRoom(scanner_motor, drop_motor, color_sensor, right_motor, left_motor)
color_sensor.set_mode("red")
wait_ready_sensors(True)


# INTERSECTION PATTERN
ROOM = 0     # Meeting Room
ST_ROOM = 1  # Storage Room
CORNER = 2   # at corner
        
INTERSECTION_PATTERN = [ROOM, ST_ROOM, ROOM,
                        CORNER, ST_ROOM, ROOM,
                        CORNER, ST_ROOM, ROOM,
                        CORNER, ST_ROOM]   

def emergency_stop_monitor():
    """Monitor touch sensor for emergency stop signal."""
    print("Emergency stop monitor started. Press touch sensor to stop.")
    while not lf.emergency_stop:
        try:
            if touch_sensor.is_pressed():
                print("\n*** EMERGENCY STOP ACTIVATED ***")
                lf.emergency_stop = True

                
                robot_scanner.emergency_stop = True
                pendulum_scanner.emergency_stop = True
                robot_scanner.wheels_stop()            # stops the wheels
                pendulum_scanner.emergency_stop_arms()  # stops both pendulum motors


                lf.stop()
                BP.reset_all()
                reset_brick()
            time.sleep(0.05)  # Check every 50ms
        except Exception as e:
            print(f"Error in emergency stop monitor: {e}")
            break
        
if __name__ == "__main__":
    
    stop_thread = threading.Thread(target=emergency_stop_monitor, daemon=True)
    stop_thread.start()

    # counters    
    delivery_counter = 0
    room_counter = 0

    playsound("./sounds/start.wav")

    lf.line_follower_distance(2.0, -1.3, left_motor, right_motor, color_sensor, -80, 24)

    for i in range(len(INTERSECTION_PATTERN)):
        
        if lf.emergency_stop:
                print("Operation cancelled due to emergency stop.")
                break
        
        # move until next intersection
        reading = lf.line_follower(left_motor=left_motor, right_motor=right_motor, color_sensor=color_sensor)
        print("Stopped because read black value of: ", reading)
        if lf.emergency_stop:
                break
            
            
        if INTERSECTION_PATTERN[i] == ROOM:
            print("At meeting room, turning left 90 degrees")

            # enter and scan room
            lf.turn_room(left_motor, right_motor)
            
            if lf.emergency_stop:
                    break
                
            color_sensor.set_mode("component")
            wait_ready_sensors(True)
            
            pendulum_scanner.reset_both_motors_to_initial_position()
            if robot_scanner.scan_room(delivery_counter):
                print("did the scanning")
                delivery_counter += 1
                playsound('./sounds/success.wav')
                print(f"Delivery successful! Total deliveries: {delivery_counter}")
            time.sleep(3)
            color_sensor.set_mode("red")
            wait_ready_sensors(True)
            
            lf.undo_turn_room(left_motor, right_motor)
            lf.line_follower_distance(4, -1.8, left_motor, right_motor, color_sensor, -80, 24) #aggressive correction
            if lf.emergency_stop:
                    break
            
            # update room number
            room_counter += 1
            if room_counter == 4:
                rt.return_home(room_counter)
                break

            # go back to storage room if 2 deliveries completed
            if delivery_counter == 2:
                busy_sleep(1)
                print("All deliveries completed.")
                rt.return_home(room_counter)
                playsound("./sounds/complete.wav")
                break

        elif INTERSECTION_PATTERN[i] == CORNER:
            print("At new edge, smooth turning left")
            lf.smooth_turn(left_motor, right_motor)
            if lf.emergency_stop:
                    break


        elif INTERSECTION_PATTERN[i] == ST_ROOM:
            print("At storage room, skipping for now")
            lf.move_forward(3)






