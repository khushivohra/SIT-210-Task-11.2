6import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# MQTT broker details
broker_address = "broker.hivemq.com"
port = 1883
topic = "PhValuezzz"

#controls GPIO pin on R.Pi
import RPi.GPIO as GPIO 
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pins for the servo motors
servo_pin_1 = 17
servo_pin_2 = 18
feeder_pin = 22

# Set the PWM parameters
frequency = 50  # 50 Hz (typical for most servos)
duty_cycle_min = 2.5  # 0 degrees
duty_cycle_max = 12.5  # 180 degrees

# Initialize the servo motors
GPIO.setup(servo_pin_1, GPIO.OUT)
pwm_1 = GPIO.PWM(servo_pin_1, frequency)
GPIO.setup(servo_pin_2, GPIO.OUT)
pwm_2 = GPIO.PWM(servo_pin_2, frequency)
GPIO.setup(feeder_pin, GPIO.OUT)
pwm_feeder = GPIO.PWM(feeder_pin, frequency)

# Function to move a servo to a specific angle
def set_angle(servo, angle):
    duty_cycle = ((angle / 180.0) * (duty_cycle_max - duty_cycle_min)) + duty_cycle_min
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(1)

# Rotate servo 1 to 0 degrees (minimum)
set_angle(pwm_1, 0)

# Pause for a moment
time.sleep(1)

# Rotate servo 1 to 90 degrees
set_angle(pwm_1, 90)

# Pause for a moment
time.sleep(1)

# Rotate servo 1 to 180 degrees (maximum)
set_angle(pwm_1, 180)

# Clean up and exit
pwm_1.stop()
pwm_2.stop()
pwm_feeder.stop()
GPIO.cleanup()

# MQTT callback when a message is received
def on_message(client, userdata, message):
    ph_value = float(message.payload.decode("utf-8"))
    update_ph_label(ph_value)
    if ph_value < 7:
        control_servo_1()
    elif ph_value > 8:
        control_servo_2()

# Function to update the pH label in the GUI
def update_ph_label(value):
    ph_label.config(text="pH Value: {:.2f}".format(value))

# Create an MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(broker_address, port)
client.subscribe(topic)
client.loop_start()

# GUI setup
root = tk.Tk()
root.title("pH Value Display")

# Set the style
style = ttk.Style()
style.configure("TLabel", font=("Arial", 24), padding=10)
style.configure("TFrame", background="#F0F0F0")
style.configure("TButton", font=("Arial", 18), padding=10, width=20)

# pH label
ph_label = ttk.Label(root, text="pH Value: ")
ph_label.pack(pady=20)

# Action label
action_label = ttk.Label(root, text="")
action_label.pack(pady=10)

# Add a frame for better layout
frame = ttk.Frame(root, style="TFrame")
frame.pack(pady=20)

# Dispense button for feeder
feeder_button = ttk.Button(frame, text="Dispense Feeder", command=control_feeder, style="TButton")
feeder_button.grid(row=0, column=0, padx=10, pady=10)

# Start the GUI main loop
root.mainloop()
