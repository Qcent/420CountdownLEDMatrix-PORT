#import ntplib
import time
import pytz
from datetime import datetime, timezone, timedelta
#import win32api
import multiprocessing
from playsound import playsound

from ColorFXUtils import BGFX_GLOBALS

# Constants and initializations
messages = {
    "duringCountdownMsg": "When is the next 4:20?",
    "afterCountdownMsg": "! Toke Up !            ! More LIFE !         "
}
mem_sec = 0

time_msg_vars = {"pass": 0, "bounce": 0, "count": 0, "matrixPrintPos": 44, "previousMillis": 0, "TextOrTime": False,
                 "FINAL_COUNTDOWN": False, "UpdateMessage": False}
time_left_in_countdown = {
    "tm_yday": 0,
    "tm_hour": 0,
    "tm_min": 0,
    "tm_sec": 0,
    "tm_ff": 0  # Initialize with 0
}

time_msg_colors = [  # list of colors to cycle through (optionally editable)
    (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255)]


class PlaySound:
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=self._run)
        self.process.start()

    def _run(self):
        while True:
            file_path = self.queue.get()
            if file_path is None:
                break
            playsound(file_path)

    def play(self, file_path):
        self.queue.put(file_path)

    def stop(self):
        self.queue.put(None)
        self.process.join()


# Function to check if the countdown is over
def COUNTDOWN_OVER():
    global time_left_in_countdown
    return time_left_in_countdown["tm_ff"] == -1


# Function to check if it's the final moments
def FINAL_MOMENTS():
    global time_left_in_countdown
    return time_left_in_countdown["tm_ff"] == -2


# Function to check if it's the last 10 minutes
def LAST_10_MIN():
    global time_left_in_countdown
    return time_left_in_countdown["tm_ff"] == -3


# Function to get the next color
def NEXT_COLOR():
    global time_msg_vars, time_msg_colors
    time_msg_vars["pass"] += 1
    if time_msg_vars["pass"] >= len(time_msg_colors):
        time_msg_vars["pass"] = 0


