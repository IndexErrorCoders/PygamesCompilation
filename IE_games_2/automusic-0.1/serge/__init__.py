import sys


def suppressChipmunk():
    """Suppress loading of Chipmunk

    This is not very clean currently. The main purpose is to allow
    for skipping chipmunk when freezing applications.

    """
    import simplevecs
    sys.modules['pymunk'] = simplevecs
    import common
    common.PYMUNK_OK = False