from pygame.locals import *
from pygame.color import THECOLORS
from pykinect.nui import JointId


VIDEO_MODE_ARGS = ((640, 480), 0, 32)
DEPTH_MODE_ARGS = ((320, 240), 0, 16)

SKELETON_COLORS = [
  THECOLORS["red"],
  THECOLORS["orange"],
  THECOLORS["yellow"],
  THECOLORS["green"],
  THECOLORS["blue"],
  THECOLORS["purple"],
  THECOLORS["violet"]
]

LEFT_ARM = (
  JointId.ShoulderCenter,
  JointId.ShoulderLeft,
  JointId.ElbowLeft,
  JointId.WristLeft,
  JointId.HandLeft
)
RIGHT_ARM = (
  JointId.ShoulderCenter,
  JointId.ShoulderRight,
  JointId.ElbowRight,
  JointId.WristRight,
  JointId.HandRight
)
LEFT_LEG = (
  JointId.HipCenter,
  JointId.HipLeft,
  JointId.KneeLeft,
  JointId.AnkleLeft,
  JointId.FootLeft
)
RIGHT_LEG = (
  JointId.HipCenter,
  JointId.HipRight,
  JointId.KneeRight,
  JointId.AnkleRight,
  JointId.FootRight
)
SPINE = (
  JointId.HipCenter,
  JointId.Spine,
  JointId.ShoulderCenter,
  JointId.Head
)
