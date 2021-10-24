from utime import sleep

from hardware import hc4067

if __name__ == '__main__':
  mp = hc4067.Hc4067(pinSig=32, pinS0=12, pinS1=13, pinS2=14, pinS3=15)
  
  print(mp.value)
  while True:
    if mp.changed:
      print(mp.value)
    #sleep(0.55)
