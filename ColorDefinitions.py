def convert_16bit_to_rgb(value):
    r = ((value >> 11) & 0x1F) * 255 // 31
    g = ((value >> 5) & 0x3F) * 255 // 63
    b = (value & 0x1F) * 255 // 31
    return r, g, b


# Color definitions
LED_BLACK = (0, 0, 0)

LED_RED_VERYLOW = convert_16bit_to_rgb(3 << 11)
LED_RED_LOW = convert_16bit_to_rgb(7 << 11)
LED_RED_MEDIUM = convert_16bit_to_rgb(15 << 11)
LED_RED_HIGH = convert_16bit_to_rgb(31 << 11)

LED_GREEN_VERYLOW = convert_16bit_to_rgb(1 << 5)
LED_GREEN_LOW = convert_16bit_to_rgb(15 << 5)
LED_GREEN_MEDIUM = convert_16bit_to_rgb(31 << 5)
LED_GREEN_HIGH = convert_16bit_to_rgb(63 << 5)

LED_BLUE_VERYLOW = convert_16bit_to_rgb(3)
LED_BLUE_LOW = convert_16bit_to_rgb(7)
LED_BLUE_MEDIUM = convert_16bit_to_rgb(15)
LED_BLUE_HIGH = convert_16bit_to_rgb(31)

LED_ORANGE_VERYLOW = convert_16bit_to_rgb((3 << 11) + (1 << 5))
LED_ORANGE_LOW = convert_16bit_to_rgb((7 << 11) + (15 << 5))
LED_ORANGE_MEDIUM = convert_16bit_to_rgb((15 << 11) + (31 << 5))
LED_ORANGE_HIGH = convert_16bit_to_rgb((31 << 11) + (63 << 5))

LED_PURPLE_VERYLOW = convert_16bit_to_rgb((3 << 11) + 3)
LED_PURPLE_LOW = convert_16bit_to_rgb((7 << 11) + 7)
LED_PURPLE_MEDIUM = convert_16bit_to_rgb((15 << 11) + 15)
LED_PURPLE_HIGH = convert_16bit_to_rgb((31 << 11) + 31)

LED_CYAN_VERYLOW = convert_16bit_to_rgb((1 << 5) + 3)
LED_CYAN_LOW = convert_16bit_to_rgb((15 << 5) + 7)
LED_CYAN_MEDIUM = convert_16bit_to_rgb((31 << 5) + 15)
LED_CYAN_HIGH = convert_16bit_to_rgb((63 << 5) + 31)

LED_WHITE_VERYLOW = convert_16bit_to_rgb((3 << 11) + (1 << 5) + 3)
LED_WHITE_LOW = convert_16bit_to_rgb((7 << 11) + (15 << 5) + 7)
LED_WHITE_MEDIUM = convert_16bit_to_rgb((15 << 11) + (31 << 5) + 15)
LED_WHITE_HIGH = convert_16bit_to_rgb((31 << 11) + (63 << 5) + 31)


