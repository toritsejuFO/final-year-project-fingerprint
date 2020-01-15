#!/usr/bin/python3

import sys, serial, requests, json
from time import sleep

from adafruit.interface import AdafruitFingerprint
from adafruit.response import FINGERPRINT_PASSWORD_OK, FINGERPRINT_OK
from enroll import enroll_fingerprint
from store import store_fingerprint
from search import search_fingerprint


def main (): 
    # base_route = 'http://localhost:4000'
    base_route = 'https://api.cerebrohive.ml'
    student_login_route = f'{base_route}/students/signin'
    students_registered = f'{base_route}/students/registered'
    lecturer_login_route = f'{base_route}/lecturers/signin'
    lecturer_details_route = f'{base_route}/lecturers/me'
    lecturer_lectures_route = f'{base_route}/lecturers/lecture/attendance'
    upload_template_route = f'{base_route}/students/me/register/fingerprint'
    TOKEN_KEY = 'x-auth-token'
    timeout = 10

    # attempt to connect to serial port
    try:
        port = '/dev/ttyUSB0' # USB TTL converter port
        baud_rate = '57600'
        serial_port = serial.Serial(port, baud_rate)
    except Exception:
        print(e)
        sys.exit()

    print('Program started...')

    # initialize sensor library with serial port connection
    finger = AdafruitFingerprint(port=serial_port)

    resp = finger.vfy_pwd()
    if resp is not FINGERPRINT_PASSWORD_OK:
        print(f'Verification error. Did not find fingerprint sensor :(')
        sys.exit()
    print('Found Fingerprint Sensor!\n')

    show_options()
    # Handle non-numerical inputs to avoid unwanted end of program
    try:
        option = int(input('Enter Option: '))
    except Exception:
        option = ''
        print('Option must be an integer from the available options')
    while not isinstance(option, int):
        try:
            option = int(input('Enter option: '))
        except Exception:
            print('Option must be an integer from the available options')
    print()
    while True:
        if option == 1:
            reg_no = str(input('Enter your reg number: '))
            password = str(input('Enter your password: '))
            payload = dict(reg_no=reg_no, password=password)
            try:
                r = requests.post(student_login_route, json=payload, timeout=timeout)
                data = r.json()
                print(f'\n{data["message"]}\n')
            except Exception:
                print('\nFailed to establish connection with server\n')
                data['success'] = False
            finally:
                if not data: data['success'] = False
            if data['success']:
                template = enroll_fingerprint(finger=finger)
                if template:
                    try:
                        r = requests.post(upload_template_route, json={'template': template},
                            timeout=timeout, headers={TOKEN_KEY: data[TOKEN_KEY]})
                        data = r.json()
                        print(f'\n{data["message"]}\n')
                    except Exception:
                        print('\nFailed to establish connection with server\n')
        elif option == 2:
            # Login a lecturer
            lecturer_email = str(input('Enter lecturer email: '))
            lecturer_password = str(input('Enter lecturer password: '))
            payload = dict(email=lecturer_email, password=lecturer_password)
            try:
                r = requests.post(lecturer_login_route, json=payload, timeout=timeout)
                data = r.json()
                print(f'\n{data["message"]}\n')
            except Exception:
                print('\nFailed to establish connection with server\n')
                data['success'] = False
            finally:
                if not data: data['success'] = False
            if data['success']:
                # Get lecturer details
                TOKEN = data[TOKEN_KEY]
                try:
                    r = requests.get(lecturer_details_route, timeout=timeout, headers={TOKEN_KEY: TOKEN})
                    data = r.json()
                except Exception:
                    print('\nFailed to establish connection with server\n')
                finally:
                    if not data: data['success'] = False
                if data['success']:
                    # List courses and lecturer selects a course
                    data = data['data']
                    lecturer_department = data['department']
                    lecturer_id = data['id']
                    print(f'\nCourses Assigned to {data["name"]}')
                    for index, assigned_course in enumerate(data['assigned_courses']):
                        print(f'{index + 1}. {assigned_course["course_code"]}({assigned_course["course_unit"]}): {assigned_course["course_title"]}')
                    try:
                        course = int(input('\nEnter index of course to select it: '))
                        selected_course = data['assigned_courses'][course - 1]
                    except Exception:
                        print('\nInvalid option selected\n')
                        continue
                    if selected_course: # Adjust for zero index
                        # Take lecture attendance for lecturer
                        try:
                            formatted_route = f'{lecturer_lectures_route}/{selected_course["course_code"]}'
                            r = requests.get(formatted_route, timeout=timeout, headers={TOKEN_KEY: TOKEN})
                            data = r.json()
                            print(f'\n{data["message"]}\n')
                        except Exception:
                            print('\nFailed to establish connection with server\n')
                        finally:
                            if not data: data['success'] = False
                        if data['success']:
                            # Fetch registered students for selected course in lecturer's department
                            try:
                                print(f'\nFetching student templates registered for {selected_course["course_code"]} from server...')
                                formatted_route = f'{students_registered}/{selected_course["course_code"]}/{lecturer_department}'
                                r = requests.get(formatted_route, timeout=timeout)
                                data = r.json()
                                if r.status_code == 500:
                                    print('\nInvalid course or department submitted\n')
                                else:
                                    print(f'\n{data["message"]}\n')
                            except Exception:
                                print('\nFailed to establish connection with server\n')
                            finally:
                                if not data: data['success'] = False
                            if data['success']:
                                # Store students' fingerprint templates in flash library for searching
                                students = data['data']
                                page_id = data['data'][0]['id'] # first student id
                                page_num = len(students) # total number of students fetched
                                for student in students:
                                    resp = store_fingerprint(finger=finger, template=student['template'], page_id=student['id'])
                                    if resp is FINGERPRINT_OK:
                                        print(f'Student with reg number {student["reg_no"]} Loaded successfully')
                                    else:
                                        print('Issue loading fingerprint templates into module')
                                        break
                                # Start searching flash library
                                search = int(input('\nEnter 1 to search or -1 to quit: '))
                                while True:
                                    if search == 1:
                                        resp = search_fingerprint(finger=finger, page_id=page_id, page_num=page_num)
                                        if resp and resp[0] is FINGERPRINT_OK:
                                            page = resp[1]
                                            student = students[page - 1] # Adjust for zero index
                                            print(f'\nStudent is {student["name"]} with reg number {student["reg_no"]}\n')
                                            try:
                                                name = student['name']
                                                reg_no = student['reg_no']
                                                lecture_route = f'{base_route}/students/{reg_no}/lecture/attendance/{selected_course["course_code"]}/{lecturer_id}'
                                                print('\nUpdating remote server...\n')
                                                r = requests.get(lecture_route, timeout=timeout)
                                                data = r.json()
                                                print(f'\n{data["message"]}\n')
                                            except Exception:
                                                print('\nFailed to establish connection with server\n')
                                        else: print('Student may not have registered for this course')
                                    elif search == -1:
                                        print('\nAre you sure you want to end lecture?')
                                        print('If YES, enter lecturer email')
                                        print('If NO then enter any key to continue')
                                        search_or_end = input('Enter option: ')
                                        if isinstance(search_or_end, str) and search_or_end == lecturer_email:
                                            print('\nThis lecture has ended\n')
                                            break
                                        else:
                                            search = 1
                                            continue
                                    else:
                                        print('Invalid option')
                                    search = int(input('\nEnter 1 to search or -1 to quit: '))
                    else:
                        print('Invalid course selected')
        elif option == 3:
            course = str(input('Enter course: '))
            department = str(input('Enter department: '))
            formatted_route = f'{students_registered}/{course}/{department}'
            try:
                print('\nFetching student templates from server...')
                r = requests.get(formatted_route, timeout=timeout)
                data = r.json()
                if r.status_code == 500:
                    print('\nInvalid course or department submitted\n')
                else:
                    print(f'\n{data["message"]}\n')
            except Exception:
                print('\nFailed to establish connection with server\n')
            finally:
                if not data: data['success'] = False
            if data['success']:
                students = data['data']
                page_id = data['data'][0]['id'] # first student id
                page_num = len(students) # total number of students fetched
                for student in students:
                    resp = store_fingerprint(finger=finger, template=student['template'], page_id=student['id'])
                    if resp is FINGERPRINT_OK:
                        print(f'Student with reg number {student["reg_no"]} Loaded successfully')
                    else:
                        print('Issue loading fingerprint templates into module')
                        break
                search = int(input('\nEnter 1 to search or -1 to quit: '))
                while True:
                    if search == 1:
                        resp = search_fingerprint(finger=finger, page_id=page_id, page_num=page_num)
                        if resp and resp[0] is FINGERPRINT_OK:
                            page = resp[1]
                            student = students[page - 1] # Adjust for zero index
                            print(f'\nStudent is {student["name"]} with reg number {student["reg_no"]}\n')
                            try:
                                name = student['name']
                                reg_no = student['reg_no']
                                exam_route = f'{base_route}/students/{reg_no}/exam/attendance/{course}'
                                print('\nUpdating remote server...\n')
                                r = requests.get(exam_route, timeout=timeout)
                                data = r.json()
                                print(f'\n{data["message"]}\n')
                            except Exception:
                                print('\nFailed to establish connection with server\n')
                        else: print('Student may not have registered for this course')
                    elif search == -1:
                        break
                    else:
                        print('Invalid option')
                    search = int(input('\nEnter 1 to search or -1 to quit: '))
        elif option == -1:
            sys.exit('Program ended')
        else:
            print('Please select a valid option')
            try:
                option = int(input('Enter Option: '))
            except Exception:
                option = ''
                print('Option must be an integer from the available options')
            while not isinstance(option, int):
                try:
                    option = int(input('Enter option: '))
                except Exception:
                    print('Option must be an integer from the available options')
            print()
            continue
        show_options()
        try:
            option = int(input('Enter Option: '))
        except Exception:
            option = ''
            print('Option must be an integer from the available options')
        while not isinstance(option, int):
            try:
                option = int(input('Enter option: '))
            except Exception:
                print('Option must be an integer from the available options')
        print()


def show_options():
    print('\nEnter 1 to register')
    print('Enter 2 for lecture')
    print('Enter 3 for exam')
    print('Enter -1 to quit')


if __name__ == '__main__':
    main()
