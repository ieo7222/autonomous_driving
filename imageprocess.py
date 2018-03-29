from statistics import mean
import cv2
import numpy as np

MIDPOINT = 128 # 360/2
OFFSET = 4

CON_WIDTH = 512
CON_HEIGHT = 256

RESIZE_WIDTH = 256
RESIZE_HEIGHT = 192
ROI_WIDTH = RESIZE_WIDTH
ROI_HEIGHT = RESIZE_HEIGHT
ROI_UPPER = RESIZE_HEIGHT*0.55
ROI_LOWER = RESIZE_HEIGHT*0.7
ROI_TOP_LEFT = RESIZE_WIDTH*0.3
ROI_TOP_RIGHT = RESIZE_WIDTH*0.7

BOUND = np.array([[OFFSET, ROI_HEIGHT-OFFSET], [OFFSET, ROI_LOWER],\
    [ROI_TOP_LEFT, ROI_UPPER], [ROI_TOP_RIGHT, ROI_UPPER],\
    [ROI_WIDTH-OFFSET, ROI_LOWER], [ROI_WIDTH-OFFSET, ROI_HEIGHT-OFFSET]], np.int32)

BOUND_VH = np.array([[OFFSET, RESIZE_HEIGHT], [OFFSET, RESIZE_HEIGHT*0.4],\
         [RESIZE_WIDTH-OFFSET, RESIZE_HEIGHT*0.4], [RESIZE_WIDTH-OFFSET, RESIZE_HEIGHT]], np.int32)

BOUND_LANE = np.array([[OFFSET, RESIZE_HEIGHT*0.6], [OFFSET, RESIZE_HEIGHT*0.4],\
     [RESIZE_WIDTH-OFFSET, RESIZE_HEIGHT*0.4], [RESIZE_WIDTH-OFFSET, RESIZE_HEIGHT*0.6]], np.int32)

def process_img(img, boundary):
    """return processed image
    take specific area from screen to inhance lane detection
    overlap this specific area on screen_gray
    process image for line detection
    """
    mask = make_mask_hls(img)
    mask_roi = set_roi(mask, BOUND_LANE)
    kernel = np.ones((3, 3), np.uint8)
    mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, kernel)
    # mask_roi = cv2.dilate(mask_roi, kernel, iterations=1)
    cv2.imshow('mask', mask_roi)
    cv2.moveWindow('mask', 1536, 192)
    img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_processed = cv2.addWeighted(img_processed, 1.0, mask_roi, 1.1, 0.0)
    img_processed = cv2.GaussianBlur(img_processed, (3, 3), 0)
    img_processed = cv2.Canny(img_processed, threshold1=130, threshold2=150)
    img_processed = set_roi(img_processed, boundary)
    cv2.imshow('processed', img_processed)
    cv2.moveWindow('processed', 1536, 0)
    return img_processed

def make_mask_rgb(img):
    lower = np.uint8([90, 120, 120])
    upper = np.uint8([255, 255, 255])
    mask = cv2.inRange(img, lower, upper)
    # cv2.imshow('rgb', mask)
    return mask

def make_mask_hls(img):
    img_hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    lower = np.uint8([0, 90, 30])
    upper = np.uint8([180, 255, 255])
    mask = cv2.inRange(img_hls, lower, upper)
    # cv2.imshow('hls', mask)
    return mask

def make_mask_hsv(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.uint8([0, 40, 115])
    upper = np.uint8([180, 255, 255])
    mask = cv2.inRange(img_hsv, lower, upper)
    # cv2.imshow('hsv', mask)
    return mask

def set_roi(img, boundary):
    """set region of interest to calculate less
    """
    mask = np.zeros_like(img)
    cv2.fillConvexPoly(mask, boundary, 255)
    img_cut = cv2.bitwise_and(img, mask)
    return img_cut

def draw_roi(img, boundary):
    """draw roi boundary
    """
    img_zero = np.zeros_like(img)
    # cv2.polylines(img_zero, [boundary], True, (255, 255, 255),0)
    return img_zero

def process_line(img, linebuffer):
    """return left and right lane
    line = [[[aa,bb,cc,dd]], [[ee,ff,gg,hh]]]
    Args:
        img: present screen
        linebuffer: array for line buffering
    Returns:
        [left_lane, right_lane] or None
    """
    lines = cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=13,\
     minLineLength=13, maxLineGap=270)
    if not isinstance(lines, type(None)):
        valid = remove_invalid(lines)
        if valid.any():
            stretched = stretch_lines(valid)
            groups = make_group(stretched)
            average_lines = get_average_line(groups)
            if average_lines:
                lanes = pick_lane(average_lines, linebuffer)
                return lanes
    else:
        return None

