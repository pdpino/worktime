"""Provides time functions."""
from datetime import datetime

## Time
def date(t):
    """ Returns the date [year, month, day] from the time t"""
    return t.strftime('%Y-%m-%d').split("-")

def hour(t):
    """Return the time Hour:Minutes from t """
    return t.strftime('%H:%M')

def seconds(t):
    """Return the seconds between the 01/01/2017 and the time t"""
    return (t - datetime(2017,1,1)).total_seconds()

def sec2hr(t):
    """Transform the seconds in H:M
    Adapted from: http://stackoverflow.com/a/33504562"""
    m, s = divmod(t, 60) # obtener minutos, segundos
    h, m = divmod(m, 60) # obtener horas, minutos
    d, h = divmod(h, 24) # obtener dias, horas

    # patterns:
    patt_sec = "{:.1f}s"
    patt_min = "{:.0f}m "
    patt_hr = "{:.0f}h "
    patt_d = "{:.0f} days, "

    if d == 0:
        if h == 0:
            if m == 0:
                return patt_sec.format(s)
            else:
                pattern = patt_min + patt_sec
                return pattern.format(m, s)
        else:
            pattern = patt_hr + patt_min + patt_sec
            return pattern.format(h, m, s)
    else:
        pattern = patt_d + patt_hr + patt_min + patt_sec
        return pattern.format(d, h, m, s)
