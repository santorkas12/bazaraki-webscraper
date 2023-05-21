@echo off

rem Set the path to the Python executable
set python_executable="C:\github\bazaraki-webscraper\real-estate\webscrapevenv\Scripts\python.exe" 

rem Set the path to the Python script
set script_path="C:\github\bazaraki-webscraper\real-estate\scrape_to_json.py" 

rem Set the arguments for the Python script
set arg1=buy
set arg2=apartments-flats
set arg3=2

rem Run the Python script with the provided arguments
%python_executable% %script_path% %arg1% %arg2% %arg3%

pause
