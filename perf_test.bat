@echo off
call env\Scripts\activate

pytest -m perf triangulator/test_triangulator.py

pause
