from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep, TouchSensor, reset_brick
from return_home import return_home
import line_follower as lf
import threading
import time

# === Initialization ===
left_motor = Motor("B")
right_motor = Motor("C")
color_sensor = EV3ColorSensor(3, mode="red")  
touch_sensor = TouchSensor(4)  
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
                lf.stop()
                reset_brick()
                break
            time.sleep(0.05)  # Check every 50ms
        except Exception as e:
            print(f"Error in emergency stop monitor: {e}")
            break

if __name__ == "__main__":

    # Start emergency stop monitor thread
    stop_thread = threading.Thread(target=emergency_stop_monitor, daemon=True)
    stop_thread.start()

    # counters    
    delivery_counter = 0
    room_counter = 0
    
    try:
        for i in range(len(INTERSECTION_PATTERN)):
            # Check emergency stop before each action
            if lf.emergency_stop:
                print("Operation cancelled due to emergency stop.")
                break

            # move until next intersection
            lf.line_follower(left_motor=left_motor, right_motor=right_motor, color_sensor=color_sensor)
            
            if lf.emergency_stop:
                break

            if INTERSECTION_PATTERN[i] == ROOM:
                print("At meeting room, turning left 90 degrees")

                # enter and scan room
                lf.turn_room(left_motor, right_motor)
                
                if lf.emergency_stop:
                    break
                
                #TODO: add room scanning function here, have it return True upon successful delivery
                # if SCANNING_FUNCTION():
                #     delivery_counter += 1
                #     print(f"Delivery successful! Total deliveries: {delivery_counter}")
                
                lf.undo_turn_room(left_motor, right_motor)
                
                if lf.emergency_stop:
                    break
                
                # update room number
                room_counter += 1

                if room_counter == 4:
                    return_home(room_counter)
                    break

                # go back to storage room if 2 deliveries completed
                if delivery_counter == 2:
                    print("All deliveries completed.")
                    return_home(room_counter)
                    break

            elif INTERSECTION_PATTERN[i] == CORNER:
                print("At new edge, smooth turning left")
                lf.smooth_turn(left_motor, right_motor)
                
                if lf.emergency_stop:
                    break

            elif INTERSECTION_PATTERN[i] == ST_ROOM:
                print("At storage room, skipping for now")
                lf.line_follower_distance(3)
    
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        lf.emergency_stop = True
        lf.stop()
        reset_brick()
    except Exception as e:
        print(f"\nError occurred: {e}")
        lf.emergency_stop = True
        lf.stop()
        reset_brick()
    finally:
        print("Program ended.")
        if not lf.emergency_stop:
            reset_brick()






