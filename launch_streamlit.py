"""Launcher: dynamically locates streamlit and runs dashboard.
Uses glob to find the real streamlit location since AppData paths may be
virtualised differently in isolated preview environments.
"""
import sys
import os
import glob

os.environ["PYTHONIOENCODING"] = "utf-8"

# Strategy 1: known user site-packages path
_known = r"C:\Users\Tu papi\AppData\Roaming\Python\Python314\site-packages"
if _known not in sys.path:
    sys.path.insert(0, _known)

# Strategy 2: glob-search for streamlit under the user profile to find real path
_hits = glob.glob(r"C:\Users\Tu papi\**\streamlit\__init__.py", recursive=True)
for _hit in _hits:
    # parent of streamlit/ is the site-packages dir
    _site_pkg = os.path.dirname(os.path.dirname(_hit))
    if _site_pkg not in sys.path:
        sys.path.insert(0, _site_pkg)

# Strategy 3: also try system Python site-packages
import site
for _p in site.getsitepackages():
    if _p not in sys.path:
        sys.path.insert(0, _p)

from streamlit.web import cli as stcli
sys.argv = ["streamlit", "run", "dashboard/app.py",
            "--server.port", "8503",
            "--server.headless", "true"]
stcli.main()
