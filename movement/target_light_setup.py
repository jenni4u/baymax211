from utils.brick import wait_ready_sensors, EV3ColorSensor

color_sensor = EV3ColorSensor(3)

wait_ready_sensors(True)

def get_redlight_value(): 
  """
    Place robot in desired position and function will return amount of reflected light 
    value is between 0 (dark) to 100 (light)
    """
  sum = 0
  for i in range(10): 
    val = color_sensor.get_red()
    sum += val
    print(val)
    print(i)

  average = sum/10
  print(average)


get_redlight_value()