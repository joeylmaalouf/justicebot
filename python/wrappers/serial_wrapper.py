from glob import glob
from serial import Serial
from serial.serialutil import SerialException


def connect(port, baud, verbose = True):
  try:
    port = glob(port)[0]
  except IndexError:
    if verbose:
      print("Error: No device found on given serial port.")
    return None
  while True:
    try:
      serial = Serial(port, baud)
      if verbose:
        print("Connected to serial on port: {}".format(port))
      return serial
    except SerialException:
      continue
