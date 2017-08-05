"""Basic functions to provide"""
import sys

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