def remove_invalid(lines):
    """return not horizontal lines(valid lines)
    remove horizontal lines not proper for lane
    """
    valid = []
    for line in lines:
        if 90 < get_angle(line) < 160 and line[0][0] != line[0][2]:
            valid.append(line)
    valid = np.array(valid)
    return valid

def make_group(valid):
    """grouping lines that have nearly same angle
    check similar lines with fuction 'check_prox(line1, line2)'
    """
    groups = []
    selection = list(valid)
    for line1 in selection:
        group = []
        group.append(line1)
        remove_line(selection, line1)
        for line2 in selection:
            if check_prox(line1, line2):
                group.append(line2)
                remove_line(selection, line2)
        groups.append(np.array(group))
    groups = np.array(groups)
    return groups

def remove_line(lines, line):
    """remove line from lines array
    """
    idx = 0
    size = len(lines)
    while idx != size and not np.array_equal(lines[idx], line):
        idx += 1
    if idx != size:
        lines.pop(idx)
    else:
        raise ValueError('not in list')

def stretch_lines(lines):
    """stretch short lines to make comparison easier
    get slope and intercept from two coordinates
    and change short line into long line
    Args:
        lines
    Returns:
        long_lines: stretched lines
    """
    long_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2-y1)/(x2-x1)
        intercept = y1-slope*x1
        new_x1 = (ROI_UPPER-intercept)/slope
        new_x2 = (RESIZE_HEIGHT-intercept)/slope
        long_line = [[int(new_x1), int(y1), int(new_x2), int(y2)]]
        long_lines.append(long_line)
    return long_lines

def check_prox(line1, line2):
    """check proximity of two lines
    with x1 and x2
    if x1 and x2 is close enough, return True
    """
    line1_x1, line1_y1, line1_x2, line1_y2 = line1[0]
    line2_x1, line2_y1, line2_x2, line2_y2 = line2[0]
    if abs(line1_x1-line2_x1) < 13 and abs(line1_x2-line2_x2) < 13:
        return True
    else:
        return False

def get_angle(line):
    """get angle in degree from line coordinates
    return angle in absolute,
    because the result of arctan2 is negative in this program
    Args:
        line
    Returns:
        angle: absolute value
    """
    x1, y1, x2, y2 = line[0]
    angle = (np.arctan2(y1-y2, x1-x2)*180) / np.pi
    return abs(angle)

def get_average_line(groups):
    """return average line of each group
    get average line of each group
    gather x1 and x2 of one group
    take mean value of x1s and x2s
    Args:
        groups: groups of smiliar lines
        [[line1.1
          line1.2
          line1.3]
         [line2.1
          line2.2
          line2.3]]
    Returns:
        average_lines:
        [line1
         line2]
    """
    average_lines = []
    for group in groups:
        average_line = []
        x1s = group[:, :, 0].ravel()
        x2s = group[:, :, 2].ravel()
        x1 = mean(x1s)
        x2 = mean(x2s)
        if not ROI_TOP_LEFT < x1 < ROI_TOP_RIGHT:
            continue
        average_line = [[int(x1), int(ROI_UPPER), int(x2), int(RESIZE_HEIGHT)]]
        average_lines.append(average_line)
    return average_lines

