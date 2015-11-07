# local imports
from wrappers.kinect_wrapper import Kinect
from wrappers.serial_wrapper import connect

# module imports
import cv2
import numpy as np


def rgb_cb(kinect, data, hog):
  """ display the rgb image with a box drawn around any detected people """
  data = np.array(data[:, :, ::-1]) # reverse color channels, RGB -> BGR for OpenCV
  found, _ = hog.detectMultiScale(data, winStride = (8, 8), padding = (32, 32), scale = 1.1) # detect humanoids
  for x, y, w, h in found:
    p1 = (max(x, 0), max(y, 0))
    p2 = (min(x + w, data.shape[1]), min(y + h, data.shape[0]))
    cv2.rectangle(data, p1, p2, (0, 255, 0), 1)
  cv2.imshow("RGB Image", data)


def depth_cb(kinect, data):
  """ display the depth image """
  data = data / float(np.amax(data)) # normalize the depth array for display
  cv2.imshow("Depth Image", data)


def body_cb(kinect, serial):
  """ quit or send a signal to the Arduino, depending on the keypress """
  instructions = {
    82: "u", # up = forwards
    84: "d", # down = backwards
    81: "l", # left = left
    83: "r", # right = right
    32: "h", # space = halt
    85: "f", # page up = faster
    86: "s"  # page down = slower
  }
  keypress = cv2.waitKey(10) % 256
  if keypress == 27: # escape key
    kinect.stop()
  elif keypress in instructions.keys():
    serial.write(instructions[keypress])


def exit_cb(kinect):
  """ close anything we have open so that the program can finish """
  print("ALERT: Kill switch flipped; terminating program execution.")
  cv2.destroyAllWindows()


if __name__ == "__main__":
  serial = connect("/dev/ttyACM*", 9600) # match any port that the Arduino connects to
  hog = cv2.HOGDescriptor()
  hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
  kinect = Kinect(
    image_callback = rgb_cb,   image_kwargs = { "hog": hog },
    depth_callback = depth_cb, depth_kwargs = {},
    body_callback  = body_cb,  body_kwargs  = { "serial": serial },
    exit_callback  = exit_cb,  exit_kwargs  = {}
  )
  kinect.run()
  # redo in C++ for Kinect skeleton-tracking?
