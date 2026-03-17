@echo off
set PYTHONPATH=C:\Users\Tu papi\AppData\Roaming\Python\Python314\site-packages
set PYTHONIOENCODING=utf-8
C:\Python314\python.exe -m streamlit run dashboard/app.py --server.port 8503 --server.headless true