def pick_lane(average_lines, linebuffer):
    """return left lane and right lane
    sort lines in order of x2
    and pick line that has largest x2 as left lane
    line that has smallest x2 as right lane

    in case of lane departure,
    (when it detects only one side lane)
    if linesbuffer is available,
    liensbuffer can be used for once
    Args:
        average_lines:
        [line1
         line2
         line3]
        linebuffer: [buffer_avail, for left lane, for right lane]
    Retruns:
        [left_lane, right_lane]:
        [ [[011,022,033,044]], [[055,066,088]] ]
    """
    left_lines = []
    right_lines = []
    buf_avail, lbuffer, rbuffer = linebuffer
    for line in average_lines:
        entry = []
        if get_angle(line) < 90:
            entry.append(get_angle(line))
            entry.append(line)
            left_lines.append(entry)
        elif get_angle(line) > 90:
            entry.append(get_angle(line))
            entry.append(line)
            right_lines.append(entry)
        else:
            print('vertical line')
            return None
    # sort each groups in order of x2
    # to pick inner line(closer to center)
    if left_lines:
        left_lines = sorted(left_lines, key=lambda x: (x[1][0][2], x[1][0][0]), reverse=True)
        left_lane = left_lines[0][1]
    if right_lines:
        right_lines = sorted(right_lines, key=lambda x: (x[1][0][2], x[1][0][0]), reverse=False)
        right_lane = right_lines[0][1]
    # if there are both lanes, save them
    if left_lines and right_lines:
        linebuffer[0] = True
    # for lane departure
    # if left or right exists
    # use buffer first,
    # but if buffer is empty
    # make compensation line to return to the center of lanes
    if not left_lines:
        if lbuffer and buf_avail:
            left_lane = lbuffer
            linebuffer[0] = False
        else:
            left_lane = [[0, 0, 0, 0]]
        compensation = MIDPOINT-(ROI_TOP_RIGHT-right_lane[0][0])
        newpoint = int((compensation+MIDPOINT)/2)
        left_lane[0][0] = newpoint
    if not right_lines:
        if rbuffer and buf_avail:
            right_lane = rbuffer
            linebuffer[0] = False
        else:
            right_lane = [[0, 0, RESIZE_WIDTH, 0]]
        compensation = MIDPOINT+(left_lane[0][0]-ROI_TOP_LEFT)
        newpoint = int((compensation+MIDPOINT)/2)
        right_lane[0][0] = newpoint
    if check_violation(left_lane, right_lane):
        return None
    return [left_lane, right_lane]

def draw_lines(img, lines, thickness=1):
    """draw lanes and lane area
    if one of lines is compensation line,
    do not draw area
    """
    for line in lines:
        coords = line[0]
        cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [0, 170, 0], thickness)

    left_x1, left_y1, left_x2, left_y2 = lines[0][0]
    right_x1, right_y1, right_x2, right_y2 = lines[1][0]
    # check whether compensation line
    if left_y2 and right_y2:
        lane_area = np.array([[left_x2, left_y2], [left_x1, left_y1],\
         [right_x1, right_y1], [right_x2, right_y2]], np.int32)
        cv2.fillConvexPoly(img, lane_area, (0, 170, 0))
    return img

def check_violation(left, right):
    """check line violation
    if two lines across in roi area,
    they are not valid
    """
    if left[0][0] > right[0][0]:
        return True
    else:
        return False