AliceBlue = (240, 248, 255)
Amethyst = (153, 102, 204)
AntiqueWhite = (250, 235, 215)
Aqua = (0, 255, 255)
Aquamarine = (127, 255, 212)
Azure = (240, 255, 255)
Beige = (245, 245, 220)
Bisque = (255, 228, 196)
Black = (0, 0, 0)
BlanchedAlmond = (255, 235, 205)
Blue = (0, 0, 255)
BlueViolet = (138, 43, 226)
Brown = (165, 42, 42)
BurlyWood = (222, 184, 135)
CadetBlue = (95, 158, 160)
Chartreuse = (127, 255, 0)
Chocolate = (210, 105, 30)
Coral = (255, 127, 80)
CornflowerBlue = (100, 149, 237)
Cornsilk = (255, 248, 220)
Crimson = (220, 20, 60)
Cyan = (0, 255, 255)
DarkBlue = (0, 0, 139)
DarkCyan = (0, 139, 139)
DarkGoldenrod = (184, 134, 11)
DarkGray = (169, 169, 169)
DarkGrey = (169, 169, 169)
DarkGreen = (0, 100, 0)
DarkKhaki = (189, 183, 107)
DarkMagenta = (139, 0, 139)
DarkOliveGreen = (85, 107, 47)
DarkOrange = (255, 140, 0)
DarkOrchid = (153, 50, 204)
DarkRed = (139, 0, 0)
DarkSalmon = (233, 150, 122)
DarkSeaGreen = (143, 188, 143)
DarkSlateBlue = (72, 61, 139)
DarkSlateGray = (47, 79, 79)
DarkSlateGrey = (47, 79, 79)
DarkTurquoise = (0, 206, 209)
DarkViolet = (148, 0, 211)
DeepPink = (255, 20, 147)
DeepSkyBlue = (0, 191, 255)
DimGray = (105, 105, 105)
DimGrey = (105, 105, 105)
DodgerBlue = (30, 144, 255)
FireBrick = (178, 34, 34)
FloralWhite = (255, 250, 240)
ForestGreen = (34, 139, 34)
Fuchsia = (255, 0, 255)
Gainsboro = (220, 220, 220)
GhostWhite = (248, 248, 255)
Gold = (255, 215, 0)
Goldenrod = (218, 165, 32)
Gray = (128, 128, 128)
Grey = (128, 128, 128)
Green = (0, 128, 0)
GreenYellow = (173, 255, 47)
Honeydew = (240, 255, 240)
HotPink = (255, 105, 180)
IndianRed = (205, 92, 92)
Indigo = (75, 0, 130)
Ivory = (255, 255, 240)
Khaki = (240, 230, 140)
Lavender = (230, 230, 250)
LavenderBlush = (255, 240, 245)
LawnGreen = (124, 252, 0)
LemonChiffon = (255, 250, 205)
LightBlue = (173, 216, 230)
LightCoral = (240, 128, 128)
LightCyan = (224, 255, 255)
LightGoldenrodYellow = (250, 250, 210)
LightGreen = (144, 238, 144)
LightGrey = (211, 211, 211)
LightPink = (255, 182, 193)
LightSalmon = (255, 160, 122)
LightSeaGreen = (32, 178, 170)
LightSkyBlue = (135, 206, 250)
LightSlateGray = (119, 136, 153)
LightSlateGrey = (119, 136, 153)
LightSteelBlue = (176, 196, 222)
LightYellow = (255, 255, 224)
Lime = (0, 255, 0)
LimeGreen = (50, 205, 50)
Linen = (250, 240, 230)
Magenta = (255, 0, 255)
Maroon = (128, 0, 0)
MediumAquamarine = (102, 205, 170)
MediumBlue = (0, 0, 205)
MediumOrchid = (186, 85, 211)
MediumPurple = (147, 112, 219)
MediumSeaGreen = (60, 179, 113)
MediumSlateBlue = (123, 104, 238)
MediumSpringGreen = (0, 250, 154)
MediumTurquoise = (72, 209, 204)
MediumVioletRed = (199, 21, 133)
MidnightBlue = (25, 25, 112)
MintCream = (245, 255, 250)
MistyRose = (255, 228, 225)
Moccasin = (255, 228, 181)
NavajoWhite = (255, 222, 173)
Navy = (0, 0, 128)
OldLace = (253, 245, 230)
Olive = (128, 128, 0)
OliveDrab = (107, 142, 35)
Orange = (255, 165, 0)
OrangeRed = (255, 69, 0)
Orchid = (218, 112, 214)
PaleGoldenrod = (238, 232, 170)
PaleGreen = (152, 251, 152)
PaleTurquoise = (175, 238, 238)
PaleVioletRed = (219, 112, 147)
PapayaWhip = (255, 239, 213)
PeachPuff = (255, 218, 185)
Peru = (205, 133, 63)
Pink = (255, 192, 203)
Plaid = (204, 85, 51)
Plum = (221, 160, 221)
PowderBlue = (176, 224, 230)
Purple = (128, 0, 128)
Red = (255, 0, 0)
RosyBrown = (188, 143, 143)
RoyalBlue = (65, 105, 225)
SaddleBrown = (139, 69, 19)
Salmon = (250, 128, 114)
SandyBrown = (244, 164, 96)
SeaGreen = (46, 139, 87)
Seashell = (255, 245, 238)
Sienna = (160, 82, 45)
Silver = (192, 192, 192)
SkyBlue = (135, 206, 235)
SlateBlue = (106, 90, 205)
SlateGray = (112, 128, 144)
SlateGrey = (112, 128, 144)
Snow = (255, 250, 250)
SpringGreen = (0, 255, 127)
SteelBlue = (70, 130, 180)
Tan = (210, 180, 140)
Teal = (0, 128, 128)
Thistle = (216, 191, 216)
Tomato = (255, 99, 71)
Turquoise = (64, 224, 208)
Violet = (238, 130, 238)
Wheat = (245, 222, 179)
White = (255, 255, 255)
WhiteSmoke = (245, 245, 245)
Yellow = (255, 255, 0)
YellowGreen = (154, 205, 50)



