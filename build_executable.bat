call venv\Scripts\activate.bat
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building GameBuilder executable...
pyinstaller --clean --onefile --name GameBuilder main.py

echo.
echo Build complete! The executable is located in the "dist" folder.
pause
