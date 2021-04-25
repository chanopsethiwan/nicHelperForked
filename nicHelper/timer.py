# AUTOGENERATED! DO NOT EDIT! File to edit: timer.ipynb (unless otherwise specified).

__all__ = ['Timer', 'start_timer', 'reset_timer', 'print_time', 'print_reset']

# Cell
from .wrappers import add_class_method,add_method,add_static_method
from datetime import datetime, timedelta

# Cell
class Timer:
  '''
  This is the class that will be used for the timer
  '''
  def __init__(self):
    self.start_timer()
  pass


# Cell
@add_method(Timer)
def start_timer(self):
  '''
  this method sets the starting time t0 to the current time
  '''
  self.t0 = datetime.now()
@add_method(Timer)
def reset_timer(self):
  '''
  this method resets t0 to the current time
  '''
  self.t0 = datetime.now()

# Cell
@add_method(Timer)
def print_time(self, description = 'function took'):
  '''
  this method subtracts the current time by t0 and prints the value in seconds to find out time between start timer and this method \n
  description: str: this is the string to be added before the value of time taken, default = 'function took'
  '''
  t1:timedelta = datetime.now() - self.t0
  print(f'{description} :{t1.total_seconds()} s')
  return t1.total_seconds()

# Cell
@add_method(Timer)
def print_reset(self, description = 'function took'):
  '''
  print and reset timer \n
  description: str: description of the item to print
  '''

  r = self.print_time(description = description)
  self.reset_timer()
  return r