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
      # keep tracked target centered
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

        # recognize gesture
        skel_lelbow = skeleton.SkeletonPositions[JointId.ElbowLeft.value]
        skel_relbow = skeleton.SkeletonPositions[JointId.ElbowRight.value]
        skel_lwrist = skeleton.SkeletonPositions[JointId.WristLeft.value]
        skel_rwrist = skeleton.SkeletonPositions[JointId.WristRight.value]
        skel_lshoulder = skeleton.SkeletonPositions[JointId.ShoulderLeft.value]
        skel_rshoulder = skeleton.SkeletonPositions[JointId.ShoulderRight.value]
        if (skel_lwrist.y > skel_lelbow.y) and (skel_rwrist.y > skel_relbow.y):#and (skel_lwrist.y > skel_center.y) and (skel_rwrist.y > skel_center.y):
          if (skel_lshoulder.x < (skel_lwrist.x + 0.1)) and ((skel_rwrist.x - 0.1) < skel_rshoulder.x):
            print("Subject compliant, arms on head. Advised action: apprehend peacefully.")
          else:
            print("Subject aggressive, arms raised. Advised action: apprehend with caution.")
        elif (skel_lwrist.z < (skel_center.z - 0.35)) or skel_rwrist.z < (skel_center.z - 0.35):
          print("Subject hostile, arm extended. Advised action: user discretion.")
        else:
          print("No special gesture recognized. Advised action: unavailable.")


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
