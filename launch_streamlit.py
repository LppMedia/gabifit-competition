"""Launcher: adds user site-packages to sys.path, then runs streamlit."""
import sys
import os

user_pkgs = r"C:\Users\Tu papi\AppData\Roaming\Python\Python314\site-packages"
if user_pkgs not in sys.path:
    sys.path.insert(0, user_pkgs)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from streamlit.web import cli as stcli
sys.argv = ["streamlit", "run", "dashboard/app.py",
            "--server.port", "8503",
            "--server.headless", "true"]
stcli.main()
