import time
import math
import random

from ColorDefinitions import *

# Constants
LINEARBLEND = 'linearblend'
LINEARBLEND_NOWRAP = 1
NOBLEND = 2
FASTLED_SCALE8_FIXED = 0
BGFX_OFF = 0
BGFX_OUTLINE = 1
BGFX_PARTY = 2
BGFX_PULSE = 3

MATRIX_WIDTH = 44
MATRIX_HEIGHT = 11
NUM_LEDS = MATRIX_WIDTH * MATRIX_HEIGHT

BGFX_GLOBALS = {
    "pulseIn_start": False,
    "bgEffect": BGFX_OFF,
    "patternIndex": 0,
    "fcount": 0,
    "leds": [(0, 0, 0)] * NUM_LEDS
}

currentPalette = RainbowColors_p
paletteNum = 0
currentBlending = LINEARBLEND
loopCount = 0
count = 0
sPseudotime = 0
sLastMillis = 0
sHue16 = 0
hue = 0
sweepCount = 0
BRIGHTNESS = 128


# Helper functions
def random8():
    return random.randint(0, 255)


def map8(x, a, b):
    return a + (b - a) * x // 255


def lsrX4(x):
    return x >> 4


def scale8_LEAVING_R1_DIRTY(value, scale):
    return (value * scale) // 256


def cleanup_R1():
    pass


def ColorFromPalette(pal, index, brightness, blendType):
    if blendType == LINEARBLEND_NOWRAP:
        index = map8(index, 0, 239)

    index = 1 + index % 255
    hi4 = lsrX4(index)
    lo4 = index & 0x0F

    entry = pal[hi4]

    red1, green1, blue1 = entry

    blend = lo4 and (blendType != NOBLEND)

    if blend:
        if hi4 == 15:
            entry = pal[0]
        else:
            entry = pal[hi4 + 1]

        f2 = lo4 << 4
        f1 = 255 - f2

        red2, green2, blue2 = entry

        red1 = scale8_LEAVING_R1_DIRTY(red1, f1)
        red2 = scale8_LEAVING_R1_DIRTY(red2, f2)
        red1 += red2

        green1 = scale8_LEAVING_R1_DIRTY(green1, f1)
        green2 = scale8_LEAVING_R1_DIRTY(green2, f2)
        green1 += green2

        blue1 = scale8_LEAVING_R1_DIRTY(blue1, f1)
        blue2 = scale8_LEAVING_R1_DIRTY(blue2, f2)
        blue1 += blue2

        cleanup_R1()

    if brightness != 255:
        if brightness:
            brightness += 1
            if red1:
                red1 = scale8_LEAVING_R1_DIRTY(red1, brightness)
                if not FASTLED_SCALE8_FIXED:
                    red1 += 1
            if green1:
                green1 = scale8_LEAVING_R1_DIRTY(green1, brightness)
                if not FASTLED_SCALE8_FIXED:
                    green1 += 1
            if blue1:
                blue1 = scale8_LEAVING_R1_DIRTY(blue1, brightness)
                if not FASTLED_SCALE8_FIXED:
                    blue1 += 1
            cleanup_R1()
        else:
            red1 = 0
            green1 = 0
            blue1 = 0

    return red1, green1, blue1


def GET_MILLIS():
    """ Return the current time in milliseconds. """
    return int(round(time.time() * 1000))


def scale16(value, scale):
    """ Scale a 16-bit value by another 16-bit value. """
    return (value * scale) >> 16


def sin16(x):
    """ Compute a sine wave for a 16-bit input. """
    return int((math.sin(x * (2 * math.pi / 65536)) * 32767) + 32768)


def beat88(beats_per_minute_88, timebase=0):
    """
    Generates a 16-bit "sawtooth" wave at a given BPM, with BPM specified in Q8.8 fixed-point format.
    :param beats_per_minute_88: the frequency of the wave, in Q8.8 format
    :param timebase: the time offset of the wave from the millis() timer
    :return: 16-bit sawtooth wave value
    """
    # BPM is 'beats per minute', or 'beats per 60000ms'.
    # To avoid using the (slower) division operator, we
    # want to convert 'beats per 60000ms' to 'beats per 65536ms',
    # and then use a simple, fast bit-shift to divide by 65536.
    #
    # The ratio 65536:60000 is 279.620266667:256; we'll call it 280:256.
    # The conversion is accurate to about 0.05%, more or less,
    # e.g. if you ask for "120 BPM", you'll get about "119.93".
    return ((GET_MILLIS() - timebase) * beats_per_minute_88 * 280) >> 16


