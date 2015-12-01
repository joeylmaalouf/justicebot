from wrappers.constants import *
from wrappers.kinect_wrapper import Kinect
from wrappers.serial_wrapper import connect


def key_cb(kinect, key, serial, instructions):
  if key == K_w:
    kinect.device.camera.elevation_angle += 2
  elif key == K_x:
    kinect.device.camera.elevation_angle -= 2
  elif key == K_s:
    kinect.device.camera.elevation_angle = 2
  elif key in instructions.keys():
    serial.write(instructions[key])


def skel_cb(kinect, skeletons, serial):
  if skeletons is not None:
    for index, skeleton in enumerate(skeletons):
      skel_center = skeleton.SkeletonPositions[JointId.ShoulderCenter.value]
      if skel_center.x != 0.0 and skel_center.y != 0.0:
        if skel_center.x < -0.25:
          serial.write("r") # image is flipped, so send opposite instruction
          print("Target is: LEFT")
        elif skel_center.x > 0.25:
          serial.write("l") # maybe I should figure out how to flip the image before processing
          print("Target is: RIGHT")
        elif skel_center.z < 1.5:
          serial.write("d")
          print("Target is: CLOSE")
        elif skel_center.z > 2.0:
          serial.write("u")
          print("Target is: FAR")
        else:
          serial.write("h")
          print("Target is: CENTERED")


if __name__ == "__main__":
  serial = connect("COM7", 9600)
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
      "serial": serial
    }
  )
  kinect.start()
