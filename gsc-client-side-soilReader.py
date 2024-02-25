import tkinter as tk
from tkinter import messagebox
import RPi.GPIO as GPIO
import board
import adafruit_dht
import os
import psycopg2
import time
from dotenv import load_dotenv

# Sensor setup
GPIO.setmode(GPIO.BCM)
S0, S1, S2, S3, OUT= 20, 21, 22, 23, 24
GPIO.setup([S0, S1, S2, S3], GPIO.OUT)
GPIO.setup(OUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(S0, GPIO.HIGH)
GPIO.output(S1, GPIO.LOW)

# Load .env file
load_dotenv()

# Get the connection string from the environment variable
connection_string = os.getenv('DATABASE_URL') 

# Connect to the Postgres database
conn = psycopg2.connect(connection_string)

# Create a cursor object
cur = conn.cursor()

def ratio(rgb):
  sum = rgb[0]+rgb[1]+rgb[2]
  r = (rgb[0] / sum) * 6
  g = (rgb[1] / sum) * 6
  b = (rgb[2] / sum) * 6
  return r, g, b

def pulseIn(pin, value=GPIO.HIGH, timeout=1.0):
    """
    Measures the pulse width on the specified pin.
    """
    start_time = time.time()
    while GPIO.input(pin) != value:
        if time.time() - start_time > timeout:
            return 0  # Timeout
    start = time.time()
    while GPIO.input(pin) == value:
        if time.time() - start > timeout:
            return 0  # Timeout
    return time.time() - start

def read_frequency(pin, num_pulses=10):
    """
    Reads the frequency from the specified pin by measuring the duration of a given number of pulses.
    """
    total_time = 0
    for i in range(num_pulses):
        pulse_duration = pulseIn(pin)
        if pulse_duration == 0:
            return 0  # Timeout or error
        total_time += pulse_duration
    return num_pulses / total_time

def frequency_to_color_value(frequency, max_frequency):
    """
    Converts a frequency value to a 0-255 scale based on a maximum frequency.
    Clamps the value between 0 and 255.
    """
    value = int((frequency / max_frequency) * 255)
    return max(0, min(255, value))  # Clamps the value between 0 and 255

def read_color(max_frequency, num_pulses=10):
    """
    Reads the color values (R, G, B) from the sensor and converts them to a 0-255 scale.
    """
    # Read red
    GPIO.output(S2, GPIO.LOW)
    GPIO.output(S3, GPIO.LOW)
    red_frequency = read_frequency(OUT, num_pulses)
    red = frequency_to_color_value(red_frequency, max_frequency)

    # Read green
    GPIO.output(S2, GPIO.HIGH)
    GPIO.output(S3, GPIO.HIGH)
    green_frequency = read_frequency(OUT, num_pulses)
    green = frequency_to_color_value(green_frequency, max_frequency)

    # Read blue
    GPIO.output(S2, GPIO.LOW)
    GPIO.output(S3, GPIO.HIGH)
    blue_frequency = read_frequency(OUT, num_pulses)
    blue = frequency_to_color_value(blue_frequency, max_frequency)

    return red, green, blue


# User management functions
def check_user_credentials(username, password):
    try:
        cur.execute('SELECT EXISTS (SELECT 1 FROM auth WHERE usern = %s AND passw = %s)', (username, password))
        exists = cur.fetchone()[0]
        return exists == 1
    except psycopg2.Error as e:
        messagebox.showwarning("Error", "Failed to authenticate user: " + str(e))
        return False

# Tkinter GUI classes
class PlantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plant Monitoring App")
        self.geometry("300x200")
        self.current_user = None

        self.frame_sign_in = SignInFrame(self)
        self.frame_record_send = RecordSendFrame(self)

        self.show_sign_in_frame()

    def show_sign_in_frame(self):
        self.frame_sign_in.pack(fill=tk.BOTH, expand=True)
        self.frame_record_send.pack_forget()

    def show_record_send_frame(self):
        self.frame_record_send.pack(fill=tk.BOTH, expand=True)
        self.frame_sign_in.pack_forget()

class SignInFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        label = tk.Label(self, text="Sign In")
        label.pack(pady=10)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        username_label = tk.Label(self, text="Username")
        username_label.pack()
        self.username_entry = tk.Entry(self, textvariable=self.username)
        self.username_entry.pack()

        password_label = tk.Label(self, text="Password")
        password_label.pack()
        self.password_entry = tk.Entry(self, textvariable=self.password, show="*")
        self.password_entry.pack()

        sign_in_button = tk.Button(self, text="Sign In", command=self.sign_in)
        sign_in_button.pack(pady=5)

    def sign_in(self):
        username = self.username.get()
        password = self.password.get()

        if check_user_credentials(username, password):
            self.master.current_user = username
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.master.show_record_send_frame()
        else:
            messagebox.showwarning("Error", "Invalid username or password")

class RecordSendFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        label = tk.Label(self, text="Record and Send Data")
        label.pack(pady=10)

        record_button = tk.Button(self, text="Record and Send", command=self.record_and_send)
        record_button.pack(pady=5)

    def record_and_send(self):
        MAX_FREQUENCY = 5000
        NUM_PULSES = 10
        colors=read_color(MAX_FREQUENCY,NUM_PULSES)
        print("RGB (0-255): ",colors)
        rgb=list(colors)
        krat,prat,nrat=ratio(rgb)
        print("NPK (Ratio): ",krat,nrat,prat)
        dht_pin=board.D4
        dht_sensor=adafruit_dht.DHT11(dht_pin)
        try:
	        # Read data from the sensor
          temperature_c = dht_sensor.temperature
          humidity = dht_sensor.humidity
          print(f"Temperature: {temperature_c}°C, Humidity: {humidity}%")
          insert_query = '''
            INSERT INTO npk (usern, nrat, prat, krat, tem, mois, timel)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            '''
          cur.execute(insert_query, (self.master.current_user, nrat, prat, krat, temperature_c, humidity))
          conn.commit()

          messagebox.showinfo("Success", f"Data recorded and sent.")
        except RuntimeError as error:
          messagebox.showwarning("Error", f"Error Capturing Soil Data: {error}")
        except psycopg2.Error as e:
          messagebox.showwarning("Error", f"Database Error: {e}")
          conn.rollback()

if __name__ == "__main__":
    app = PlantApp()
    app.mainloop()

GPIO.cleanup()
