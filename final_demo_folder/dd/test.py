from utils.brick import Motor, EV3ColorSensor
from robot_moving_in_the_room import RobotScannerOfRoom

top = Motor("A")
bottom = Motor("D")
COLOR_SENSOR = EV3ColorSencor(3)
RIGHT_WHEEL = Motor("C")
LEFT_WHEEL = Motor("B")

scanner = RobotScannerOfRoom(top, bottom, COLOR_SENSOR, RIGHT_WHEEL, LEFT_WHEEL)

scanner.scan_room(0)