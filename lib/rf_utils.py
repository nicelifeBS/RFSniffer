"""
Utility functions to decode 433Mhz signals use by RF power sockets
"""


def get_code(
    times, 
    values, 
    long_delay=0.0008, 
    short_delay=0.0003,
    extended_delay=0.010):
    """Function to get code values from an RF signal which has long peaks and
    lows as well as short peaks and lows. A threshold value set from 
    `long_delay` and `short_delay` is used to define short or long signal.
    Example code: 01230101230123232323010101.

    Args:
        times (list of float): Time values of captured codes
        values (list of int): Code values of capture. Indices matching the time
            list.
        long_delay (float): Time in seconds of long delay
        short_delay (float): Time in seconds of short delay
        extended_delay (float): Time in seconds which marks the end/start of a
            new code block. This is used to start and stop the search for code
            values

    Returns:
        str: Found code string
    """
    threshold = long_delay - short_delay
    code = ''
    last_time = None
    last_value = None
    check_point = None
    code_times = []
    for i, v in enumerate(values):
        if not (1.0 < times[i] < 1.5):
            continue
        if last_value is None:
            last_value = v
            last_time = times[i]
            continue
        if v != last_value:
            t = times[i] - last_time
            code_times.append(t)
            # check if we found our start or end point
            if t >= extended_delay:
                if check_point == 'start':
                    check_point = 'stop'
                if check_point is None:
                    check_point = 'start'
            # if we are at the start we can now collect the codes
            if check_point == 'start':
                # long delay but not extended
                if extended_delay > t > threshold:
                    if last_value == 1:
                        code = code + '0'
                    else:
                        code = code + '3'
                # anything shorter than our threshold is a short delay
                if t < threshold:
                    if last_value == 0:
                        code = code + '1'
                    else:
                        code = code + '2'
            last_time = times[i]
        last_value = v

        # End of code reached 
        if check_point == 'stop':
            break
    
    min_time = min(code_times)
    max_time = max(code_times)

    p_extralong = [x for x in code_times if isclose(x, max_time, .1)]
    p_short = [x for x in code_times if isclose(x, min_time, .9)]
    p_long = set(code_times).symmetric_difference(set(p_extralong + p_short))

    print('extra long delay: ', average(p_extralong))
    print('short delay     : ', average(p_short))
    print('long delay      : ', average(p_long))
    
    return code


def average(values):
    """Return average of given values
    
    Args:
        values (list): List of float values
    
    Returns:
        float: Averaged float values
    """
    if not len(values):
        return None
    return sum(values) / len(values)


def isclose(value, baseline, margin=0.1):
    """Return if given value falls into margin
    
    Args:
        val (float): Value to evaluate
        margin (float): +- margin

    Returns:
        bool
    """
    percentile = baseline * margin
    result = baseline - percentile <= value <= baseline + percentile
    return baseline - percentile <= value <= baseline + percentile


if __name__ == '__main__':
    # adhoc testing
    
    import pickle
    with open('../tests/data/sniffer.dump', 'r') as f:
        data = pickle.load(f)
    
    baseline = '0123010123012323232301010123230123232323010101010123230101012301232'
    times, values = data
    # get extended_delay by filtering outliers
    # find_delays(times, values)
    # print max_times
    code = get_code(times, values)
    print('code:     ', code, len(code))
    # print 'baseline: ', baseline, len(baseline)
    # assert(code == baseline)

    # plotting
    # import matplotlib.pyplot as pyplot
    # pyplot.plot(times, values)
    # pyplot.axis([0, 5, -1, 2])
    # pyplot.show()