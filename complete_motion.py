from motion import move_forward, reset
from utils.brick import wait_ready_sensors, EV3UltrasonicSensor, EV3ColorSensor

# --- Constants --- #
CRITICAL_DISTANCES = {
    1: [],
    2: [86.8],
    3: [86.8],
    4: [86.8, 36.8],
}
LINE_COLOR = "black"  # Color of the line to follow
STEP_DISTANCE = 0.3  # Distance to move forward in small steps (cm)
WALL_DISTANCE = 10

# --- Sensors --- #
ULTRASOUND_SENSOR = EV3UltrasonicSensor(2)
COLOR_SENSOR = EV3ColorSensor(3)
wait_ready_sensors()
print("Sensors are ready!")

# --- Global Variables --- #
payload_count = 2  # Number of payloads to deliver
rooms_visited = 0

# --- Helper Functions --- #
# def check_line():
#     """Check if the robot is still on the black line."""
#     color = COLOR_SENSOR.get_color()
#     if color != LINE_COLOR:
#         fix_path()

# def fix_path():
#     """Correct the robot's path if it deviates from the black line."""
#     print("Fixing path...")
#     # Logic to adjust the robot's position back to the line

def check_critical_distance(critical_distance):
    """Check if the robot is at a critical distance using the ultrasonic sensor."""
    distance = ULTRASOUND_SENSOR.get_value()
    return distance <= critical_distance

def follow_edge(critical_distances):
    """Follow an edge of the square, checking critical distances."""
    global payload_count
    for critical_distance in critical_distances:
        while not check_critical_distance(critical_distance):
            move_forward(STEP_DISTANCE)
            # check_line()
        motion.turn(1)
        #scan_room() -- returns a boolean if payload is needed
        rooms_visited += 1

    motion.turn(0)
    #stop at the entrance of the room where we dropped the last package
    if payload_count == 0:
        return

    # Go to the wall after finishing the edge
    while not check_critical_distance(WALL_DISTANCE):
        move_forward(step_DISTANCE)
        check_line()

# --- Main Logic --- #
def navigate_to_rooms():
    for edge_number in CRITICAL_DISTANCES:
        critical_distances = CRITICAL_DISTANCES[edge_number]
        follow_edge(critical_distances)
        if payload_count == 0:
            break
        motion.turn(1) 
        
# --- Start Navigation --- #
navigate_to_rooms()