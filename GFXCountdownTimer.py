import re
import sys
import multiprocessing
from datetime import datetime

from PyQt5.QtGui import QColor, QIcon, QKeySequence, QPalette, QPainter, QPen, QCursor, QPixmap, QBrush
from PyQt5.QtWidgets import QAction, QApplication, QShortcut, QWidget, QVBoxLayout, QSystemTrayIcon, QMenu, \
    QWidgetAction, QGraphicsView, QGridLayout, QLabel, QHBoxLayout, QDialog, QLineEdit, QPushButton
from PyQt5.QtCore import QTimer, Qt, QEvent, QSize, QPoint, QThread, QObject, pyqtSignal, pyqtSlot

from fontLetters import *
from ColorFXUtils import *
from CountDownTimer import calc_time_difference, get_formatted_time, get_next_time_target, \
    time_msg_vars, time_left_in_countdown, printMessage, messages, PlaySound

APP_KILLED = False  # global flag signals loops/threads to exit when app needs to quit

############################################
# CountDownTimer Globals
targetEpoch = 0
interval = 1000
tokingTime = 60000 * 10  # 10 minutes
runGFXloop = False
ALARM_LEVEL = 0


############################################
# Helper Functions
def text_width(txt, scale):
    char_width = 6  # Width of each character in pixels
    return len(txt) * (char_width * scale)


def rotate_matrix(matrix, angle):
    """
    Rotate a matrix by the given angle.

    :param matrix: The matrix to rotate, represented as a list of lists.
    :param angle: The angle to rotate (in degrees). Should be one of 90, 180, 270.
    :return: The rotated matrix.
    """
    if angle not in [90, 180, 270]:
        raise ValueError("Angle must be one of 90, 180, 270 degrees.")

    def rotate_90(matrix):
        """Rotate the matrix 90 degrees clockwise."""
        return [list(reversed(col)) for col in zip(*matrix)]

    def rotate_180(matrix):
        """Rotate the matrix 180 degrees."""
        return [row[::-1] for row in matrix[::-1]]

    def rotate_270(matrix):
        """Rotate the matrix 270 degrees clockwise (or 90 degrees counterclockwise)."""
        return list(reversed(list(zip(*matrix))))

    if angle == 90:
        return rotate_90(matrix)
    elif angle == 180:
        return rotate_180(matrix)
    elif angle == 270:
        return rotate_270(matrix)


def rgb565_to_qcolor(color):
    r = ((color >> 11) & 0x1F) * 255 // 31
    g = ((color >> 5) & 0x3F) * 255 // 63
    b = (color & 0x1F) * 255 // 31
    return QColor(r, g, b)


def scale_8bit_to_nbit(value, num_bits):
    if not (0 <= value <= 255):
        raise ValueError("Input value must be an 8-bit integer (0-255)")
    if not (1 <= num_bits <= 32):
        raise ValueError("numBits must be between 1 and 32")

    max_8bit = 255  # Maximum value for 8-bit
    max_nbit = (1 << num_bits) - 1  # Maximum value for numBits

    # Scale the value
    scaled_value = round((value / max_8bit) * max_nbit)

    return scaled_value


def rgb_to_rgb565(r, g, b):
    r_5bit = scale_8bit_to_nbit(r, 5)
    g_6bit = scale_8bit_to_nbit(g, 6)
    b_5bit = scale_8bit_to_nbit(b, 5)
    rgb565 = (r_5bit << 11) | (g_6bit << 5) | b_5bit
    return rgb565


def qcolor_to_rgb565(color):
    r = color.red()
    g = color.green()
    b = color.blue()
    return rgb_to_rgb565(r, g, b)


def constrain(val, min_val, max_val):
    return max(min_val, min(val, max_val))


