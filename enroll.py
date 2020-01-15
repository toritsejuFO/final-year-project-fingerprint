import sys
from time import sleep


from adafruit.exceptions import *
from adafruit.response import *


CHAR_BUFF_1 = 0x01
CHAR_BUFF_2 = 0x02


def enroll_fingerprint(finger):
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

    # Ensure finger has been removed
    print('Remove finger')
    sleep(1)
    resp = -1
    while (resp is not FINGERPRINT_NOFINGER):
        resp = finger.gen_img()

    print('\nPlace that same finger again')
    sys.stdout.flush()

    # read finger the second time
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
    
    resp = finger.img_2tz(buffer=CHAR_BUFF_2)
    sleep(0.1)
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

    print('Remove finger')
    print('\nChecking both prints...\n')
    sys.stdout.flush()

    # Register model
    resp = finger.reg_model()
    sleep(0.1)
    if resp is FINGERPRINT_OK:
        print('Prints matched')
        sys.stdout.flush()
    if resp is FINGERPRINT_PACKETRECEIVER:
        print('Communication error')
        return False
    if resp is FINGERPRINT_ENROLLMISMATCH:
        print('Prints did not match')
        return False

    resp = finger.up_char(buffer=CHAR_BUFF_2)
    sleep(0.1)
    if isinstance(resp, tuple) and len(resp) == 2 and resp[0] is FINGERPRINT_OK:
        print('Template created successfully!')
        print('Enrollment done!\n')
        sys.stdout.flush()
        return resp[1]
    if resp is FINGERPRINT_PACKETRECEIVER:
        print('Communication error')
        return False
    if resp is FINGERPRINT_TEMPLATEUPLOADFAIL:
        print('Template upload error')
        return False
