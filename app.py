import RPi.GPIO as GPIO
from time import sleep
from approxeng.input import CentredAxis, TriggerAxis, Button, Controller, BinaryAxis
from approxeng.input.selectbinder import ControllerResource
from approxeng.input.controllers import ControllerRequirement, print_devices


GPIO.setmode(GPIO.BOARD)

Motor1A = 16
Motor1B = 18
Motor1E = 22

Motor2A = 19
Motor2B = 21
Motor2E = 23

GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1E, GPIO.OUT)

GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(Motor2E, GPIO.OUT)


class WirelessXBoxOnePad(Controller):
    """
    Wireless XBox One controller, tested with the older controller that do not use bluetooth and are supplied with the
    XBox One 2014 through USB wire connection.
    """

    def __init__(self, dead_zone=0.1, hot_zone=0.05):
        """
        Create a new xbox one controller instance
        :param float dead_zone:
            Used to set the dead zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        :param float hot_zone:
            Used to set the hot zone for each :class:`approxeng.input.CentredAxis` and
            :class:`approxeng.input.TriggerAxis` in the controller.
        """
        super(WirelessXBoxOnePad, self).__init__(
            controls=[
                Button("BTN_NORTH", 307, sname='square'),
                Button("BTN_WEST", 308, sname='triangle'),
                Button("BTN_B", 305, sname='circle'),
                Button("BTN_A", 304, sname='cross'),
                Button("BTN_THUMBR", 318, sname='rs'),
                Button("BTN_THUMBL", 317, sname='ls'),
                Button("BTN_SELECT", 314, sname='select'),
                Button("BTN_START", 315, sname='start'),
                Button("BTN_MODE", 316, sname='home'),
                Button("BTN_TL", 310, sname='l1'),
                Button("BTN_TR", 311, sname='r1'),
                CentredAxis("ABS_X", -32768, 32767, 0, sname='lx'),
                CentredAxis("ABS_Y", -32768, 32767, 1, invert=True, sname='ly'),
                CentredAxis("ABS_RX", -32768, 32767, 3, sname='rx'),
                CentredAxis("ABS_RY", -32768, 32767, 4, invert=True, sname='ry'),
                TriggerAxis("ABS_Z", 0, 1023, 2, sname='lt', button_sname='l2', button_trigger_value=0.2),
                TriggerAxis("ABS_RZ", 0, 1023, 5, sname='rt', button_sname='r2', button_trigger_value=0.2),
                BinaryAxis("ABS_HAT0X", 16, b1name='dleft', b2name='dright'),
                BinaryAxis("ABS_HAT0Y", 17, b1name='dup', b2name='ddown')
            ],
            dead_zone=dead_zone,
            hot_zone=hot_zone)

    @staticmethod
    def registration_ids():
        """
        :return: list of (vendor_id, product_id) for this controller
        """
        return [(0x45e, 0x2d1)]

    def __repr__(self):
        return 'Microsoft X-Box One pad'


print('DEBUG: list controllers found')
print(print_devices())

# Get a joystick
with ControllerResource(ControllerRequirement(require_class=WirelessXBoxOnePad)) as joystick:
    # Loop until we're disconnected
    try:
        while joystick.connected:
            # This is an instance of approxeng.input.ButtonPresses
            left_y = joystick['ly']
            if left_y != 0:
                print('left x is %s' % left_y)
            if left_y == 1:
                GPIO.output(Motor1A, GPIO.HIGH)
                GPIO.output(Motor1B, GPIO.LOW)
                GPIO.output(Motor1E, GPIO.HIGH)

                GPIO.output(Motor2A, GPIO.HIGH)
                GPIO.output(Motor2B, GPIO.LOW)
                GPIO.output(Motor2E, GPIO.HIGH)
            elif left_y == -1:
                GPIO.output(Motor1A, GPIO.LOW)
                GPIO.output(Motor1B, GPIO.HIGH)
                GPIO.output(Motor1E, GPIO.HIGH)

                GPIO.output(Motor2A, GPIO.LOW)
                GPIO.output(Motor2B, GPIO.HIGH)
                GPIO.output(Motor2E, GPIO.HIGH)
            else:
                GPIO.output(Motor1E, GPIO.LOW)
                GPIO.output(Motor2E, GPIO.LOW)
            presses = joystick.check_presses()
            if presses['square']:
                print('SQUARE pressed since last check')
            # We can also use attributes directly, and get at the presses object from the controller:
            if joystick.presses.circle:
                print('CIRCLE pressed since last check')
            # Or we can use the 'x in y' syntax:
            if 'triangle' in presses:
                print('TRIANGLE pressed since last check')

            # If we had any presses, print the list of pressed buttons by standard name
            if joystick.has_presses:
                print(joystick.presses)
    except KeyboardInterrupt:
        GPIO.output(Motor1E, GPIO.LOW)
        GPIO.output(Motor2E, GPIO.LOW)
    finally:
        GPIO.cleanup()
