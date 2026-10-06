"""Importing this re-runs the script under ./venv's python, which has the dependencies"""

import os
import sys

python = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'bin', 'python')
if sys.prefix == sys.base_prefix and os.path.exists(python):
    os.execv(python, [python] + sys.argv)
