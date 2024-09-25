# main.py
import time
from led import LED

# Set up LEDs
green_led = LED(18)  # GPIO pin for green LED
red_led = LED(17)    # GPIO pin for red LED

# Ask the user how many times to blink
num_blinks = int(input("How many times should the LEDs blink? "))

# Blink the LEDs alternately
for _ in range(num_blinks):
    green_led.on()
    red_led.off()
    time.sleep(0.1)  # Fast blink
    green_led.off()
    red_led.on()
    time.sleep(0.1)  # Fast blink

# Clean up GPIO
LED.cleanup()
