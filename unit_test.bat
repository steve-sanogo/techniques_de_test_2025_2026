@echo off
call env\Scripts\activate

pytest -m "not perf" triangulator/test_triangulator.py

pause
