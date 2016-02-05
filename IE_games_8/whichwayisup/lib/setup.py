from distutils.core import setup
import py2exe

setup(console=['main.py'],zipfile=None, windows = [{ 'script': "main.py", 'icon_resources': [(0x0004,'whichway.ico')]}])
