def steer_wheel(direction, speed, braking):
    """get value for vjoy

    'x axis'
    0x0000(left)<-0x4000(center)->0x8000(right)

    'y axis'
    accel
    0x0000(high)<->0x4000(low)
    brake
    0x4000(low)<->0x8000(high)

    x axis and y axis can be limited for stabilization
    Args:
        direction: how far from midpoint
        accel_override: flag for ocassion that stopped for a long time
        accel: optional value for accel_override
    Returns:
        x_axis
        y_axiss
    """
    try:
        if steer_wheel.pre_direction*direction > 0:
            steer_wheel.count = steer_wheel.count+1
        else:
            steer_wheel.count = 0
    except:
        pass

    speed_factor = speed/150
    unit = direction/103*4
    x_axis = (1+unit*0.7)*0x4000

    if steer_wheel.count > 40:
        y_axis = 0x5700
        x_axis = (1+unit*42/speed)*0x4000
        if steer_wheel.count > 55:
            steer_wheel.count = 0
        elif speed < 20:
            y_axis = 0x4000

    # speed limitation
    Max_speed = 65
    if speed > Max_speed:
        y_axis = 0x4000
    else:
        y_axis = abs(unit*speed_factor)*0x8000

    # control boundary
    if x_axis > 0x8000:
        x_axis = 0x8000
    elif x_axis < 0x0000:
        x_axis = 0x0000
    if y_axis > 0x8000:
        y_axis = 0x8000
    elif y_axis < 0x0000:
        y_axis = 0x0000

    # accel limit
    if y_axis < 0x4000:
        y_axis = y_axis*1.05
    else:
        y_axis = y_axis*0.95

    x_axis = int(x_axis)
    y_axis = int(y_axis)

    if braking:
        x_axis = 0x4000
        y_axis = 0x8000
        print("braking")

    steer_wheel.pre_direction = direction
    return x_axis, y_axis

# static var
steer_wheel.count=0
steer_wheel.pre_direction=1
