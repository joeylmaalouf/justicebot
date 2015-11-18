from wrappers.constants import *
from wrappers.kinect_wrapper import Kinect
from wrappers.serial_wrapper import connect


def key_cb(kinect, key, serial, instructions):
  print dir(kinect.device.camera)
  if key == K_w:
    kinect.device.camera.elevation_angle += 2
  elif key == K_x:
    kinect.device.camera.elevation_angle -= 2
  elif key == K_s:
    kinect.device.camera.elevation_angle = 2
  elif key in instructions.keys():
    serial.write(instructions[key])


def skel_cb(kinect):
  if kinect.skeletons is not None:
    for index, skeleton in enumerate(kinect.skeletons):
      skel_center = skeleton.SkeletonPositions[JointId.ShoulderCenter.value]
      if skel_center.x != 0.0 and skel_center.y != 0.0:
        print index, skel_center


if __name__ == "__main__":
  serial = connect("/dev/ttyACM*", 9600) # match any port that the Arduino connects to
  instructions = {
    K_UP:       "u", # forwards
    K_DOWN:     "d", # backwards
    K_LEFT:     "l", # left
    K_RIGHT:    "r", # right
    K_SPACE:    "h", # halt
    K_PAGEUP:   "f", # faster
    K_PAGEDOWN: "s"  # slower
  }
  kinect = Kinect(
    key_callback  = key_cb,
    key_cb_kwargs = {
      "serial": serial,
      "instructions": instructions
    },
    skel_callback = skel_cb,
    skel_cb_kwargs = {
    }
  )
  kinect.start()
