import threading
import time
import cv2
import numpy as np
import csv
import pyautogui # pyautogui for bug about size of output screen
import pyvjoy # https://github.com/tidzo/pyvjoy

from controlscreen import get_screen, move_screen
import imageprocess as ip
from imageprocess import BOUND, BOUND_VH, CON_HEIGHT, CON_WIDTH, MIDPOINT
from steering import steer_wheel
from telemetry import get_truckinfo
# init of global var
screen = get_screen(256, 192)
cars = None
ending = False

def drive():
    """act like main func
    include init of values
    main drive thread is for lane detection and steering
    sub detect vehicle thread is for vehicle detection
    use 'ending' for escape from loop in subthread

    1. get screen
    1.1 process screen
    1.2 get lanes from processed screen
    1.3 control steering wheel and throttle
    1.4 draw lanes and vehicles

    2.1 process screen
    2.2 detect vehicle
    2.3 save detection data into 'cars'

    original game screen size
    width = 1024
    height = 768
    """
    move = True
    paused = False
    linebuffer = [False, [], []]
    accel_average = []
    brake_average = []
    road_width = 0
    brake_distance = 0
    braking = False

    global screen
    global cars
    global ending

    # for the vehicle detection
    dt = threading.Thread(target=detect_vehicle, args=())
    dt.daemon = True
    dt.start()

    # for performance check
    fps_sum = 0
    count_fps = 0

    j = pyvjoy.VJoyDevice(1)
    j.data.wAxisX = 0x4000
    j.data.wAxisY = 0x1000
    j.update()
    
    loop_count=0
    data_count=0
    while True:
        if not paused:

            speed, accel,brake,steer = get_truckinfo()
            accel=0x4000-(0x4000*accel)+(0x4000*brake)
            steer=0x4000-(0x4000*steer)

            control_fig = np.zeros((CON_HEIGHT, CON_WIDTH, 3), np.uint8)
            start_time = time.time()
            screen = get_screen(256, 192)

            screen_lane = screen
            screen_processed = ip.process_img(screen_lane, BOUND)
            lines = ip.process_line(screen_processed, linebuffer)

        

            if lines and linebuffer[0]:
                linebuffer[1] = lines[0]
                linebuffer[2] = lines[1]

            overlay = ip.draw_roi(screen_lane, BOUND)
            if not isinstance(lines, type(None)):
                # point = x1 of each line
                point_left = lines[0][0][0]
                point_right = lines[1][0][0]
                vanishing = (point_left+point_right)/2
                direction = vanishing - MIDPOINT
                x_axis, y_axis = steer_wheel(direction, speed, braking)
                overlay = ip.draw_lines(overlay, lines, 3)
            else:
                # if there is no line
                # go straight
                vanishing = MIDPOINT
                x_axis = 0x4000
                y_axis = 0x1000

            overlay = ip.indicate_vehicle(overlay, cars, road_width, brake_distance)

            screen_lane = ip.overlap_img(screen_lane, overlay)
            # control_fig = ip.draw_control_fig(control_fig, x_axis, y_axis, accel_average, brake_average)

            j.data.wAxisX = x_axis
            j.data.wAxisY = y_axis
            j.update()
            if(lines):
                if len(lines)==2:
                    if loop_count%5000==0:
                        data_count=data_count+1
                        Fname='dataSET'+str(data_count)+'.csv'
                    loop_count=loop_count+1
                    fields=[loop_count,lines[0][0][0],lines[0][0][2],lines[1][0][0],lines[1][0][2],speed,steer,accel]
                    with open(Fname, 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(fields)


            fps = int(1/(time.time()-start_time))
            fps_sum += fps
            count_fps += 1
            if count_fps == 60:
                fps_ave = int(fps_sum/60)
                count_fps = 0
                fps_sum = 0
                print('[mainthread]average {}FPS'.format(fps_ave), '/60frm')
            # print('{}FPS'.format(fps))
            cv2.line(screen_lane, (0, int(brake_distance)), (256, int(brake_distance)), [0, 255, 0], 1)
            screen_lane = cv2.resize(screen_lane, (512, 384))
            cv2.imshow('OUTPUT', cv2.cvtColor(screen_lane, cv2.COLOR_BGR2RGB))
            cv2.moveWindow('OUTPUT', 1024, 0)
##            cv2.imshow('CONTROL', cv2.cvtColor(control_fig, cv2.COLOR_BGR2RGB))
            cv2.moveWindow('CONTROL', 1024, 384)
        key_com = cv2.waitKey(10) & 0xff
        # esc
        if key_com == 27:
            j.data.wAxisX = 0x4000
            j.data.wAxisY = 0x4000
            j.update()
            # finish subthread
            ending = True
            cv2.destroyAllWindows()
            break
        # space
        elif key_com == 32:
            if paused:
                paused = False
            else:
                paused = True
        elif key_com == ord('r'):
            j.data.wAxisX = 0x4000
            j.data.wAxisY = 0x4000
            j.update()
        if move:
            move_screen()
            move = False

def detect_vehicle():
    """detect vehicles and save data into global var
    use about 60% of image from bottom
    the other 40% is not useful for vehicle detection
    detectMultiScale(source, scaleFactor, minNeighbors, flags, minSize)
    scaleFactor: before detection, scales the image
    it should be larger than '1', get bigger, lower chance of detection
    ex) '1.1' means decreas 10%
    """
    cascade = cv2.CascadeClassifier('cars.xml')
    global screen
    global cars
    global ending
    fps_sum = 0
    count_fps = 0
    fps_ave = 0
    # this loop can be break by pressing 'esc' in drive()
    while not ending:
        start_time = time.time()

        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        screen_blurred = cv2.GaussianBlur(screen_gray, (3, 3), 0)
        screen_roi = ip.set_roi(screen_blurred, BOUND_VH)
        cars = cascade.detectMultiScale(screen_roi, scaleFactor=1.15, minNeighbors=5,\
         flags=cv2.CASCADE_SCALE_IMAGE, minSize=(10, 10))

        fps = int(1/(time.time()-start_time))
        fps_sum += fps
        count_fps += 1
        if count_fps == 60:
            fps_ave = int(fps_sum/60)
            count_fps = 0
            fps_sum = 0
            print('[subthread]average {}FPS'.format(fps_ave), '/60frm')

drive()
