from constants import *
import ctypes
import itertools
import pygame
from pykinect import nui
import thread
import sys


class Kinect(object):
  def __init__(
      self,
      key_callback  = None, key_cb_kwargs  = {},
      skel_callback = None, skel_cb_kwargs = {}
    ):
    super(Kinect, self).__init__()
    pygame.init()
    self.key_callback,  self.key_cb_kwargs  = key_callback,  key_cb_kwargs
    self.skel_callback, self.skel_cb_kwargs = skel_callback, skel_cb_kwargs
    self.skeletons = None
    self.done = False
    self.screen_lock = thread.allocate()
    self.set_video_mode(True)
    pygame.display.set_caption("Python Kinect Skeleton Tracking")

    self._PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
    self._PyObject_AsWriteBuffer.restype = ctypes.c_int
    self._PyObject_AsWriteBuffer.argtypes = [ctypes.py_object, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int)]

    try:
      self.device = nui.Runtime()
    except WindowsError:
      print("Error: No Kinect device found.")
      sys.exit()
    self.device.skeleton_engine.enabled = True
    self.device.skeleton_frame_ready += self.post_frame
    self.device.depth_frame_ready += self.put_depth_frame
    self.device.video_frame_ready += self.put_video_frame
    self.device.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
    self.device.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)

  def set_video_mode(self, mode = True):
    with self.screen_lock:
      self.screen = pygame.display.set_mode(*(VIDEO_MODE_ARGS if mode else DEPTH_MODE_ARGS))
      self.video_mode = mode
      self.cur_w = pygame.display.Info().current_w
      self.cur_h = pygame.display.Info().current_h


  def surface_to_array(self, surface):
    buffer_interface = surface.get_buffer()
    address = ctypes.c_void_p()
    size = ctypes.c_int()
    self._PyObject_AsWriteBuffer(buffer_interface, ctypes.byref(address), ctypes.byref(size))
    bytedata = (ctypes.c_byte * size.value).from_address(address.value)
    bytedata.object = buffer_interface
    return bytedata

  def post_frame(self, frame):
    try:
      pygame.event.post(pygame.event.Event(pygame.USEREVENT, skeletons = frame.SkeletonData))
    except RuntimeError:
      pass

  def put_depth_frame(self, frame):
    if self.video_mode:
      return
    with self.screen_lock:
      if self.skel_callback:
        self.skel_callback(self, self.skeletons, **self.skel_cb_kwargs)
      address = self.surface_to_array(self.screen)
      frame.image.copy_bits(address)
      del address
      self.draw_skeletons()
      pygame.display.update()

  def put_video_frame(self, frame):
    if not self.video_mode:
      return
    with self.screen_lock:
      if self.skel_callback:
        self.skel_callback(self, self.skeletons, **self.skel_cb_kwargs)
      address = self.surface_to_array(self.screen)
      frame.image.copy_bits(address)
      del address
      self.draw_skeletons()
      pygame.display.update()

  def draw_bones(self, skeleton, index, positions, width = 5):
    start = skeleton.SkeletonPositions[positions[0]]
    for position in itertools.islice(positions, 1, None):
      end = skeleton.SkeletonPositions[position.value]
      curstart = nui.SkeletonEngine.skeleton_to_depth_image(start, self.cur_w, self.cur_h)
      curend = nui.SkeletonEngine.skeleton_to_depth_image(end, self.cur_w, self.cur_h)
      pygame.draw.line(self.screen, SKELETON_COLORS[index], curstart, curend, width)
      start = end

  def draw_skeletons(self):
    if self.skeletons is not None:
      for index, data in enumerate(self.skeletons):
        HeadPos = nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[nui.JointId.Head], self.cur_w, self.cur_h)
        self.draw_bones(data, index, SPINE, 10)
        pygame.draw.circle(self.screen, SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)
        self.draw_bones(data, index, LEFT_ARM)
        self.draw_bones(data, index, RIGHT_ARM)
        self.draw_bones(data, index, LEFT_LEG)
        self.draw_bones(data, index, RIGHT_LEG)

  def start(self):
    while not self.done:
      e = pygame.event.wait()
      if e.type == pygame.QUIT:
        self.stop()
      elif e.type == pygame.USEREVENT:
        self.skeletons = e.skeletons
        self.draw_skeletons()
        pygame.display.update()
      elif e.type == KEYDOWN:
        if e.key == K_ESCAPE:
          self.stop()
        elif e.key == K_v:
          self.set_video_mode(True)
        elif e.key == K_d:
          self.set_video_mode(False)
        elif self.key_callback:
          self.key_callback(self, e.key, **self.key_cb_kwargs)

  def stop(self):
    self.done = True


if __name__ == "__main__":
  k = Kinect()
  k.start()
