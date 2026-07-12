import modi_plus
import time

bundle = modi_plus.MODIPlus()

time.sleep(2)

m1= bundle.motors[0]
m2 = bundle.motors[1]
m3 = bundle.motors[2]
m4 = bundle.motors[3]

def sleep(time1):
    time.sleep(time1)

def stop():
    m1.speed=0
    m2.speed=0
    m3.speed=0
    m4.speed=0

def s(speed):
    m1.speed=speed
    m2.speed=-speed
    m3.speed=-speed
    m4.speed= speed

def w(speed):
    m1.speed=-speed
    m2.speed=speed
    m3.speed=speed
    m4.speed=-speed

def a(speed):
    m1.speed=speed
    m2.speed=speed
    m3.speed=speed
    m4.speed=speed

def d(speed):
    m1.speed=-speed
    m2.speed=-speed
    m3.speed=-speed
    m4.speed=-speed

while True:
    a1=input()
    if a1 == "w":
        w(100)
        sleep(0.5)
        stop()
    if a1 == "s":
        s(100)
        sleep(0.5)
        stop()
    if a1 == "a":
        a(100)
        sleep(0.5)   
        stop()
    if a1 == "d":
        d(100)
        sleep(0.5)
        stop()


