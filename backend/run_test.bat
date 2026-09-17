@echo off
echo Running RAG verification test using virtual environment...
"%~dp0venv\Scripts\python.exe" "%~dp0test_rag.py"
pause
