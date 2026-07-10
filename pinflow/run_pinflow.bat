@echo off
REM PinFlow scheduled launcher. Env vars come from the user-scope vars set via setx.
cd /d "C:\Users\VISAL\Desktop\Realistic Project"
echo ---- run started %DATE% %TIME% ---->> pinflow_runs.log
python orchestrator.py >> pinflow_runs.log 2>&1
echo ---- run ended %DATE% %TIME% ---->> pinflow_runs.log
