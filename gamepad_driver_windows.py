# Released by rdb under the Unlicense (unlicense.org)
# Further reading about the WinMM Joystick API:
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd757116(v=vs.85).aspx

"""
Current values: (tested with logitech gamepad)
Left stick:
N = (..., 100, 200, ...)
E = (..., 200, 100, ...)
S = (..., 100, 0, ...)
W = (..., 0, 100, ...)

Right stick:
N = (0, 0, ...)
E = (0, 200, ...)
S = (200, 200, ...)
W = (200, 0, ...)

Right thumb buttons (the letter/shape ones):
N = (..., 2)
S = (..., 0)

Triggers: ...


These values may not make the most sense (eg the right stick N/S directions are swapped). If the
behavior of this file is changed, make sure to also update gamepad_driver_linux.py.
"""

from math import floor, ceil
import time
import ctypes
import winreg as winreg
from ctypes.wintypes import WORD, UINT, DWORD
from ctypes.wintypes import WCHAR as TCHAR
import numpy as np

# Fetch function pointers
joyGetNumDevs = ctypes.windll.winmm.joyGetNumDevs
joyGetPos = ctypes.windll.winmm.joyGetPos
joyGetPosEx = ctypes.windll.winmm.joyGetPosEx
joyGetDevCaps = ctypes.windll.winmm.joyGetDevCapsW

# Define constants
MAXPNAMELEN = 32
MAX_JOYSTICKOEMVXDNAME = 260

JOY_RETURNX = 0x1
JOY_RETURNY = 0x2
JOY_RETURNZ = 0x4
JOY_RETURNR = 0x8
JOY_RETURNU = 0x10
JOY_RETURNV = 0x20
JOY_RETURNPOV = 0x40
JOY_RETURNBUTTONS = 0x80
JOY_RETURNRAWDATA = 0x100
JOY_RETURNPOVCTS = 0x200
JOY_RETURNCENTERED = 0x400
JOY_USEDEADZONE = 0x800
JOY_RETURNALL = JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ | JOY_RETURNR | JOY_RETURNU | JOY_RETURNV | JOY_RETURNPOV | JOY_RETURNBUTTONS

# This is the mapping for my XBox 360 controller.
button_names = ['a', 'b', 'x', 'y', 'tl',
                'tr', 'back', 'start', 'thumbl', 'thumbr']
povbtn_names = ['dpad_up', 'dpad_right', 'dpad_down', 'dpad_left']

# Define some structures from WinMM that we will use in function calls.


class JOYCAPS(ctypes.Structure):
    _fields_ = [
        ('wMid', WORD),
        ('wPid', WORD),
        ('szPname', TCHAR * MAXPNAMELEN),
        ('wXmin', UINT),
        ('wXmax', UINT),
        ('wYmin', UINT),
        ('wYmax', UINT),
        ('wZmin', UINT),
        ('wZmax', UINT),
        ('wNumButtons', UINT),
        ('wPeriodMin', UINT),
        ('wPeriodMax', UINT),
        ('wRmin', UINT),
        ('wRmax', UINT),
        ('wUmin', UINT),
        ('wUmax', UINT),
        ('wVmin', UINT),
        ('wVmax', UINT),
        ('wCaps', UINT),
        ('wMaxAxes', UINT),
        ('wNumAxes', UINT),
        ('wMaxButtons', UINT),
        ('szRegKey', TCHAR * MAXPNAMELEN),
        ('szOEMVxD', TCHAR * MAX_JOYSTICKOEMVXDNAME),
    ]


class JOYINFO(ctypes.Structure):
    _fields_ = [
        ('wXpos', UINT),
        ('wYpos', UINT),
        ('wZpos', UINT),
        ('wButtons', UINT),
    ]


class JOYINFOEX(ctypes.Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('dwFlags', DWORD),
        ('dwXpos', DWORD),
        ('dwYpos', DWORD),
        ('dwZpos', DWORD),
        ('dwRpos', DWORD),
        ('dwUpos', DWORD),
        ('dwVpos', DWORD),
        ('dwButtons', DWORD),
        ('dwButtonNumber', DWORD),
        ('dwPOV', DWORD),
        ('dwReserved1', DWORD),
        ('dwReserved2', DWORD),
    ]


# Get the number of supported devices (usually 16).
num_devs = joyGetNumDevs()
if num_devs == 0:
    print("Joystick driver not loaded.")

# Number of the joystick to open.
joy_id = 0

# Check if the joystick is plugged in.
info = JOYINFO()
p_info = ctypes.pointer(info)
if joyGetPos(0, p_info) != 0:
    print("Joystick %d not plugged in." % (joy_id + 1))

