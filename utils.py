import time


def flash_led(nb, led):
    for i in range(nb):
        led.toggle()
        time.sleep_ms(1)
        led.toggle()
        time.sleep_ms(199)
    led.off()


def logPrint(log, serialConnect=False):
    if serialConnect:
        print(log)


def safe_call(func, error_code, socketMessage, serialConnect, *args, **kwargs):
    try:
        return func(socketMessage, serialConnect, *args, **kwargs)
    except Exception as e:
        logPrint('safe_call [err=%d] %s: %s' % (error_code, func.__name__, str(e)), serialConnect)
        socketMessage["aquaErrorNum"] = errorNumSet(error_code, socketMessage["aquaErrorNum"], serialConnect)
        return None


def errorNumSet(number, errorVal, serialConnect):
    prev = errorVal
    errorVal = errorVal | (1 << number)
    if prev != errorVal:
        logPrint('errorVal: %s -> %s' % (prev, errorVal), serialConnect)
    return errorVal


def errorNumReset(number, errorVal, serialConnect):
    prev = errorVal
    errorVal = errorVal & ~(1 << number)
    if prev != errorVal:
        logPrint('errorVal: %s -> %s' % (prev, errorVal), serialConnect)
    return errorVal


def interpolate2D(x, colonne_x, colonne_y):
    n = len(colonne_x)
    ascending = colonne_x[-1] > colonne_x[0]
    if ascending:
        if x <= colonne_x[0]:
            return colonne_y[0]
        if x >= colonne_x[-1]:
            return colonne_y[-1]
        for i in range(n - 1):
            if colonne_x[i] <= x <= colonne_x[i + 1]:
                t = (x - colonne_x[i]) / (colonne_x[i + 1] - colonne_x[i])
                return colonne_y[i] + t * (colonne_y[i + 1] - colonne_y[i])
    else:
        if x >= colonne_x[0]:
            return colonne_y[0]
        if x <= colonne_x[-1]:
            return colonne_y[-1]
        for i in range(n - 1):
            if colonne_x[i + 1] <= x <= colonne_x[i]:
                t = (x - colonne_x[i]) / (colonne_x[i + 1] - colonne_x[i])
                return colonne_y[i] + t * (colonne_y[i + 1] - colonne_y[i])
    return colonne_y[-1]


def interpolate3D(x_points, y_points, z_table, x_val, y_val, serialConnect):
    nx = len(x_points)
    index_x = nx - 2
    for i in range(nx - 1):
        if x_points[i] <= x_val <= x_points[i + 1]:
            index_x = i
            break
    ny = len(y_points)
    index_y = ny - 2
    for i in range(ny - 1):
        if y_points[i] <= y_val <= y_points[i + 1]:
            index_y = i
            break
    x0, x1 = x_points[index_x], x_points[index_x + 1]
    y0, y1 = y_points[index_y], y_points[index_y + 1]
    z00 = z_table[index_x][index_y]
    z10 = z_table[index_x + 1][index_y]
    z01 = z_table[index_x][index_y + 1]
    z11 = z_table[index_x + 1][index_y + 1]
    return (z00 * (x1 - x_val) * (y1 - y_val) +
            z10 * (x_val - x0) * (y1 - y_val) +
            z01 * (x1 - x_val) * (y_val - y0) +
            z11 * (x_val - x0) * (y_val - y0)) / ((x1 - x0) * (y1 - y0))