#########################################
# Palette Definitions

CloudColors_p = [
    Blue,
    DarkBlue,
    DarkBlue,
    DarkBlue,

    DarkBlue,
    DarkBlue,
    DarkBlue,
    DarkBlue,

    Blue,
    DarkBlue,
    SkyBlue,
    SkyBlue,

    LightBlue,
    White,
    LightBlue,
    SkyBlue
]


LavaColors_p = [
    Black,
    Maroon,
    Black,
    Maroon,

    DarkRed,
    DarkRed,
    Maroon,
    DarkRed,

    DarkRed,
    DarkRed,
    Red,
    Orange,

    White,
    Orange,
    Red,
    DarkRed
]


OceanColors_p = [
    MidnightBlue,
    DarkBlue,
    MidnightBlue,
    Navy,

    DarkBlue,
    MediumBlue,
    SeaGreen,
    Teal,

    CadetBlue,
    Blue,
    DarkCyan,
    CornflowerBlue,

    Aquamarine,
    SeaGreen,
    Aqua,
    LightSkyBlue
]


ForestColors_p = [
    DarkGreen,
    DarkGreen,
    DarkOliveGreen,
    DarkGreen,

    Green,
    ForestGreen,
    OliveDrab,
    Green,

    SeaGreen,
    MediumAquamarine,
    LimeGreen,
    YellowGreen,

    LightGreen,
    LawnGreen,
    MediumAquamarine,
    ForestGreen
]


RainbowColors_p = [
    (255, 0, 0), (213, 42, 0), (171, 85, 0), (171, 127, 0),
    (171, 171, 0), (86, 213, 0), (0, 255, 0), (0, 213, 42),
    (0, 171, 85), (0, 86, 170), (0, 0, 255), (42, 0, 213),
    (85, 0, 171), (127, 0, 129), (171, 0, 85), (213, 0, 43)
]


RainbowStripeColors_p = [
    (255, 0, 0), (0, 0, 0), (171, 85, 0), (0, 0, 0),
    (171, 171, 0), (0, 0, 0), (0, 255, 0), (0, 0, 0),
    (0, 171, 85), (0, 0, 0), (0, 0, 255), (0, 0, 0),
    (85, 0, 171), (0, 0, 0), (171, 0, 85), (0, 0, 0)
]


PartyColors_p = [
    (85, 0, 171), (132, 0, 124), (181, 0, 75), (229, 0, 27),
    (232, 23, 0), (184, 71, 0), (171, 119, 0), (171, 171, 0),
    (171, 85, 0), (221, 34, 0), (242, 0, 14), (194, 0, 62),
    (143, 0, 113), (95, 0, 161), (47, 0, 208), (0, 7, 249)
]


HeatColors_p = [
    (0, 0, 0),
    (51, 0, 0), (102, 0, 0), (153, 0, 0), (204, 0, 0), (255, 0, 0),
    (255, 51, 0), (255, 102, 0), (255, 153, 0), (255, 204, 0), (255, 255, 0),
    (255, 255, 51), (255, 255, 102), (255, 255, 153), (255, 255, 204), (255, 255, 255)
]

myRedWhiteBluePalette_p = [
    Red,
    WhiteSmoke,  # 'white' is too bright compared to red and blue
    Blue,
    Black,

    Red,
    WhiteSmoke,
    Blue,
    Black,

    Red,
    Red,
    WhiteSmoke,
    WhiteSmoke,
    Blue,
    Blue,
    Black,
    Black
]

# Black and White Striped Palette
BlackAndWhiteStrip_p = [
    White, Black, Black, Black,
    White, Black, Black, Black,
    White, Black, Black, Black,
    White, Black, Black, Black
]