def draw_control_fig(img, x_axis, y_axis, accel_average, brake_average):
    """draw information about control
    including steering degree, acceleration and braking in percentage
    """
    RADIUS = int(CON_HEIGHT*0.25)
    BAR_SIZE = int(CON_HEIGHT/1.8) - int(CON_HEIGHT/10)
    UPPER = 25
    LOWER = 50
    SIZE = 16
    T_SIZE = 12
    ST_BAR_SIZE = 30
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    ac_average = 0x4000
    br_average = 0x4000

    cv2.circle(img, (int(CON_WIDTH/4), int(CON_HEIGHT/3)), int(RADIUS), (255, 255, 255), 1)
    cv2.rectangle(img, (int(CON_WIDTH*0.6), int(CON_HEIGHT/10)), (int(CON_WIDTH*0.7), int(CON_HEIGHT/1.8)), (255, 255, 255), 1)
    cv2.rectangle(img, (int(CON_WIDTH*0.8), int(CON_HEIGHT/10)), (int(CON_WIDTH*0.9), int(CON_HEIGHT/1.8)), (255, 255, 255), 1)
    cv2.putText(img, 'steering', (int(CON_WIDTH/4)-65, int(CON_HEIGHT*0.9)), FONT, 1.1, (255, 255, 255), 3)
    cv2.putText(img, 'accel', (int(CON_WIDTH*0.65-45), int(CON_HEIGHT*0.9)), FONT, 1.1, (255, 255, 255), 3)
    cv2.putText(img, 'brake', (int(CON_WIDTH*0.85-33), int(CON_HEIGHT*0.9)), FONT, 1.1, (255, 255, 255), 3)

    if x_axis < 0x4000:
        steer_per = (0x4000-x_axis)/0x4000
        steer_degree = int(steer_per*180)
        steer_per = str(int(steer_per*100))+'%'
        cv2.ellipse(img, (int(CON_WIDTH/4), int(CON_HEIGHT/3)), (RADIUS, RADIUS), 0, (-90), (-90)-steer_degree, (255, 255, 255), -1)
        cv2.putText(img, steer_per, (int(CON_WIDTH/4-27), int(CON_HEIGHT*0.75)), FONT, 1, (255, 255, 255), 2)
    elif x_axis > 0x4000:
        steer_per = (x_axis-0x4000)/0x4000
        steer_degree = int(steer_per*180)
        steer_per = str(int(steer_per*100))+'%'
        cv2.ellipse(img, (int(CON_WIDTH/4), int(CON_HEIGHT/3)), ((RADIUS, RADIUS)), 0, (-90), (-90)+steer_degree, (255, 255, 255), -1)
        cv2.putText(img, steer_per, (int(CON_WIDTH/4-27), int(CON_HEIGHT*0.75)), FONT, 1, (255, 255, 255), 2)
    else:
        cv2.putText(img, '0%', (int(int(CON_WIDTH/4-27)), int(CON_HEIGHT*0.75)), FONT, 1, (255, 255, 255), 2)

    if y_axis < 0x4000:
        accel_average.append(y_axis)
        brake_average.append(0x4000)
    elif y_axis > 0x4000:
        brake_average.append(y_axis)
        accel_average.append(0x4000)
    else:
        accel_average.append(0x4000)
        brake_average.append(0x4000)

    accel_average2 = np.array(accel_average)
    ac_average = mean(accel_average2)
    if len(accel_average) > 30:
        del accel_average[0]

    brake_average2 = np.array(brake_average)
    br_average = mean(brake_average2)
    if len(brake_average) > 6:
        del brake_average[0]

    accel_per = (0x4000-ac_average)/0x4000
    accel_degree = int(accel_per*BAR_SIZE)
    accel_per = str(int(accel_per*100))+'%'

    brake_per = (br_average-0x4000)/0x4000
    brake_degree = int(brake_per*BAR_SIZE)
    temp = brake_per*100
    if temp < 0:
        temp = 0
    brake_per = str(int(temp))+'%'

    cv2.rectangle(img, (int(CON_WIDTH*0.6), int(CON_HEIGHT/1.8)), (int(CON_WIDTH*0.7), int(CON_HEIGHT/1.8)-accel_degree), (255, 255, 255), -1)
    cv2.putText(img, accel_per, (int(CON_WIDTH*0.65-45), int(CON_HEIGHT*0.75)), FONT, 1, (255, 255, 255), 2)
    cv2.rectangle(img, (int(CON_WIDTH*0.8), int(CON_HEIGHT/1.8)), (int(CON_WIDTH*0.9), int(CON_HEIGHT/1.8)-brake_degree), (255, 255, 255), -1)
    cv2.putText(img, brake_per, (int(CON_WIDTH*0.85-13), int(CON_HEIGHT*0.75)), FONT, 1, (255, 255, 255), 2)
    return img, accel_average, brake_average

def overlap_img(img, overlay):
    """return fusion of img and overlay
    img * alpha + overlay * betha + gamma
    in this case, gamma is not used
    """
    return cv2.addWeighted(img, 1.0, overlay, 0.3, 0.0)

def indicate_vehicle(overlay, cars, road_width, brake_distance):
    """draw vehicle
    in case that car is away from brake distance(safe distance),
    display vehicle with green rectangle
    in case that car is in brake distance,
    display vehicle with red rectangle
    """
    if not isinstance(cars, type(None)):
        for x, y, w, h in cars:
            if y+h > brake_distance and x > (RESIZE_WIDTH/2)-(road_width/2) and x+w < (RESIZE_WIDTH/2)+(road_width/2):
                cv2.rectangle(overlay, (x, y), (x+w, y+h), (255, 0, 0), 3)
            else:
                cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 0, 255), 2)
    return overlay
