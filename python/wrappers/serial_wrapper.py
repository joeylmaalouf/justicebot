from serial import Serial
from serial.serialutil import SerialException


def connect(port, baud, verbose = True):
  while True:
    try:
      serial = Serial(port, baud)
      if verbose:
        print("Connected to serial on port: {}.".format(port))
      return serial
    except SerialException, e:
      if "WindowsError(5" in e.message:
        continue
      elif "WindowsError(2" in e.message:
        if verbose:
          print("Error: No device found on given serial port.")
        return None
      else:
        raise SerialException("")
