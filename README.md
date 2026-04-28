# CFG Generator Docker Instructions

## Prerequisites
- Docker installed on your system.

## Build the Image
Open your terminal in the project folder and run:
`docker build -t cfg-generator .`

## Run the Container
Since the script generates a PNG file, you need to mount a local directory to see the output.
Replace `$(pwd)` with `${PWD}` on Windows PowerShell.

### Linux / macOS / PowerShell:
`docker run -it -v ${PWD}:/app cfg-generator`

### Command Prompt (Windows):
`docker run -it -v ${PWD}:/app cfg-generator`

### Create a CFG:
paste valid python code in the code.py file or directly in the command line.
When prompted enter the file name with just `Code.py`

## Notes
- The 'view=True' setting in the script might attempt to open a window. 
- Since Docker containers are headless, the script will save 'cfg_output.png' to your local folder, but might show an error when trying to open the default image viewer. This is normal in a containerized environment.