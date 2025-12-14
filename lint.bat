@echo off
call env\Scripts\activate

ruff check triangulator triangulator\test_triangulator.py

pause
