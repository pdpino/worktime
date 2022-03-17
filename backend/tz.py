import os
import time

def get_tz_offset():
    """Return timezone offset in seconds.

    Taken from: https://stackoverflow.com/a/10854983/9951939
    """
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    return offset

def get_tz_name():
    """
    Taken from: https://stackoverflow.com/a/11715353/9951939
    """
    fpath = '/etc/timezone'
    if os.path.exists(fpath):
        with open(fpath) as f:
            tzname = str(f.read().strip())
    else:
        tzname = ''
    return tzname