# Loads PROGMEM array from a file representing an image into memory
def parse_progmem_data(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"{e}")

    # Extract the PROGMEM array
    pattern = re.compile(r'const unsigned short.*?\{(.*?)\};', re.DOTALL)
    match = pattern.search(content)

    if not match:
        raise ValueError("PROGMEM array not found in file")

    data_str = match.group(1)

    # Extract width and height from the first line
    size_pattern = re.compile(r'\((\d+) << 8\) \| (\d+)')
    size_match = size_pattern.search(data_str)

    if not size_match:
        raise ValueError("Width and height information not found")

    width = int(size_match.group(1))
    height = int(size_match.group(2))

    # Extract numbers from the PROGMEM array, ignoring comments
    pixel_data = []
    lines = data_str.splitlines()
    for line in lines:
        line = line.split('//')[0].strip()  # Ignore comments after '//'
        if line:
            pixel_data.extend(int(num, 16) for num in re.findall(r'0x[0-9A-Fa-f]+', line))

    if len(pixel_data) != width * height:
        raise ValueError("Pixel data does not match the specified width and height")

    return width, height, pixel_data


def set_new_target_time(matrix, new_epoch):
    global ALARM_LEVEL, targetEpoch

    time_left_in_countdown["tm_ff"] = 0
    time_msg_vars["FINAL_COUNTDOWN"] = False
    BGFX_GLOBALS["bgEffect"] = BGFX_OFF
    ALARM_LEVEL = 0
    BGFX_GLOBALS["fcount"] = 0

    targetEpoch = new_epoch

    print("Current Datetime: ")
    print(datetime.now())
    print("Countdown Ends: ")
    print(datetime.fromtimestamp(targetEpoch))

    current_local_time = datetime.now()
    # Convert local time to epoch time
    epoch_time = current_local_time.timestamp()
    calc_time_difference(epoch_time, targetEpoch)

    print(messages["duringCountdownMsg"])
    print(get_formatted_time(matrix))


############################################
class TimeAndMessagesDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Countdown Settings')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove the help button

        # Create layout
        self.layout = QVBoxLayout()

        dt = datetime.fromtimestamp(targetEpoch)

        # Extract hours and minutes
        hours = dt.hour
        minutes = dt.minute

        # Create text boxes
        self.textbox1 = QLineEdit(self)
        self.textbox1.setText(f"{hours}:{minutes}")
        self.textbox2 = QLineEdit(self)
        self.textbox2.setText(messages["duringCountdownMsg"])
        self.textbox3 = QLineEdit(self)
        self.textbox3.setText(messages["afterCountdownMsg"])

        # Add text boxes to layout
        self.layout.addWidget(self.textbox1)
        self.layout.addWidget(self.textbox2)
        self.layout.addWidget(self.textbox3)

        # Create OK button
        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.on_ok_button_clicked)

        # Create button layout and add OK button
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)

        # Add button layout to main layout
        self.layout.addLayout(self.button_layout)

        # Set dialog layout
        self.setLayout(self.layout)

    def on_ok_button_clicked(self):
        # set new messages
        messages["duringCountdownMsg"] = self.textbox2.text()
        messages["afterCountdownMsg"] = self.textbox3.text()

        # set new end time for countdown
        hour, minutes = self.textbox1.text().split(':')
        new_epoch = get_next_time_target(int(hour), int(minutes))
        set_new_target_time(window.matrix, new_epoch)

        # Close the dialog
        self.accept()


class MxPixel:
    def __init__(self, is_on=False, color=(0, 0, 0)):
        """
        Initialize a pixel with an on/off bit flag and an RGB color value.

        :param is_on: Boolean flag indicating whether the pixel is on or off.
        :param color: A tuple representing the RGB color value of the pixel.
        """
        self.is_on = is_on
        self.color = color

    def __repr__(self):
        return f"Pixel(is_on={self.is_on}, color={self.color})"


