from gpiozero import LED
from time import sleep

# Set up the LEDs
green_led = LED(4)  # Green LED on GPIO pin 4
red_led = LED(17)   # Red LED on GPIO pin 17

# Ask the user for the number of times to blink
num_blinks = int(input("How many times should the LEDs blink? "))

# Blink the LEDs
for _ in range(num_blinks):
    green_led.on()  # Turn on the green LED
    red_led.off()   # Turn off the red LED
    sleep(0.5)      # Wait for 0.5 seconds
    green_led.off() # Turn off the green LED
    red_led.on()    # Turn on the red LED
    sleep(0.5)      # Wait for 0.5 seconds
