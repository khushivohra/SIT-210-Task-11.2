import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# MQTT broker details
broker_address = "broker.hivemq.com"
port = 1883
topic = "PhValuezzz"

import RPi.GPIO as GPIO
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pins for the servo motors
servo_pin_1 = 18
servo_pin_2 = 23
feeder_pin = 24

# Set the PWM parameters
GPIO.setup(servo_pin_1, GPIO.OUT)
GPIO.setup(servo_pin_2, GPIO.OUT)
GPIO.setup(feeder_pin, GPIO.OUT)

pwm_1 = GPIO.PWM(servo_pin_1, 50)  # (typical for most servos) (controls voltage at 50Hz)
pwm_2 = GPIO.PWM(servo_pin_2, 50)
pwm_3 = GPIO.PWM(feeder_pin, 50)

# Function to set the servo angle
def set_servo_angle(pwm, angle):
    duty_cycle = (angle / 18.0) + 2.5
    pwm.ChangeDutyCycle(duty_cycle)

try:
    pwm_1.start(0) #Starts each servo with an initial duty cycle of 0
    pwm_2.start(0)
    pwm_3.start(0)
    
    while True:
        set_servo_angle(pwm_1, 180)  # Rotate servo 1 to 180 degrees
        set_servo_angle(pwm_2, 180)  # Rotate servo 2 to 180 degrees
        set_servo_angle(pwm_3, 180)  # Rotate servo 3 to 180 degrees
        time.sleep(2)

except KeyboardInterrupt:
    pwm_1.stop()
    pwm_2.stop()
    pwm_3.stop()
    GPIO.cleanup()

# MQTT callback when a message is received
def on_message(client, userdata, message):
    ph_value = float(message.payload.decode("utf-8"))
    update_ph_label(ph_value)
    if ph_value < 6:
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
