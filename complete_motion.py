from motion import move_forward, reset
from utils.brick import wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor

# --- Constants --- #
CRITICAL_DISTANCES_EDGE_2 = [86.8]
CRITICAL_DISTANCES_EDGE_3 = [86.8]
CRITICAL_DISTANCES_EDGE_4 = [86.8, 36.8]
DOOR_DISTANCE = 25  # Distance to check for a door
LINE_COLOR = "black"  # Color of the line to follow
STEP_DISTANCE = 0.5  # Distance to move forward in small steps (cm)

# --- Sensors --- #
ULTRASOUND_SENSOR = EV3UltrasonicSensor(2)
COLOR_SENSOR = EV3ColorSensor(3)
wait_ready_sensors()
print("Sensors are ready!")

# --- Global Variables --- #
payload_count = 2  # Number of payloads to deliver
current_line = 0
rooms_visited = 0

# --- Helper Functions --- #
def check_line():
    """Check if the robot is still on the black line."""
    color = COLOR_SENSOR.get_color()
    if color != LINE_COLOR:
        fix_path()

def fix_path():
    """Correct the robot's path if it deviates from the black line."""
    print("Fixing path...")
    # Logic to adjust the robot's position back to the line

def check_critical_distance(critical_distance):
    """Check if the robot is at a critical distance using the ultrasonic sensor."""
    distance = ULTRASOUND_SENSOR.get_value()
    return distance <= critical_distance

def check_for_door():
    """Check if the robot is at a door by scanning the floor color."""
    color = COLOR_SENSOR.get_color()
    return color == DOOR_COLOR

def follow_edge(critical_distances):
    """Follow an edge of the square, checking critical distances."""
    global payload_count
    for critical_distance in critical_distances:
        if critical_distance == 36.8 and payload_count > 0:
            continue  # Skip this path until all payloads are dropped

        while not check_critical_distance(critical_distance):
            move_forward(STEP_DISTANCE)
            check_line()

        if critical_distance == 36.8:
            # Go down the path to check for a door
            for _ in range(int(DOOR_DISTANCE / STEP_DISTANCE)):
                move_forward(STEP_DISTANCE)
                check_line()

            if check_for_door():
                print("Door found!")
                return  # Stop further movement if a door is found

            # Return to the main path
            for _ in range(int(DOOR_DISTANCE / STEP_DISTANCE)):
                move_forward(-STEP_DISTANCE)
                check_line()

# --- Main Logic --- #
def navigate_to_rooms():
    """Navigate the robot to the entrances of the rooms."""
    # Edge 1: No critical distances
    print("Following Edge 1...")
    for _ in range(int(MAP_LENGTH / STEP_DISTANCE)):
        move_forward(STEP_DISTANCE)
        check_line()

    # Edge 2: Critical distances [86.8, 38.8]
    print("Following Edge 2...")
    follow_edge(CRITICAL_DISTANCES_EDGE_2)

    # Edge 3: Critical distances [86.8, 36.8]
    print("Following Edge 3...")
    follow_edge(CRITICAL_DISTANCES_EDGE_3)

    # Edge 4: Critical distances [86.8, 36.8]
    print("Following Edge 4...")
    follow_edge(CRITICAL_DISTANCES_EDGE_4)

# --- Start Navigation --- #
navigate_to_rooms()