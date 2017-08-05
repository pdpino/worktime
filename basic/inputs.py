"""Provide input functions."""
import sys

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

def input_y_n(question="Do you want to...", default="y"):
    """Input a yes or no answer."""
    answer = input_any(default, "{}? (y|n)".format(question)).lower()
    return answer == "y" or answer == "yes"


## OTRAS
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
