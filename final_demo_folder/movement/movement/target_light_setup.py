from ..utils.brick import wait_ready_sensors, EV3ColorSensor, busy_sleep

def get_redlight_value(color_sensor): 
  """
    Place robot in desired position and function will return amount of reflected light 
    value is between 0 (dark) to 100 (light)
    """

  for i in range(5):
    sum = 0
    print(f"Set up for {i+1}th reading")
    for i in range(3): 
      val = color_sensor.get_red()
      sum += val
      print(f"\t{i+1}th reading: {val}")
    average = sum/3
    print(f"\tAverage for {i+1}th reading: {average}")
    print("-------------------------")

if __name__ == "__main__":
  color_sensor = EV3ColorSensor(3)
  wait_ready_sensors(True)
  while True:
    get_redlight_value(color_sensor)
    busy_sleep(1)