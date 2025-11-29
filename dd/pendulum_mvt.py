from utils.brick import Motor, EV3ColorSensor, SensorError
from color_detection_algorithm import ColorDetectionAlgorithm
import time
import threading
import sounds_utils

class PendulumScanner:
    LEFT_POSITION = -45
    LEFT_POSITION_2 = -45
    RIGHT_POSITION = 45
    RIGHT_POSITION_2 = 45
    MOTOR_DPS = 150

    def __init__(self, motor_color_sensor, motor_block, color_sensor):
        self.motor_color_sensor = motor_color_sensor
        self.motor_block = motor_block
        self.COLOR_SENSOR = color_sensor
        self.color_detection_algorithm = ColorDetectionAlgorithm()

        self.initial_color = self.motor_color_sensor.get_position()
        self.initial_block = self.motor_block.get_position()

        # State
        self.detected_color = None
        self.stopped_color_detection = False
        self.stopped_motor_block = False
        self.stopped_motor_color_sensor = False
        self.emergency_stop = False

    # ----- CENTRAL EMERGENCY STOP -----
    def stop_the_arms_movement(self, color=None):
        """Stop both arms immediately"""
        self.detected_color = color
        self.stopped_color_detection = True
        self.motor_color_sensor.set_dps(0)
        self.motor_block.set_dps(0)

    # ----- COLOR SENSOR -----
    def color_sample(self):
        count_green = 0
        count_red = 0

        while not self.stopped_color_detection and not self.stopped_motor_block and not self.stopped_motor_color_sensor:
            if self.emergency_stop:
                self.stop_the_arms_movement("emergency")
                return "emergency"

            try:
                values = self.COLOR_SENSOR.get_value()
                if values:
                    R, G, B, L = values
                    color = self.color_detection_algorithm.classify_the_color(R, G, B)

                    # Count consecutive greens or reds
                    if color == "green":
                        count_green += 1
                        count_red = 0
                    elif color == "red":
                        count_red += 1
                        count_green = 0
                    else:
                        count_green = 0
                        count_red = 0

                    if count_green >= 5:
                        self.stop_the_arms_movement("green")
                        sounds_utils.play_wav("balalala.wav")
                        return "green"

                    if count_red >= 5:
                        self.stop_the_arms_movement("red")
                        return "red"

            except SensorError:
                print("Color sensor error")

            time.sleep(0.05)  # small sleep

        return None

    # ----- MOTOR MOVEMENT -----
    def move_motor(self, motor, left, right, position):
        """Simple pendulum move without repeated emergency checks"""
        motor.set_dps(self.MOTOR_DPS)
        base_pos = self.initial_color if motor == self.motor_color_sensor else self.initial_block

        if position == "right":
            motor.set_position(base_pos + left)
        else:
            motor.set_position(base_pos + right)

        time.sleep(1)  # allow motor to move
        motor.set_dps(0)

    def move_motor_pendulum(self, position):
        self.move_motor(self.motor_color_sensor, self.LEFT_POSITION, self.RIGHT_POSITION, position)
        self.stopped_motor_color_sensor = True

    def move_motor_block(self, position):
        self.move_motor(self.motor_block, self.LEFT_POSITION_2, self.RIGHT_POSITION_2, position)
        self.stopped_motor_block = True

    # ----- MAIN FUNCTION -----
    def main_pendulum(self, position="right"):
        self.detected_color = None
        self.stopped_color_detection = False
        self.stopped_motor_block = False
        self.stopped_motor_color_sensor = False

        # Threads for concurrent movement and color sensing
        color_thread = threading.Thread(target=self.color_sample)
        pendulum_thread = threading.Thread(target=self.move_motor_pendulum, args=(position,))
        block_thread = threading.Thread(target=self.move_motor_block, args=(position,))

        color_thread.start()
        pendulum_thread.start()
        block_thread.start()

        color_thread.join()
        pendulum_thread.join()
        block_thread.join()

        return self.detected_color
