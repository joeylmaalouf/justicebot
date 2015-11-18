import thread
import itertools
import ctypes
from pykinect import nui
import pygame
from pygame.locals import *
from constants import *


class Kinect(object):
  """ the class representation of our Kinect interface """
  def __init__(self):
    super(Kinect, self).__init__()
    pygame.init()
    self.skeletons = None
    self.video_mode = True # depth mode if False
    self.screen_lock = thread.allocate()
    self.screen = pygame.display.set_mode(*VIDEO_MODE_ARGS)
    pygame.display.set_caption("Python Kinect Skeleton Tracking")

  def print_help(self):
    print("Controls: ")
    print("  Esc: Quit")
    print("  V:   Switch to video view")
    print("  D:   Switch to depth view")
    print("  U:   Increase elevation angle")
    print("  J:   Decrease elevation angle")
    print("  K:   Reset elevation angle")


pygame.init()


def draw_bones(skeleton, index, positions, width = 5):
  start = skeleton.SkeletonPositions[positions[0]]
  for position in itertools.islice(positions, 1, None):
    end = skeleton.SkeletonPositions[position.value]
    curstart = nui.SkeletonEngine.skeleton_to_depth_image(start, cur_w, cur_h)
    curend = nui.SkeletonEngine.skeleton_to_depth_image(end, cur_w, cur_h)
    pygame.draw.line(screen, SKELETON_COLORS[index], curstart, curend, width)
    start = end


_PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
_PyObject_AsWriteBuffer.restype = ctypes.c_int
_PyObject_AsWriteBuffer.argtypes = [ctypes.py_object, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int)]


def surface_to_array(surface):
  buffer_interface = surface.get_buffer()
  address = ctypes.c_void_p()
  size = ctypes.c_int()
  _PyObject_AsWriteBuffer(buffer_interface, ctypes.byref(address), ctypes.byref(size))
  bytedata = (ctypes.c_byte * size.value).from_address(address.value)
  bytedata.object = buffer_interface
  return bytedata


def draw_skeletons(skeletons):
  for index, data in enumerate(skeletons):
    # draw the head
    HeadPos = nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[nui.JointId.Head], cur_w, cur_h)
    draw_bones(data, index, SPINE, 10)
    pygame.draw.circle(screen, SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)
    # draw the limbs
    draw_bones(data, index, LEFT_ARM)
    draw_bones(data, index, RIGHT_ARM)
    draw_bones(data, index, LEFT_LEG)
    draw_bones(data, index, RIGHT_LEG)


def post_frame(frame):
  try:
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, skeletons = frame.SkeletonData))
  except RuntimeError:
    pass # event queue full


def put_depth_frame(frame):
  if video_display:
    return
  with screen_lock:
    address = surface_to_array(screen)
    frame.image.copy_bits(address)
    del address
    if skeletons is not None:
      draw_skeletons(skeletons)
    pygame.display.update()


def put_video_frame(frame):
  if not video_display:
    return
  with screen_lock:
    address = surface_to_array(screen)
    frame.image.copy_bits(address)
    del address
    if skeletons is not None:
      draw_skeletons(skeletons)
    pygame.display.update()


if __name__ == "__main__":
  video_display = True

  screen_lock = thread.allocate()

  screen = pygame.display.set_mode(*VIDEO_MODE_ARGS)
  pygame.display.set_caption("Python Kinect Skeleton Tracking")
  skeletons = None

  kinect = nui.Runtime()
  kinect.skeleton_engine.enabled = True
  kinect.skeleton_frame_ready += post_frame
  kinect.depth_frame_ready += put_depth_frame
  kinect.video_frame_ready += put_video_frame

  kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
  kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)

  print("Controls: ")
  print("  Esc: Quit")
  print("  V:   Switch to video view")
  print("  D:   Switch to depth view")
  print("  U:   Increase elevation angle")
  print("  J:   Decrease elevation angle")
  print("  K:   Reset elevation angle")

  # main game loop
  done = False
  while not done:
    e = pygame.event.wait()
    cur_w = pygame.display.Info().current_w
    cur_h = pygame.display.Info().current_h
    if e.type == pygame.QUIT:
      done = True
      break
    elif e.type == pygame.USEREVENT:
      skeletons = e.skeletons
      draw_skeletons(skeletons)
      pygame.display.update()
    elif e.type == KEYDOWN:
      if e.key == K_ESCAPE:
        done = True
        break
      elif e.key == K_v:
        with screen_lock:
          screen = pygame.display.set_mode(*VIDEO_MODE_ARGS)
          video_display = True
      elif e.key == K_d:
        with screen_lock:
          screen = pygame.display.set_mode(*DEPTH_MODE_ARGS)
          video_display = False
      elif e.key == K_u:
        kinect.camera.elevation_angle = kinect.camera.elevation_angle + 2
      elif e.key == K_j:
        kinect.camera.elevation_angle = kinect.camera.elevation_angle - 2
      elif e.key == K_k:
        kinect.camera.elevation_angle = 2
