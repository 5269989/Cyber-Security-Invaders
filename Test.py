import RPi.GPIO as GPIO
import time

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setwarnings(False)  # Disable warnings

green_led_pin = 18  # GPIO pin for the green LED
red_led_pin = 17    # GPIO pin for the red LED

GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(red_led_pin, GPIO.OUT)

# Ask the user how many times to blink
num_blinks = int(input("How many times should the LEDs blink? "))

# Blink the LEDs alternately
for _ in range(num_blinks):
    # Turn on green LED, off red LED
    GPIO.output(green_led_pin, GPIO.HIGH)
    GPIO.output(red_led_pin, GPIO.LOW)
    time.sleep(0.1)  # Blink fast
    
    # Turn on red LED, off green LED
    GPIO.output(green_led_pin, GPIO.LOW)
    GPIO.output(red_led_pin, GPIO.HIGH)
    time.sleep(0.1)  # Blink fast

# Clean up GPIO settings after the loop
GPIO.cleanup()
