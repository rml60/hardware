""" hc4067.py

    Simple drivers for external hardware to use with esp32.
     - 74HC4067 16-channel analog/digital Multiplexer 
     
    gnd: 4067-pin12, vcc: 4067-pin24
    sig: 4067-pin1,  en:  4067-pin15
    s0:  4067-pin10, s1:  4067-pin11, s2:  4067-pin14, s3:  4067-pin13
    y0:  4067-pin9,  y1:  4067-pin8,  y2:  4067-pin7,  y3:  4067-pin6
    y4:  4067-pin5,  y5:  4067-pin4,  y6:  4067-pin3,  y7:  4067-pin2
    y8:  4067-pin23, y9:  4067-pin22, y10: 4067-pin21, y11: 4067-pin20
    y12: 4067-pin19, y13: 4067-pin18, y14: 4067-pin17, y15: 4067-pin16

    Author:   Rainer Maier-Lohmann
    ---------------------------------------------------------------------------
    "THE BEER-WARE LICENSE" (Revision 42):
    <r.m-l@gmx.de> wrote this file.  As long as you retain this notice you
    can do whatever you want with this stuff. If we meet some day, and you 
    think this stuff is worth it, you can buy me a beer in return.
    ---------------------------------------------------------------------------    
    Copyright (c) 2021 
"""
from machine import Pin
from machine import Timer
from utime import sleep_us, sleep_ms

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
PORTS_DEFAULT = 16
TIMER_ID = 3 # 0 bis 3
PERIOD = 250 # in ms
SETADDR_DELAY_US = 25 # in us - min. 16 x 25 = 400 us for one read
CHECK_MAX = 100
CHECK_MIN_ZEROS = 25

#-------------------------------------------------------------------------------
# classes
#-------------------------------------------------------------------------------
class Hc4067():
  def __init__(self
              , pinSig
              , pinS0, pinS1, pinS2, pinS3
              , pinEn = None # via hardware set to 0 - no need to configure
              , ports=PORTS_DEFAULT
              , timerId=TIMER_ID
              , period=PERIOD # in ms
              ):
    """
    """
    self.__numberOfPorts = ports
    self.__enable = Pin(pinEn, Pin.OUT) if pinEn else None
    self.__signal = Pin(pinSig, Pin.IN, Pin.PULL_UP)
    self.__value = 0
    self.__changed = False
    self.__addrPins = [pinS0, pinS1, pinS2, pinS3]
    self.__pins = []
    for pin in self.__addrPins:
      self.__pins.append(Pin(pin, Pin.OUT))
    self.__addrBitValues = []
    self.__addr = 0
    self.__setAddrBits()

    # init timer
    self.__timerId = timerId
    self.__period = period
    self.__timer = Timer(timerId)
    self.__timer.init(period=period, mode=Timer.PERIODIC, callback=self.__getValue)

  def __getValue(self, timer):
    """ value is a integer with the sum of all inport values according to the
        bitposition. bitposition = address
        ( 1 = 1 (value=2^0, ..., 16 = 16 (value=2^15) )
    """
    value = 0
    for addr in range(0, self.__numberOfPorts, 1):
      self.__setAddr(addr)
      bitValue = self.__getRepeatedValue()
      if bitValue != 0:
        value |= 2**addr
      else:
        value &= 0xFFFF - 2**addr
    if self.__value != value:
      self.__changed = True
    self.__value = value
    #del addr
    #del bitValue
    #del value  

  @property
  def timerId(self):
    """ returns the ID of the used Timer (0 .. 3)
    """
    return self.__timerId

  @property
  def period(self):
    """ returns the periodlength in ms
    """
    return self.__period

  @property
  def changed(self):
    """ returns True, if min. one portvalue is toggeled else False
    """ 
    changed = self.__changed
    self.__changed = False
    return changed

  @property
  def value(self):
    """ returns the actual sum of portvalues
        (port1 = 1, port2 = 2, port3 = 4, port4 = 8,...).
    """
    return self.__value

  @property
  def addrBitValues(self):
    """ returns a list with all single addressbitvalues
        f.e. addr = 0 => [0,0,0,0] or addr = 5 => [0,1,0,1]
    """
    return self.__addrBitValues

  @property
  def portValues(self):
    """ returns a list with all single portvalues (0/1).
    """
    # TODO: to be implemented
    portValues = []
    value = 0
    portValues.append(value)
    return portValues

  def readPortValue(self, addr):
    """ returns the portvalue (0/1) of address.
    """
    # TODO: to be implemented
    portValue = 0
    return portValue

  def __isAddrBitSet(self, value, bitNo):
    """ True, if the given bit number in value is set.
    """
    return ((value & 2**bitNo) >> bitNo)

  def __setAddr(self, addr):
    """ sets the address for selecting the inport.
    """
    self.__addr = addr
    self.__setAddrBits()

  def __setAddrBitValues(self):
    """ sets the address bits according to the address
    """
    self.__addrBitValues = [] # reset the list just here
    for index, pin in enumerate(self.__addrPins):
      self.__addrBitValues.append(self.__isAddrBitSet(self.__addr, index))

  def __setAddrBits(self):
    """ sets the address out pins according to the address bits
    """
    self.__setAddrBitValues()
    for pinValue, pin in zip(self.__addrBitValues, self.__pins):
      pin.value(pinValue)
    sleep_us(SETADDR_DELAY_US)
    #del pinValue
    #del pin

  def __getRepeatedValue(self):
    """ returns the interpreted value of the selected inport.
        Value is 1, if a minimal count of zeros were readed in a loop for
        specified times.       
        values: 1 - set, 0 - open 
    """
    numberOfZeros = 0
    bitVal = 0
    for i in range(0, CHECK_MAX):
      val = self.__signal.value()
      if val == 0:
        numberOfZeros += 1
      if numberOfZeros >= CHECK_MIN_ZEROS:
        bitVal = 1
        break
    return bitVal
