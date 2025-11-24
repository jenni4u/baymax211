from utils.brick import Motor, wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor, busy_sleep, TouchSensor
from return_home import return_home
import line_follower as lf

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


if __name__ == "__main__":

    # counters    
    delivery_counter = 0
    room_counter = 0

    for i in range(len(INTERSECTION_PATTERN)):

        # move until next intersection
        lf.line_follower(left_motor=left_motor, right_motor=right_motor, color_sensor=color_sensor)

        if INTERSECTION_PATTERN[i] == ROOM:
            print("At meeting room, turning left 90 degrees")

            # enter and scan room
            lf.turn_room(left_motor, right_motor)
            #TODO: add room scanning function here, have it return True upon successful delivery
            # if SCANNING_FUNCTION():
            #     delivery_counter += 1
            #     print(f"Delivery successful! Total deliveries: {delivery_counter}")
            lf.undo_turn_room(left_motor, right_motor)
            
            # update room number
            room_counter += 1

            # go back to storage room if 2 deliveries completed
            if delivery_counter == 2:
                print("All deliveries completed.")
                return_home(room_counter)
                break

        elif INTERSECTION_PATTERN[i] == CORNER:
            print("At new edge, smooth turning left")
            lf.smooth_turn(left_motor, right_motor)

        elif INTERSECTION_PATTERN[i] == ST_ROOM:
            print("At storage room, skipping for now")
            lf.line_follower_distance(3)






