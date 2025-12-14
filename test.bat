@echo off
call env\Scripts\activate

pytest triangulator/test_triangulator.py

pause