class Matrix:
    def __init__(self, width, height, output_target):
        """
        Initialize the matrix with the given width and height.

        :param width: The width of the matrix.
        :param height: The height of the matrix.
        """
        self.width = width
        self.height = height
        self.output_target = output_target
        self.grid = [[MxPixel() for _ in range(width)] for _ in range(height)]

    def show(self):
        """
        Update the MainWindow's PixelDataCell widgets with the current matrix data.
        """
        pixel_data = []
        for row in self.grid:
            for pixel in row:
                if pixel.is_on:
                    pixel_data.append(pixel.color)
                else:
                    pixel_data.append((0, 0, 0))  # Default color for off pixels

        idx = 0
        for row in range(self.height):
            for col in range(self.width):
                color = pixel_data[idx]
                cell = self.output_target.grid_layout.itemAtPosition(row, col)
                if cell is not None:
                    widget = cell.widget()
                    if isinstance(widget, PixelDataCell):
                        widget.set_color(color)
                idx += 1
        # print(self)

    def clear(self):
        """
        Clear the matrix by setting all pixels to off.
        """
        for row in self.grid:
            for pixel in row:
                pixel.is_on = False
                pixel.color = (0, 0, 0)

    def set_pixel(self, x, y, is_on, color=(0, 0, 0)):
        """
        Set the properties of a pixel at a specific location in the matrix.

        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :param is_on: Boolean flag indicating whether the pixel is on or off.
        :param color: A tuple representing the RGB color value of the pixel.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].is_on = is_on
            self.grid[y][x].color = color
        else:
            # raise IndexError("Pixel coordinates out of bounds")
            pass

    def get_pixel(self, x, y):
        """
        Get the properties of a pixel at a specific location in the matrix.

        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :return: The pixel at the specified location.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        else:
            raise IndexError("Pixel coordinates out of bounds")

    def write(self, x, y, text, scale=1, color=(255, 0, 0), rotation=0):
        """
        Write a string to the matrix starting at the specified (x, y) position with scaling and rotation.

        :param x: The starting x-coordinate.
        :param y: The starting y-coordinate.
        :param text: The string to write to the matrix.
        :param scale: The scaling factor for the text.
        :param color: The RGB color value to use for the text.
        :param rotation: The rotation angle (0=0°, 1=90° CCW, 2=180°, 3=90° CW).
        """
        color_value = (color[0], color[1], color[2])

        for char in text:
            if char in CHAR_TO_INDEX:
                char_index = CHAR_TO_INDEX[char]
                char_data = ASCII_CHARACTERS[char_index]

                char_height = 7
                if char in ['g', 'j', 'p', 'q', 'y']:
                    char_height = 8

                # Convert the 1D char_data to a 2D matrix
                char_matrix = [char_data[i * 6:(i + 1) * 6] for i in range(char_height)]

                if rotation == 1:  # 90° CW
                    char_matrix = rotate_matrix(char_matrix, 270)
                    max_row, max_col = len(char_matrix), len(char_matrix[0])
                    # Adjust the starting coordinates
                    x_offset, y_offset = x, y
                elif rotation == 2:  # 180°
                    char_matrix = rotate_matrix(char_matrix, 180)
                    max_row, max_col = len(char_matrix), len(char_matrix[0])
                    x_offset, y_offset = x, y
                elif rotation == 3:  # 270° CCW
                    char_matrix = rotate_matrix(char_matrix, 90)
                    max_row, max_col = len(char_matrix), len(char_matrix[0])
                    # Adjust the starting coordinates
                    x_offset, y_offset = x - (max_row - 1) * scale, y - (max_col - 1) * scale
                else:  # 0°
                    max_row, max_col = len(char_matrix), len(char_matrix[0])
                    x_offset, y_offset = x, y

                # Draw the rotated character data
                for row in range(max_row):
                    for col in range(max_col):
                        if char_matrix[row][col] == '*':
                            # Scale the pixel
                            for dy in range(scale):
                                for dx in range(scale):
                                    self.set_pixel(x_offset + col * scale + dx, y_offset + row * scale + dy, True,
                                                   color_value)

                # Move to the next character position
                if rotation == 0:  # For 0°
                    x += max_col * scale
                elif rotation == 1:  # For 270°
                    y -= max_row * scale
                elif rotation == 3:  # For 90°
                    y += max_row * scale
                elif rotation == 2:  # For 180°
                    x -= max_col * scale

    def drawRGBBitmap(self, x, y, bitmap, w, h):
        """
        Draw an RGB bitmap at the given position.

        :param x: Starting x-coordinate on the matrix.
        :param y: Starting y-coordinate on the matrix.
        :param bitmap: Flat list of pixel values (in RGB565 format).
        :param w: Width of the bitmap.
        :param h: Height of the bitmap.
        """
        for j in range(h):
            for i in range(w):
                self.set_pixel(x + i, y + j, True, convert_16bit_to_rgb(bitmap[j * w + i]))

    def __repr__(self):
        return '\n'.join([''.join(['1' if pixel.is_on else '0' for pixel in row]) for row in self.grid])