def printMessage(msg, matrix):
    global time_msg_vars
    len_msg = len(msg) * 6  # 6 pixels per character

    matrix.write(time_msg_vars["matrixPrintPos"], 2, msg, 1, time_msg_colors[time_msg_vars["pass"]], 0)

    if FINAL_MOMENTS():  # center time, flash colors
        time_msg_vars["matrixPrintPos"] = (matrix.width // 2) - len_msg // 2
        if time_msg_vars["count"] > 8:
            time_msg_vars["count"] = 0
            NEXT_COLOR()
        else:
            time_msg_vars["count"] += 1

    elif LAST_10_MIN() and time_msg_vars["TextOrTime"]:  # Bounce the time-left 3 times across display
        if time_msg_vars["bounce"] % 2 == 1:
            time_msg_vars["count"] += 1
            if time_msg_vars["count"] > 2:  # move the text twice as slow
                time_msg_vars["count"] = 0
                time_msg_vars["matrixPrintPos"] -= 1
                if time_msg_vars["matrixPrintPos"] < 1:
                    time_msg_vars["bounce"] += 1
                    NEXT_COLOR()
                    if time_msg_vars["bounce"] % 3 == 0:
                        time_msg_vars["matrixPrintPos"] = matrix.width
                        return 1

        else:
            time_msg_vars["count"] += 1
            if time_msg_vars["count"] > 2:  # move the text twice as slow
                time_msg_vars["count"] = 0
                time_msg_vars["matrixPrintPos"] += 1
                if time_msg_vars["matrixPrintPos"] > (matrix.width - len_msg):
                    time_msg_vars["bounce"] += 1
                    NEXT_COLOR()
                    if time_msg_vars["bounce"] % 3 == 0:
                        time_msg_vars["matrixPrintPos"] = matrix.width
                        return 1  # bouncing has reached it max

    elif (time_msg_vars["matrixPrintPos"] - 1) < -len_msg:  # Default Scroll
        # the text message has scrolled through the display entirely
        if LAST_10_MIN():  # reset the position to continue bounce effect (4 characters (0:00) * 6 pixels)
            time_msg_vars["matrixPrintPos"] = matrix.width - (4 * 6) if time_msg_vars["bounce"] % 2 else 0
        else:
            time_msg_vars["matrixPrintPos"] = matrix.width  # reset the printout position
        NEXT_COLOR()  # loop through the colors for our text

        return 1  # message was displayed in its entirety

    else:
        time_msg_vars["matrixPrintPos"] -= 1

    return 0  # message is still scrolling through display

'''
def set_system_time(new_time):
    win32api.SetSystemTime(new_time.year, new_time.month, new_time.weekday(),
                           new_time.day, new_time.hour, new_time.minute,
                           new_time.second, int(new_time.microsecond / 1000))


def get_ntp_time(ntp_server='pool.ntp.org', target_timezone_str='US/Eastern'):
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request(ntp_server, version=3)

    # Convert the timestamp to a datetime object in UTC
    utc_time = datetime.fromtimestamp(response.tx_time, pytz.utc)

    # Define the target timezone
    target_timezone = pytz.timezone(target_timezone_str)

    # Convert the UTC time to the target timezone
    target_time = utc_time.astimezone(target_timezone)

    return target_time
'''

def millis():
    return int(time.time() * 1000)


def calc_time_difference(epoch_time1, epoch_time2):
    # Calculate difference in seconds
    time_difference = epoch_time2 - epoch_time1

    # Calculate days, hours, minutes, and seconds
    days = time_difference // (3600 * 24)
    hours = (time_difference % (3600 * 24)) // 3600
    minutes = (time_difference % 3600) // 60
    seconds = time_difference % 60

    global time_left_in_countdown
    time_left_in_countdown["tm_yday"] = int(days)
    time_left_in_countdown["tm_hour"] = int(hours)
    time_left_in_countdown["tm_min"] = int(minutes)
    time_left_in_countdown["tm_sec"] = int(seconds)

    # Update time_left_in_countdown dictionary
    if time_difference < 1:
        time_left_in_countdown["tm_ff"] = -1  # Signal the countdown is over
    elif time_difference < 120:
        time_left_in_countdown["tm_ff"] = -2  # In the last 2 minutes
    elif time_difference < 600:
        time_left_in_countdown["tm_ff"] = -3  # In the last 10 minutes

    return time_left_in_countdown


def get_formatted_time(matrix):
    global mem_sec
    global time_left_in_countdown

    # Create a buffer for the formatted time
    formatted_time = ""

    if time_left_in_countdown['tm_sec'] != mem_sec:  # clock has ticked at least one second
        mem_sec = time_left_in_countdown['tm_sec']
        if time_left_in_countdown['tm_yday'] < 1 and time_left_in_countdown['tm_hour'] < 1 and time_left_in_countdown[
            'tm_min'] < 1:
            formatted_time = f"{time_left_in_countdown['tm_sec']}"
            if mem_sec < 12:
                if 11 > mem_sec > 0:
                    matrix.output_target.sound_player.play("ding.mp3")
                time_msg_vars["FINAL_COUNTDOWN"] = True
                BGFX_GLOBALS["pulseIn_start"] = True
                BGFX_GLOBALS["bgEffects"] = 3  # BGFX_PULSE

        elif time_left_in_countdown['tm_yday'] < 1 and time_left_in_countdown['tm_hour'] < 1:
            formatted_time = f"{time_left_in_countdown['tm_min']}:{time_left_in_countdown['tm_sec']:02d}"
        elif time_left_in_countdown['tm_yday'] < 1:
            formatted_time = f"{time_left_in_countdown['tm_hour']:02d}:{time_left_in_countdown['tm_min']:02d}:{time_left_in_countdown['tm_sec']:02d}"
        else:
            formatted_time = f"{time_left_in_countdown['tm_yday']} days, {time_left_in_countdown['tm_hour']:02d}:{time_left_in_countdown['tm_min']:02d}:{time_left_in_countdown['tm_sec']:02d}"

    return formatted_time


'''def get_current_epoch_time():
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        return response.tx_time  # This returns the time in seconds since the epoch
    except Exception as e:
        print(f"Could not get NTP time: {e}")
        return None'''


def get_next_time_target(hour, minute, target_timezone_str='US/Eastern'):
    current_epoch_time = datetime.now().timestamp() # get_current_epoch_time()
    if current_epoch_time is None:
        print("Failed to get the current time")
        return False

        # Convert the current epoch time to a datetime object in UTC
    current_time_utc = datetime.fromtimestamp(current_epoch_time, timezone.utc)

    # Define the target timezone
    target_timezone = pytz.timezone(target_timezone_str)

    # Convert the current UTC time to the target timezone, which will account for DST
    current_time_target_tz = current_time_utc.astimezone(target_timezone)

    # Create a naive datetime object for the target time today (no timezone info)
    target_time_naive = datetime(current_time_target_tz.year, current_time_target_tz.month, current_time_target_tz.day,
                                 hour, minute)

    # Attach the target timezone to the naive datetime object (without adjusting for DST)
    target_time = target_timezone.localize(target_time_naive, is_dst=None)

    if current_time_target_tz > target_time:
        target_time += timedelta(days=1)  # advance a day

    # Return the target time as an epoch timestamp
    return int(target_time.timestamp())


"""
targetEpoch = get_next_time_target(16, 20)
print(targetEpoch)

print(calc_time_difference(get_current_epoch_time(), targetEpoch))

print(get_formatted_time())
"""
