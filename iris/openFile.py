import subprocess
import os
import sys

def open_file(f):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', f))
    elif os.name == 'nt':
        os.startfile(f)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', f))