class TestLogicWorker(QObject):
    show_matrix = pyqtSignal()

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix

    def run(self):
        """
        The method that runs in the separate thread.
        """
        txt = "☺ ☻ ♥ ♦ ♣ ♠ • ◘ ○ ♂ ♀ ♪ ♫ ☼ ► ◄ ↕ ‼ ¶ § ▬ ↨ ↑ ↓ → ← ∟ ↔ ▲ ▼ "
        scale = 1
        char_width = 6  # Width of each character in pixels
        text_len = len(txt) * (char_width * scale) + self.matrix.width
        x = self.matrix.width
        for _ in range(text_len):
            self.matrix.clear()
            self.matrix.write(x, 2, txt, scale, (0, 255, 0), 0)
            # self.matrix.show()
            self.show_matrix.emit()

            time.sleep(0.06)
            x -= 1


class GFXLogicWorker(QObject):
    show_matrix = pyqtSignal()

    ###################################################
    # Helpers
    def y_center_text(self, scale):
        return self.matrix.height // 2 - (((6 * scale) // 2) + (scale - 1))

    def send_bgfx_to_matrix(self):
        for index, value in enumerate(BGFX_GLOBALS["leds"]):
            self.matrix.set_pixel(index % self.matrix.width, index // self.matrix.width, True, value)

    def pan_or_bounce_bitmap(self, bitmap):
        bitmap_w, bitmap_h = bitmap[0], bitmap[1]
        mw, mh = self.matrix.width, self.matrix.height

        xf = max(0, (mw - bitmap_w) // 2) << 4
        yf = max(0, (mh - bitmap_h) // 2) << 4
        xfc = 6
        yfc = 3
        xfdir = -1
        yfdir = -1

        for i in range(1, 420):
            if APP_KILLED:
                return
            updDir = False
            x = xf >> 4
            y = yf >> 4

            self.matrix.clear()
            self.matrix.drawRGBBitmap(x, y, bitmap[2], bitmap_w, bitmap_h)
            self.show_matrix.emit()  # send update signal

            if bitmap_w - mw > 2:
                xf += xfc * xfdir
                if xf >= 0:
                    xfdir = -1
                    updDir = True
                if xf <= (mw - bitmap_w) << 4:
                    xfdir = 1
                    updDir = True

            if bitmap_h - mh > 2:
                yf += yfc * yfdir
                if yf >= 0:
                    yfdir = -1
                    updDir = True
                if yf <= (mh - bitmap_h) << 4:
                    yfdir = 1
                    updDir = True

            if mw > bitmap_w:
                xf += xfc * xfdir
                if xf >= (mw - bitmap_w) << 4:
                    xfdir = -1
                    updDir = True
                if xf <= 0:
                    xfdir = 1
                    updDir = True

            if mh > bitmap_h:
                yf += yfc * yfdir
                if yf >= (mh - bitmap_h) << 4:
                    yfdir = -1
                    updDir = True
                if yf <= 0:
                    yfdir = 1
                    updDir = True

            if updDir:
                xfc = constrain(xfc + random.randint(-1, 1), 3, 16)
                yfc = constrain(yfc + random.randint(-1, 1), 3, 16)

            time.sleep(self.speed / 1.5)

    def pan_or_bounce_animated_bitmap(self, bitmap_list, frame_interval, ani_length=420):
        mw, mh = self.matrix.width, self.matrix.height
        num_frames = len(bitmap_list)
        bitmap_w, bitmap_h = bitmap_list[0][0], bitmap_list[0][1]

        current_frame = 0
        count = 0

        xf = max(0, (mw - bitmap_w) // 2) << 4
        yf = max(0, (mh - bitmap_h) // 2) << 4
        xfc = 6
        yfc = 3
        xfdir = -1
        yfdir = -1

        for i in range(ani_length):
            if APP_KILLED:
                return
            updDir = False
            x = xf >> 4
            y = yf >> 4

            self.matrix.clear()
            self.matrix.drawRGBBitmap(x, y, bitmap_list[current_frame][2], bitmap_w, bitmap_h)
            self.show_matrix.emit()  # send update signal

            if bitmap_w - mw > 2:
                xf += xfc * xfdir
                if xf >= 0:
                    xfdir = -1
                    updDir = True
                if xf <= (mw - bitmap_w) << 4:
                    xfdir = 1
                    updDir = True

            if bitmap_h - mh > 2:
                yf += yfc * yfdir
                if yf >= 0:
                    yfdir = -1
                    updDir = True
                if yf <= (mh - bitmap_h) << 4:
                    yfdir = 1
                    updDir = True

            if mw > bitmap_w:
                xf += xfc * xfdir
                if xf >= (mw - bitmap_w) << 4:
                    xfdir = -1
                    updDir = True
                if xf <= 0:
                    xfdir = 1
                    updDir = True

            if mh > bitmap_h:
                yf += yfc * yfdir
                if yf >= (mh - bitmap_h) << 4:
                    yfdir = -1
                    updDir = True
                if yf <= 0:
                    yfdir = 1
                    updDir = True

            if updDir:
                xfc = constrain(xfc + random.randint(-1, 1), 3, 16)
                yfc = constrain(yfc + random.randint(-1, 1), 3, 16)

            time.sleep(self.speed / 1.5)

            # Advance Frame
            if num_frames > 1:
                count += 1
                if count % frame_interval == 0:
                    current_frame = (current_frame + 1) % num_frames

    #####################################################

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix
        self.speed = 0.035  # speed that matrix updates in seconds

        self.leaf = parse_progmem_data("leaf2.h")
        self.bong_a = parse_progmem_data("bonga.h")
        self.bong_b = parse_progmem_data("bongb.h")
        self.joint_a = parse_progmem_data("jointa.h")
        self.joint_b = parse_progmem_data("jointb.h")

    def GFX_loop(self):
        if APP_KILLED is False:
            self.pan_or_bounce_animated_bitmap([self.bong_a, self.bong_b], 12)
        if APP_KILLED is False:
            self.work_hard()
        if APP_KILLED is False:
            self.pan_or_bounce_bitmap(self.leaf)
        if APP_KILLED is False:
            self.how_high()
        if APP_KILLED is False:
            self.pan_or_bounce_animated_bitmap([self.joint_a, self.joint_b], 15)

    def work_hard(self):
        ltr_size = 1

        txt = "We work hard"
        txt2 = "and we"
        txt3 = "Smoke HARD!"

        mh = self.matrix.height
        mw = self.matrix.width

        txt_y_pos = self.y_center_text(ltr_size)
        txt2_pos = 0

        txt_len = text_width(txt, ltr_size)  # length of first message (txt)
        txt2_len = text_width(txt2, ltr_size)  # length of second message (txt2)
        txt3_len = text_width(txt3, 2)

        for x in range(mw, -txt_len - (mw - 16), -1):
            if APP_KILLED:
                return
            self.matrix.write(x, txt_y_pos, txt, ltr_size, LED_BLUE_HIGH, 0)

            if x < -(txt_len - 12):
                self.matrix.write(mw // 2 - ltr_size * 3, txt2_pos, txt2, ltr_size, LED_RED_HIGH, 1)
                txt2_pos += 1

            self.show_matrix.emit()  # send update signal
            time.sleep(self.speed)  # delay for 20ms
            self.matrix.clear()

        ltr_size = 2
        x = mw
        for step in range(txt3_len + mw):
            if APP_KILLED:
                return
            self.matrix.write(x - step, self.y_center_text(ltr_size), txt3, ltr_size, LED_ORANGE_HIGH, 0)
            self.show_matrix.emit()
            time.sleep(self.speed)
            self.matrix.clear()

    def how_high(self):
        mw, mh = self.matrix.width, self.matrix.height
        size = max(mw // 8, 1)

        for x in range(7, -38, -1):
            if APP_KILLED:
                return

            self.matrix.clear()
            self.matrix.write(x, 0, "How", 1, LED_PURPLE_HIGH, 0)

            if mh > 10:
                self.matrix.write(-18 - x, mh - 8, "Hi", 1, LED_RED_MEDIUM, 0)

            self.show_matrix.emit()  # send update signal
            time.sleep(self.speed)

        for x in range(-size * 6, 3 * size * 6 + mh, 1):
            if APP_KILLED:
                return
            self.matrix.clear()
            self.matrix.write(mw // 2 - size * 3 - 2, x, "RU?", size, LED_GREEN_MEDIUM, 1)
            self.show_matrix.emit()  # send update signal
            time.sleep(self.speed / 1.5)

    def run(self):
        """
        The method that runs in the separate thread.
        """
        global runGFXloop, targetEpoch, ALARM_LEVEL
        from CountDownTimer import COUNTDOWN_OVER, FINAL_MOMENTS, LAST_10_MIN

        ALARM_LEVEL = 0

        # set_system_time(get_ntp_time())
        targetEpoch = get_next_time_target(16, 20)
        msg = messages["duringCountdownMsg"]

        while APP_KILLED is False:
            currentMillis = GET_MILLIS()

            if not COUNTDOWN_OVER():
                if (time_msg_vars["UpdateMessage"] is True
                        or currentMillis - time_msg_vars["previousMillis"] >= interval):
                    time_msg_vars["UpdateMessage"] = False
                    time_msg_vars["previousMillis"] = currentMillis

                    # Get the current local time
                    current_local_time = datetime.now()
                    # Convert local time to epoch time
                    epoch_time = current_local_time.timestamp()

                    calc_time_difference(epoch_time, targetEpoch)

                    if COUNTDOWN_OVER():
                        if BGFX_GLOBALS["bgEffect"] != BGFX_PARTY:
                            BGFX_GLOBALS["bgEffect"] = BGFX_PARTY
                        msg = messages["afterCountdownMsg"]
                        print(msg)
                    elif FINAL_MOMENTS() or time_msg_vars["TextOrTime"] is True:
                        if ALARM_LEVEL < 2 and FINAL_MOMENTS():
                            ALARM_LEVEL = 2
                            # print(":::Alarm Two:::")
                            self.matrix.output_target.show()
                            self.matrix.output_target.sound_player.play("r2.mp3")
                        if time_msg_vars["FINAL_COUNTDOWN"] and BGFX_GLOBALS["bgEffect"] != BGFX_PULSE:
                            BGFX_GLOBALS["bgEffect"] = BGFX_PULSE
                        elif FINAL_MOMENTS() and not time_msg_vars["FINAL_COUNTDOWN"] \
                                and BGFX_GLOBALS["bgEffect"] != BGFX_OUTLINE:
                            BGFX_GLOBALS["bgEffect"] = BGFX_OUTLINE
                        msg = get_formatted_time(self.matrix)

                    else:
                        if LAST_10_MIN() and BGFX_GLOBALS["bgEffect"] != BGFX_OUTLINE:
                            BGFX_GLOBALS["bgEffect"] = BGFX_OUTLINE
                            if ALARM_LEVEL < 1:
                                ALARM_LEVEL = 1
                                # print(":::Alarm One:::")
                                self.matrix.output_target.show()
                                self.matrix.output_target.sound_player.play("RedAlert.mp3")
                        msg = messages["duringCountdownMsg"]
            else:
                if ALARM_LEVEL < 3:
                    ALARM_LEVEL = 3
                    # print(":::Time's Up:::")
                    self.matrix.output_target.show()
                    self.matrix.output_target.sound_player.play("tu1.mp3")
                if currentMillis - time_msg_vars["previousMillis"] >= tokingTime:
                    new_epoch = targetEpoch + 3600 * 24  # add a day
                    set_new_target_time(self.matrix, new_epoch)

            self.matrix.clear()
            generateBGFX()
            self.send_bgfx_to_matrix()

            if printMessage(msg, self.matrix):
                time_msg_vars["TextOrTime"] = not time_msg_vars["TextOrTime"]
                time_msg_vars["UpdateMessage"] = True

                if not time_msg_vars["TextOrTime"] and time_left_in_countdown["tm_ff"] == 0:
                    runGFXloop = True

            self.show_matrix.emit()  # send update signal
            time.sleep(self.speed)

            if runGFXloop:
                self.GFX_loop()
                runGFXloop = False


# Custom widget for each pixel cell
class PixelDataCell(QWidget):
    def __init__(self, idx, color, size=20, spacing=4, parent=None):
        super().__init__(parent)
        self.setMinimumSize(size, size)  # Set the size of each cell
        self.setAutoFillBackground(True)
        self.index = idx
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        self.color = color  # Store the color
        self.spacing = spacing

    # Modify paintEvent in CellWidget class
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Optional: for smoother edges

        try:
            painter.setBrush(QColor(*self.color))  # Use the specified color
        except Exception as e:
            print(f"color: {self.color} \n\n {e}")
            return

        # Calculate radius with additional spacing
        spacing = self.spacing
        painter.setPen(Qt.NoPen)  # No outline
        radius = (min(self.width(), self.height()) - spacing) // 2

        center = self.rect().center()
        painter.drawEllipse(center, radius, radius)

    def set_color(self, color):
        self.color = color
        self.update()

    def get_rgb565_color(self):
        return qcolor_to_rgb565(self.color)


class MainWindow(QWidget):

    def quitEvent(self, event):
        global APP_KILLED
        APP_KILLED = True
        self.sound_player.stop()
        self.thread.quit()
        self.thread.wait()
        QApplication.instance().quit()

    def __init__(self, width, height, pixel_data):
        super().__init__()
        self.tray_icon = QSystemTrayIcon(QIcon('icon.png'), self)
        self.sound_player = PlaySound()

        # Set the shortcut for Alt+T
        shortcut = QShortcut(QKeySequence("Alt+T"), self)
        shortcut.activated.connect(self.show_dialog)

        self.width = width
        self.height = height
        self.title = "420 Countdown Matrix"
        self.offset = None

        self.img_width = width
        self.img_height = height

        main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

        self.grid_layout.setSpacing(1)
        self.pixel_data_cells = []

        idx = 0
        for row in range(height):
            for col in range(width):
                pixel_data[idx] = (0, 0, 0)
                cell = PixelDataCell(idx, pixel_data[idx], 10, 2, self)
                self.grid_layout.addWidget(cell, row, col)
                self.pixel_data_cells.append(cell)
                idx += 1

        main_layout.addLayout(self.grid_layout)
        self.setLayout(main_layout)
        self.setWindowTitle(f"{self.title}")

        # Set the window flags to remove the titlebar and make the window frameless
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowCloseButtonHint | \
                            Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)

        self.setStyleSheet("background-color: #111111;")

        # create matrix buffer for emulated led output
        self.matrix = Matrix(width, height, self)
        # spin up thread that will handle matrix display logic
        self.thread = QThread()
        self.worker = GFXLogicWorker(self.matrix)
        self.worker.moveToThread(self.thread)
        # Connect worker signals to slots
        self.worker.show_matrix.connect(self.show_matrix)
        # Start worker
        self.thread.started.connect(self.worker.run)
        self.thread.start()

        # Variables for custom resizing (**mouse cursor not changing until clicked)
        self._startPos = None
        self._isResizing = False
        self._resizeEdge = None

        # Create a menu for the tray icon
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet("""
            QMenu {
                background-color: #353535;
                color: #CECECE; 
            }
            QMenu::item {
                background-color: transparent;
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #666666;  /* Highlight color */
            }
        """)

        # Add a title to the menu
        title_action = QWidgetAction(self.tray_menu)
        title_label = QLabel("420 Countdown")
        title_label.setStyleSheet("QLabel { padding: 5px; font-weight: bold; color: #CECECE;}")
        title_action.setDefaultWidget(title_label)
        self.tray_menu.addAction(title_action)

        # Add a separator for visual clarity
        self.tray_menu.addSeparator()

        # Add a show action
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        self.tray_menu.addAction(show_action)

        # Add a hide action
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        self.tray_menu.addAction(hide_action)

        # Add a quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quitEvent)
        self.tray_menu.addAction(quit_action)

        # Set the menu to the tray icon
        self.tray_icon.setContextMenu(self.tray_menu)

        # Show the tray icon
        self.tray_icon.show()

        # Connect the tray icon activated signal
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def closeEvent(self, event):
        # Override the close event to minimize to tray instead of exiting
        event.ignore()
        self.hide()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._startPos = event.globalPos()
            self._isResizing, self._resizeEdge = self._getResizeEdge(event.pos())
            if not self._isResizing:
                self._dragPos = event.globalPos()

        elif event.button() == Qt.RightButton:
            print("right Click")
            self.mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._isResizing:
            self._resizeWindow(event.globalPos())
        else:
            self._moveWindow(event.globalPos())
        self._updateCursorShape(event.pos())

    def mouseReleaseEvent(self, event):
        self._startPos = None
        self._dragPos = None
        self._isResizing = False
        self._resizeEdge = None
        self.unsetCursor()

    def _moveWindow(self, pos):
        if self._dragPos is not None:
            delta = pos - self._dragPos
            self.move(self.pos() + delta)
            self._dragPos = pos

    def _resizeWindow(self, pos):
        delta = pos - self._startPos
        rect = self.geometry()

        if self._resizeEdge == "top":
            rect.setTop(rect.top() + delta.y())
        elif self._resizeEdge == "bottom":
            rect.setBottom(rect.bottom() + delta.y())
        elif self._resizeEdge == "left":
            rect.setLeft(rect.left() + delta.x())
        elif self._resizeEdge == "right":
            rect.setRight(rect.right() + delta.x())
        elif self._resizeEdge == "top-left":
            rect.setTop(rect.top() + delta.y())
            rect.setLeft(rect.left() + delta.x())
        elif self._resizeEdge == "top-right":
            rect.setTop(rect.top() + delta.y())
            rect.setRight(rect.right() + delta.x())
        elif self._resizeEdge == "bottom-left":
            rect.setBottom(rect.bottom() + delta.y())
            rect.setLeft(rect.left() + delta.x())
        elif self._resizeEdge == "bottom-right":
            rect.setBottom(rect.bottom() + delta.y())
            rect.setRight(rect.right() + delta.x())

        self.setGeometry(rect)
        self._startPos = pos

    def _getResizeEdge(self, pos):
        margin = 10
        rect = self.rect()
        top, bottom, left, right = rect.top(), rect.bottom(), rect.left(), rect.right()

        if pos.x() < left + margin and pos.y() < top + margin:
            return True, "top-left"
        elif pos.x() > right - margin and pos.y() < top + margin:
            return True, "top-right"
        elif pos.x() < left + margin and pos.y() > bottom - margin:
            return True, "bottom-left"
        elif pos.x() > right - margin and pos.y() > bottom - margin:
            return True, "bottom-right"
        elif pos.y() < top + margin:
            return True, "top"
        elif pos.y() > bottom - margin:
            return True, "bottom"
        elif pos.x() < left + margin:
            return True, "left"
        elif pos.x() > right - margin:
            return True, "right"
        else:
            return False, None

    def _updateCursorShape(self, pos):
        _, edge = self._getResizeEdge(pos)
        if edge in ["top-left", "bottom-right"]:
            self.setCursor(Qt.SizeFDiagCursor)
        elif edge in ["top-right", "bottom-left"]:
            self.setCursor(Qt.SizeBDiagCursor)
        elif edge in ["top", "bottom"]:
            self.setCursor(Qt.SizeVerCursor)
        elif edge in ["left", "right"]:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.unsetCursor()

    @pyqtSlot()
    def show_matrix(self):
        self.matrix.show()

    def show_dialog(self):
        dialog = TimeAndMessagesDialog()
        dialog.exec_()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.ico'))
    window = MainWindow(44, 11, {})
    window.show()
    sys.exit(app.exec_())
