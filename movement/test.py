from utils.brick import Motor, EV3ColorSensor, TouchSensor
import line_follower as lf
import return_home as rh
from robot_moving_in_the_room import RobotScannerOfRoom

left_motor = Motor("B")
right_motor = Motor("C")
scanner_motor = Motor("A")  # Assuming motor A is for the scanner
drop_motor = Motor("D")     # Assuming motor D is for dropping blocks
color_sensor = EV3ColorSensor(3)
touch_sensor = TouchSensor(4)

# def test(t):
#     lf.line_follower()
#     print("intersection")
#     lf.move_forward(3)
#     lf.line_follower_distance(17.5, -1.5)
#     print("return home")
#     rh.return_home(t)

def scan():
    scanner_room = RobotScannerOfRoom(scanner_motor, drop_motor, color_sensor, right_motor, left_motor)
    scanner.scan_room(0)
        
# test(2)
# print("line follower")
# lf.line_follower()
# print("smooth turn")
# lf.smooth_turn()
# print("line follower distance 10")
# lf.line_follower_distance(10)