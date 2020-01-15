import sys
from time import sleep


from adafruit.exceptions import *
from adafruit.response import *


CHAR_BUFF_1 = 0x01
CHAR_BUFF_2 = 0x02


def search_fingerprint(finger, page_id, page_num):
    print('\nPlace your finger')
    sys.stdout.flush()

    # read finger the first time
    resp = -1
    while resp is not FINGERPRINT_OK:
        resp = finger.gen_img()
        sleep(0.1)
        if resp is FINGERPRINT_OK:
            print('Image taken')
            sys.stdout.flush() 
        elif resp is FINGERPRINT_NOFINGER:
            print('waiting...')
            sys.stdout.flush()
        elif resp is FINGERPRINT_PACKETRECEIVER:
            print('Communication error')
            return False
        elif resp is FINGERPRINT_IMAGEFAIL:
            print('Imaging Error')
            return False
        else:
            print('Unknown Error')
            return False
    
    resp = finger.img_2tz(buffer=CHAR_BUFF_1)
    if resp is FINGERPRINT_OK:
        print('Image Converted')
        sys.stdout.flush() 
    elif resp is FINGERPRINT_IMAGEMESS:
        print('Image too messy')
        return False
    elif resp is FINGERPRINT_PACKETRECEIVER:
        print('Communication error')
        return False
    elif resp is FINGERPRINT_FEATUREFAIL:
        print('Could not find fingerprint features')
        return False
    elif resp is FINGERPRINT_INVALIDIMAGE:
        print('Could not find fingerprint features')
        return False
    else:
        print('Unknown Error')
        return False

    resp = finger.search(buffer=CHAR_BUFF_1, page_start=page_id, page_num=page_num)
    sleep(0.1)
    if isinstance(resp, tuple) and len(resp) == 3 and resp[0] is FINGERPRINT_OK:
        print('Found a print match!')
        sys.stdout.flush()
        return resp[0], resp[1], resp[2]
    if resp is FINGERPRINT_PACKETRECEIVER:
        print('Communication error')
        return False
    if resp is FINGERPRINT_NOTFOUND:
        print('Did not find a match')
        return False