def beatsin88(beats_per_minute_88, lowest=0, highest=65535, timebase=0, phase_offset=0):
    """
    Generates a 16-bit sine wave at a given BPM that oscillates within a given range.
    :param beats_per_minute_88: the frequency of the wave, in Q8.8 format
    :param lowest: the lowest output value of the sine wave
    :param highest: the highest output value of the sine wave
    :param timebase: the time offset of the wave from the millis() timer
    :param phase_offset: phase offset of the wave from the current position
    :return: 16-bit sine wave value within the specified range
    """
    beat = beat88(beats_per_minute_88, timebase)
    beatsin = (sin16(beat + phase_offset) + 32768)
    rangewidth = highest - lowest
    scaledbeat = scale16(beatsin, rangewidth)
    result = lowest + scaledbeat
    return result


def nblend(led, newcolor, blend_amount):
    r = (led[0] * (255 - blend_amount) + newcolor[0] * blend_amount) // 255
    g = (led[1] * (255 - blend_amount) + newcolor[1] * blend_amount) // 255
    b = (led[2] * (255 - blend_amount) + newcolor[2] * blend_amount) // 255
    return r, g, b


def CHSV(hue, sat, val):
    # Simplified CHSV function to convert HSV to RGB (assuming full saturation and brightness)
    c = val * sat // 255
    x = c * (1 - abs((hue // 42) % 2 - 1))
    m = val - c

    if hue < 42:
        r, g, b = c, x, 0
    elif hue < 84:
        r, g, b = x, c, 0
    elif hue < 126:
        r, g, b = 0, c, x
    elif hue < 168:
        r, g, b = 0, x, c
    elif hue < 210:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    # Ensure values are within 0-255 range
    r = max(0, (r+m)) % 256
    g = max(0, (g+m)) % 256
    b = max(0, (b+m)) % 256

    return r, g, b


def nscale8(leds, num_leds, scale):
    """
    Scales the brightness of the LED colors by a given scale.
    :param leds: List of dictionaries representing the LED colors
    :param num_leds: Number of LEDs in the list
    :param scale: Scale factor to adjust the brightness
    """
    for i in range(num_leds):
        r = (leds[i][0] * scale) >> 8
        g = (leds[i][1] * scale) >> 8
        b = (leds[i][2] * scale) >> 8
        leds[i] = (r, g, b)


def fadeToBlackBy(leds, num_leds, fadeBy):
    """
    Fades the LED colors to black by a given factor.
    :param leds: List of dictionaries representing the LED colors
    :param num_leds: Number of LEDs in the list
    :param fadeBy: Amount to fade the colors by
    """
    nscale8(leds, num_leds, 255 - fadeBy)


def reverse_steps_alternate(arr, width):
    # Flag to determine whether to reverse or not
    reverse_flag = False

    # Iterate through the array in steps of width
    for i in range(0, len(arr), width):
        if reverse_flag:
            # Reverse the current segment of width elements
            arr[i:i + width] = arr[i:i + width][::-1]
        # Toggle the flag
        reverse_flag = not reverse_flag


def FillLEDsFromPaletteColors(patternIndex):
    global currentPalette, currentBlending
    for i in range(NUM_LEDS):
        # print(i)
        BGFX_GLOBALS["leds"][i] = ColorFromPalette(currentPalette, patternIndex, BRIGHTNESS, currentBlending)
        patternIndex += 3


HUE_PURPLE = 160
HUE_GREEN = 96

PurpleAndGreen_p = [
    CHSV(HUE_GREEN, 255, 255), CHSV(HUE_GREEN, 255, 255), Black, Black,
    CHSV(HUE_PURPLE, 255, 255), CHSV(HUE_PURPLE, 255, 255), Black, Black,
    CHSV(HUE_GREEN, 255, 255), CHSV(HUE_GREEN, 255, 255), Black, Black,
    CHSV(HUE_PURPLE, 255, 255), CHSV(HUE_PURPLE, 255, 255), Black, Black
]


def SetupTotallyRandomPalette():
    currentPalette = []
    for _ in range(16):
        hue = random8()
        value = random8()
        currentPalette.append(CHSV(hue, 255, value))
    return currentPalette


def ChangePalette():
    global currentPalette, currentBlending, paletteNum
    paletteNum += 1

    if paletteNum == 0:
        currentPalette = RainbowColors_p
        currentBlending = LINEARBLEND
    elif paletteNum == 1:
        currentPalette = RainbowStripeColors_p
        currentBlending = NOBLEND
    elif paletteNum == 2:
        currentPalette = RainbowStripeColors_p
        currentBlending = LINEARBLEND
    elif paletteNum == 3:
        currentPalette = PurpleAndGreen_p
        currentBlending = LINEARBLEND
    elif paletteNum == 4:
        SetupTotallyRandomPalette()
        currentBlending = LINEARBLEND
    elif paletteNum == 5:
        currentPalette = BlackAndWhiteStrip_p
        currentBlending = NOBLEND
    elif paletteNum == 6:
        currentPalette = BlackAndWhiteStrip_p
        currentBlending = LINEARBLEND
    elif paletteNum == 7:
        currentPalette = CloudColors_p
        currentBlending = LINEARBLEND
    elif paletteNum == 8:
        currentPalette = PartyColors_p
        currentBlending = LINEARBLEND
    elif paletteNum == 9:
        currentPalette = myRedWhiteBluePalette_p
        currentBlending = NOBLEND
    elif paletteNum == 10:
        currentPalette = myRedWhiteBluePalette_p
        currentBlending = LINEARBLEND
    else:
        paletteNum = 0
        currentPalette = RainbowColors_p
        currentBlending = LINEARBLEND


def RainbowSweep():
    global loopCount, hue, sweepCount
    ledIndex = 0

    # Fade everything out
    fadeToBlackBy(BGFX_GLOBALS["leds"], NUM_LEDS, 36)

    if sweepCount > MATRIX_HEIGHT + MATRIX_WIDTH:
        sweepCount = 0

    # PERIMETER SWEEP
    # Left / Right Sides
    if sweepCount < MATRIX_HEIGHT:
        ledIndex = sweepCount * MATRIX_WIDTH
    # Top / Bottom Sides
    elif MATRIX_HEIGHT <= sweepCount < MATRIX_HEIGHT + MATRIX_WIDTH:
        ledIndex = NUM_LEDS - MATRIX_WIDTH + sweepCount - MATRIX_HEIGHT

    hue = (hue + 2) % 256

    # Led index and inverse index set to match
    BGFX_GLOBALS["leds"][ledIndex] = CHSV(hue, 255, 255)
    BGFX_GLOBALS["leds"][NUM_LEDS - 1 - ledIndex] = CHSV(hue, 255, 255)

    sweepCount += 1


def final_countdown(start, length):
    numLEDS = length
    global sPseudotime, sLastMillis, sHue16

    sat8 = beatsin88(87, 220, 250)
    brightdepth = beatsin88(341, 96, 224)
    brightnessthetainc16 = beatsin88(203, 25 * 256, 40 * 256)
    msmultiplier = beatsin88(147, 23, 60)

    hue16 = sHue16
    hueinc16 = beatsin88(113, 1, 3000)

    ms = GET_MILLIS()
    deltams = ms - sLastMillis
    sLastMillis = ms
    sPseudotime += deltams * msmultiplier
    sHue16 += deltams * beatsin88(400, 5, 9)
    brightnesstheta16 = sPseudotime

    if BGFX_GLOBALS["pulseIn_start"] is True:
        BGFX_GLOBALS["fcount"] += 1
        for i in range(length):
            if (i % 6) < 2:
                continue
            hue16 += hueinc16
            hue8 = hue16 // 256
            brightnesstheta16 += brightnessthetainc16
            b16 = sin16(brightnesstheta16) + 32768
            bri16 = (b16 * b16) // 65536
            bri8 = (bri16 * brightdepth) // 65536
            bri8 += (255 - brightdepth)

            newcolor = CHSV(hue8, sat8, bri8)
            pixelnumber = (numLEDS - 1) - i
            BGFX_GLOBALS["leds"][pixelnumber + start] = nblend(BGFX_GLOBALS["leds"][pixelnumber + start], newcolor, 64)
    else:
        fadeToBlackBy(BGFX_GLOBALS["leds"], NUM_LEDS, 40)

    if BGFX_GLOBALS["fcount"] > 8:
        BGFX_GLOBALS["fcount"] = 0
        BGFX_GLOBALS["pulseIn_start"] = False


def generateBGFX():
    global count

    if BGFX_GLOBALS["bgEffect"] == BGFX_OFF:
        fadeToBlackBy(BGFX_GLOBALS["leds"], NUM_LEDS, 40)
    elif BGFX_GLOBALS["bgEffect"] == BGFX_OUTLINE:
        RainbowSweep()
    elif BGFX_GLOBALS["bgEffect"] == BGFX_PARTY:
        count += 1
        FillLEDsFromPaletteColors(BGFX_GLOBALS["patternIndex"])
        reverse_steps_alternate(BGFX_GLOBALS["leds"], MATRIX_WIDTH)
        BGFX_GLOBALS["patternIndex"] += 1
        if count % 300 == 0:
            ChangePalette()
    elif BGFX_GLOBALS["bgEffect"] == BGFX_PULSE:
        final_countdown(MATRIX_WIDTH * 4, MATRIX_WIDTH * 3)
        #reverse_steps_alternate(BGFX_GLOBALS["leds"], MATRIX_WIDTH)
    else:
        BGFX_GLOBALS["bgEffect"] = BGFX_OFF
