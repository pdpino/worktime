"""Basic functions to provide"""

import sys
from datetime import datetime, timedelta
import pickle

## Error handle
def perror(text, exit_code=1, force_continue=False, exception=None, **kwargs):
    """Prints error info to stderr and exits"""
    if force_continue:
        level = "WARNING"
    else:
        level = "ERROR"

    msje = "\t{}: {}".format(level, text)

    if not exception is None:
        msje += "\n\t{}".format(exception)

    print(msje, file=sys.stderr, **kwargs)
    if not force_continue:
        sys.exit(exit_code)

def usage_error(text, prefix=False):
    """Wrapper to print an usage error and exit"""

    msje = "usage: " if prefix else ""
    print("{}{}".format(msje, text), file=sys.stderr)
    sys.exit(1) # REVIEW: use error codes

## Files
def dump(obj, fname):
    """Dump an object using pickle"""
    f = open(fname, "wb")
    pickle.dump(obj, f)
    f.close()

def load(fname):
    """Load an object using pickle"""
    f = open(fname, "rb")
    d = pickle.load(f)
    f.close()
    return d

## Input
def input_any(default, message):
    """Prompt the user to input a string"""
    input_exit_option = "exit;"

    w = input("\t{} ({}): ".format(message, default))
    w.strip()
    if w == "":
        w = str(default)
    elif w == input_exit_option: #para poder salir desde cualquier parte
        sys.exit(1)

    print("")
    return w

def input_y_n(default="y", question="Desea ..."):
    return input_any(default, question + "? (y|n)").lower() == "y"

## Time
def date(t):
    """ Returns the date [year, month, day] from the time t"""
    return t.strftime('%Y-%m-%d').split("-")

def hour(t):
    """Return the time Hour:Minutes from t """
    return t.strftime('%H:%M')

def seconds(t):
    """Return the seconds between the 01/01/2017 and the datetime t"""
    return (t - datetime(2017,1,1)).total_seconds()

def sec2hr(t):
    """Transform the seconds in H:M
    Adapted from: http://stackoverflow.com/a/33504562"""
    # print("{}".format(timedelta(seconds=t)))

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

# OTRAS
# def input_fname(default, para="guardar/cargar ...", msje="Ingrese filename para"):
#     """Prompt the user to input a filename """
#
#     w = input_any(default, msje + " " + para)
#     if w.startswith("_"): # Si empieza con _ se appendea a default
#         w = default + w
#     return w
#
# def input_number(default=100, message="ingrese numero"):
#     while True:
#         num = input_any(default, message)
#
#         try:
#             num = int(num)
#             return num
#         except:
#             print("ingrese un numero")
#
# def input_words(default, message="ingrese una palabra"):
#     w = input_any(default, message)
#     # Separar palabras por comas y trim espacios en c/u
#     w = w.split(",")
#     return list(map(str.strip, w))
