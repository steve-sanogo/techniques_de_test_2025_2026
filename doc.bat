@echo off
call env\Scripts\activate

pdoc --html triangulator.triangulator triangulator.test_triangulator ^
     --output-dir docs --force --skip-errors

echo Documentation générée dans le dossier docs\
pause