from utils.brick import wait_ready_sensors, EV3ColorSensor, busy_sleep

def get_redlight_value(color_sensor): 
  """
    Place robot in desired position and function will return amount of reflected light 
    value is between 0 (dark) to 100 (light)
    """
  sum = 0
  for i in range(5): 
    val = color_sensor.get_red()
    sum += val
    print(val)
    print(i)

  average = sum/5
  print(average)

if __name__ == "__main__":
  color_sensor = EV3ColorSensor(3)
  wait_ready_sensors(True)
  while True:
    get_redlight_value(color_sensor)
    busy_sleep(1)