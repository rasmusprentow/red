


import Adafruit_BBIO.GPIO as GPIO

cols = ["P8_11", "P8_15", "P8_17", "P8_26"]
rows = ["P8_12", "P8_14", "P8_18", "P8_16"]



keymap = (
        ("1", "2", "3", "r"),
        ("4", "5", "6", "y"),
        ("7", "8", "9", "b"),
        ("*", "0", "#", "g"),
)


def setup():
    for row in rows:
               
        for col in cols:
            GPIO.setup(col, GPIO.OUT,  pull_up_down=GPIO.PUD_OFF)
            GPIO.output(col, GPIO.HIGH)
    
        GPIO.setup(row, GPIO.OUT)
        GPIO.output(row, GPIO.HIGH)
        GPIO.setup(row, GPIO.IN,pull_up_down=GPIO.PUD_UP)



def getkey():
    for row in rows:
        GPIO.setup(row,GPIO.IN, pull_up_down=GPIO.PUD_UP)
           
    c = 0
    for col in cols:
        GPIO.output(col, GPIO.HIGH)

        r = 0
        for row in rows:
            if GPIO.input(row):
                return keymap[r][c]
                GPIO.output(col, GPIO.LOW)
            r += 1    

        GPIO.output(col, GPIO.LOW)
        c += 1


setup()