# Get device capabilities.
caps = JOYCAPS()
if joyGetDevCaps(joy_id, ctypes.pointer(caps), ctypes.sizeof(JOYCAPS)) != 0:
    print("Failed to get device capabilities.")

print("Driver name:", caps.szPname)

# Fetch the name from registry.
key = None
if len(caps.szRegKey) > 0:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             "System\\CurrentControlSet\\Control\\MediaResources\\Joystick\\%s\\CurrentJoystickSettings" % (caps.szRegKey))
    except:
        key = None

if key:
    oem_name = winreg.QueryValueEx(key, "Joystick%dOEMName" % (joy_id + 1))
    if oem_name:
        key2 = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "System\\CurrentControlSet\\Control\\MediaProperties\\PrivateProperties\\Joystick\\OEM\\%s" % (oem_name[0]))
        if key2:
            oem_name = winreg.QueryValueEx(key2, "OEMName")
            print("OEM name:", oem_name[0])
        key2.Close()

# Set the initial button states.
button_states = {}
for b in range(caps.wNumButtons):
    name = button_names[b]
    if (1 << b) & info.wButtons:
        button_states[name] = True
    else:
        button_states[name] = False

for name in povbtn_names:
    button_states[name] = False

# Initialise the JOYINFOEX structure.
info = JOYINFOEX()
info.dwSize = ctypes.sizeof(JOYINFOEX)
info.dwFlags = JOY_RETURNBUTTONS | JOY_RETURNCENTERED | JOY_RETURNPOV | JOY_RETURNU | JOY_RETURNV | JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ
p_info = ctypes.pointer(info)


def thresh(a, l_th=0.1, u_th=1):
    if abs(a) < l_th:
        return 0
    elif abs(a) > u_th:
        return -1 if a < 0 else 1
    return a


def get_gamepad_values():
    # Remap the values to float
    x = (info.dwXpos - 32767) / 32768.0
    y = (info.dwYpos - 32767) / 32768.0
    trig = (info.dwZpos - 32767) / 32768.0
    rx = (info.dwRpos - 32767) / 32768.0
    ry = (info.dwUpos - 32767) / 32768.0

    # NB.  Windows drivers give one axis for the trigger, but I want to have
    # two for compatibility with platforms that do support them as separate axes.
    # This means it'll behave strangely when both triggers are pressed, though.
    lt = max(-1.0,  trig * 2 - 1.0)
    rt = max(-1.0, -trig * 2 - 1.0)

    # Figure out which buttons are pressed.
    for b in range(caps.wNumButtons):
        pressed = (0 != (1 << b) & info.dwButtons)
        name = button_names[b]
        button_states[name] = pressed

    # Determine the state of the POV buttons using the provided POV angle.
    if info.dwPOV == 65535:
        povangle1 = None
        povangle2 = None
    else:
        angle = info.dwPOV / 9000.0
        povangle1 = int(floor(angle)) % 4
        povangle2 = int(ceil(angle)) % 4

    for i, btn in enumerate(povbtn_names):
        if i == povangle1 or i == povangle2:
            button_states[btn] = True
        else:
            button_states[btn] = False

    # Display the x, y, trigger values.
    # print ("\r(% .3f % .3f % .3f) (% .3f % .3f % .3f)%s%s" % (x, y, lt, rx, ry, rt, buttons_text, erase),)
    # print info.dwXpos, info.dwYpos, info.dwZpos, info.dwRpos, info.dwUpos, info.dwVpos, info.dwButtons, info.dwButtonNumber, info.dwPOV, info.dwReserved1, info.dwReserved2

    # print(x, y, rx, ry, button_states)

    rx, ry = -ry, -rx  # the axes are flipped for this gamepad
    y = -y

    if abs(x) > abs(y):
        y = 0
    else:
        x = 0

    deposit_bin_angle = 100
    if button_states['y']:
        deposit_bin_angle = 90
    elif button_states['a']:
        deposit_bin_angle = 110

    conveyor = 100 # TODO the code for the conveyor belt is untested. I just copied the implementation from gamepad_driver_linux that I did test.
    if button_states['b']:
        conveyor = 110
    elif button_states['x']:
        conveyor = 90

    args = (
        int(thresh(ry-rx, 0.1) * 100 + 100),
        int(thresh(ry+rx, 0.1) * 100 + 100),
        int(thresh(x, 0.1) * 100 + 100),
        int(thresh(y, 0.1) * 100 + 100),
        int((-(lt + 1) / 2 + (rt + 1) / 2) * 100 + 100),
        deposit_bin_angle,
        conveyor
    )
    return args


if __name__ == "__main__":
    while True:
        if joyGetPosEx(0, p_info) != 0:
            print("Gamepad disconnected")
            break
        print(get_gamepad_values())
        time.sleep(0.1)
