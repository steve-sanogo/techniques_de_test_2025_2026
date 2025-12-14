@echo off
REM Activer l'environnement virtuel
call env\Scripts\activate

REM Lancer uniquement le test_triangulator.py avec couverture et rapport HTML
pytest triangulator/test_triangulator.py --cov=triangulator --cov-report=html --html=report-coverage.html --self-contained-html

pause