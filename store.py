import sys
from time import sleep


from adafruit.exceptions import *
from adafruit.response import *


CHAR_BUFF_1 = 0x01
CHAR_BUFF_2 = 0x02


def store_fingerprint(finger, template, page_id):
    resp = finger.down_char(buffer=CHAR_BUFF_1, template=template)
    sleep(0.1)
    if resp is FINGERPRINT_OK:
        print('Template downloaded successfully!')
        sys.stdout.flush()
    if resp is FINGERPRINT_PACKETRECEIVER:
        print('Communication error')
        return False
    if resp is FINGERPRINT_TEMPLATEDOWNLOADFAIL:
        print('Template download error')
        return False

    resp = finger.store(buffer=CHAR_BUFF_1, page=page_id)
    sleep(0.1)
    if resp is FINGERPRINT_OK:
        print('Template stored successfully!')
        sys.stdout.flush()
        return resp
    if resp is FINGERPRINT_PACKETRECEIVER:
        print('Communication error')
        return False
    if resp is FINGERPRINT_BADLOCATION:
        print('Could not store in that location')
        return False
    if resp is FINGERPRINT_FLASHER:
        print('Error writing to flash')
        return False
