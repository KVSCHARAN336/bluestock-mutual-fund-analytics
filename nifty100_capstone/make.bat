@echo off
if "%1"=="" goto help
if "%1"=="load" goto load
if "%1"=="ratios" goto ratios
if "%1"=="test" goto test
if "%1"=="report" goto report
if "%1"=="dashboard" goto dashboard
if "%1"=="api" goto api
if "%1"=="clean" goto clean

:help
echo Usage: make [load ^| ratios ^| test ^| report ^| dashboard ^| api ^| clean]
goto end

:load
python src/etl/loader.py
goto end

:ratios
python src/etl/ratios.py
goto end

:test
pytest tests/ -v
goto end

:report
python src/etl/report_generator.py
goto end

:dashboard
streamlit run dashboard/streamlit_app.py
goto end

:api
python src/api/app.py
goto end

:clean
rmdir /s /q __pycache__ src\etl\__pycache__ tests\__pycache__ tests\etl\__pycache__ 2>nul
del /q logs\*.log 2>nul
del /q data\db\nifty100.db 2>nul
echo Cleaned build artifacts and cache.
goto end

:end
