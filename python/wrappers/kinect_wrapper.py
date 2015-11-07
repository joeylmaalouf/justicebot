import freenect
from time import sleep


class Kinect(object):
  """ the class representation of our Kinect interface """
  def __init__(self, delay = float(1) / 60,
               image_callback = None, image_kwargs = {},
               depth_callback = None, depth_kwargs = {},
               body_callback  = None, body_kwargs  = {},
               exit_callback  = None, exit_kwargs  = {}):
    super(Kinect, self).__init__()
    self.delay = delay
    self.image_callback, self.image_kwargs = image_callback, image_kwargs
    self.depth_callback, self.depth_kwargs = depth_callback, depth_kwargs
    self.body_callback , self.body_kwargs  = body_callback , body_kwargs
    self.exit_callback , self.exit_kwargs  = exit_callback , exit_kwargs

  def video(self, dev, data, timestamp):
    """ runs when we receive RGB camera data """
    if self.image_callback:
      self.image_callback(self, data, **self.image_kwargs)

  def depth(self, dev, data, timestamp):
    """ runs when we receive depth camera data """
    if self.depth_callback:
      self.depth_callback(self, data, **self.depth_kwargs)

  def body(self, *args):
    """ runs every loop """
    if self.body_callback:
      self.body_callback(self, **self.body_kwargs)
    sleep(self.delay)

  def run(self):
    """ runs main loop with given callbacks """
    freenect.runloop(video = self.video, depth = self.depth, body = self.body)

  def stop(self):
    """ terminate execution with an optional final callback """
    if self.exit_callback:
      self.exit_callback(self, **self.exit_kwargs)
    raise freenect.Kill
