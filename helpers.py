import platform
import sys
import textwrap
import time

import usb.core
import usb.util


class Pipsta(object):

    USB_BUSY = 66

    PIPSTA_USB_VENDOR_ID = 0x0483
    PIPSTA_USB_PRODUCT_ID = 0xA053

    LINE_CHAR_WIDTH = 32
    CR = b"\x0D"

    FONT_REGULAR = b"\x1b!\x00"
    FONT_UNDERLINE = b"\x1b!\x80"
    FONT_WIDE = b"\x1b!\x20"
    FONT_TALL = b"\x1b!\x10"

    def __init__(self,
                 vendor=PIPSTA_USB_VENDOR_ID,
                 product=PIPSTA_USB_PRODUCT_ID):
        self.vendor = vendor
        self.product = product

    def tprint(self, text, font=FONT_REGULAR, feed=1, wrap=False):
        self.check_platform()
        dev = self.get_device()
        endpoint = self.get_endpoint(dev)
        endpoint.write(font)
        if wrap:
            text = textwrap.fill(text, self.LINE_CHAR_WIDTH)
        endpoint.write(text)
        """
        for x in text:
            endpoint.write(x)    # write all the data to the USB OUT endpoint
            res = dev.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
            while res[0] == self.USB_BUSY:
                time.sleep(0.01)
                res = dev.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
        """
        endpoint.write(b"\n" * feed)
        usb.util.dispose_resources(dev)

    def get_endpoint(self, dev):
        cfg = dev.get_active_configuration()  # Get handle to active interface
        interface_number = cfg[(0, 0)].bInterfaceNumber
        usb.util.claim_interface(dev, interface_number)
        alternate_setting = usb.control.get_interface(dev, interface_number)
        interface = usb.util.find_descriptor(
            cfg,
            bInterfaceNumber=interface_number,
            bAlternateSetting=alternate_setting
            )
        usb_endpoint = usb.util.find_descriptor(
            interface,
            custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
                usb.util.ENDPOINT_OUT
        )
        if usb_endpoint is None:  # check we have a real endpoint handle
            raise IOError("Could not find an endpoint to print to")
        return usb_endpoint

    def get_device(self):
        dev = usb.core.find(
            idVendor=self.vendor,
            idProduct=self.product
        )
        if dev is None:  # if no such device is connected...
            raise IOError("Printer  not found")  # ...report error
        try:
            dev.reset()
            dev.set_configuration()
        except usb.core.USBError as ex:
            raise IOError("Failed to configure the printer", ex)
        return dev

    def check_platform(self):
        if platform.system() != "Linux":
            sys.exit("This script has only been written for Linux")