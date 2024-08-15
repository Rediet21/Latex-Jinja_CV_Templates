import subprocess
import requests
import os
import sys
import time
from pathlib import Path

def download_file(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    print(f"Downloaded {filename}")


def run_command(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    if process.returncode != 0:
        raise Exception(f"Command '{command}' failed with exit code {process.returncode}")
    
def install_latex_packages():
    # List of required LaTeX packages
    packages = ['raleway', 'moresize', 'fancyhdr', 'multirow']
    
    # Iterate over the list and install each package using mpm
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call(['mpm', '--install=' + package])
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}. Please check if MiKTeX is installed and accessible.")
            sys.exit(1)

def check_file_exists(filename):
    return os.path.isfile(filename)

def check_miktex_installed():
    try:
        result = subprocess.run(['pdflatex', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def set_path():
    miktex_path = r"C:\Program Files\MiKTeX\miktex\bin\x64"
    if miktex_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + miktex_path
        subprocess.call(f'setx PATH "%PATH%;{miktex_path}"', shell=True)
        print(f"PATH updated to include {miktex_path}")
    else:
        print(f"PATH already includes {miktex_path}")

def wait_for_miktex_installation(installer_filename, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_miktex_installed():
            print("MiKTeX installation detected.")
            return True
        print("Waiting for MiKTeX installation to complete...")
        time.sleep(10)
    print("Timeout waiting for MiKTeX installation.")
    return False

def compile_latex(latex_file, template_name):
    installer_filename = "basic-miktex-24.1-x64.exe"
    miktex_url = "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe"
    
    # Step 1: Download MiKTeX if not already downloaded
    if not check_file_exists(installer_filename):
        if not check_miktex_installed():
            print("MiKTeX installer not found. Downloading...")
            download_file(miktex_url, installer_filename)
    else:
        print("MiKTeX installer already downloaded.")
    
    # Step 2: Install MiKTeX if not already installed
    if not check_miktex_installed():
        print("MiKTeX not found. Installing...")
        install_process = subprocess.Popen(installer_filename, shell=True)
        print("Installation started. Waiting for it to complete...")
        if wait_for_miktex_installation(installer_filename):
            print("MiKTeX installation completed.")
        else:
            print("MiKTeX installation failed or timed out.")
            sys.exit(1)
    else:
        print("MiKTeX already installed.")
    
    # Step 3: Set PATH for Environment Variable
    set_path()
    
    # Wait a bit to ensure the environment variable is updated
    time.sleep(5)
    
    # Step 4: Automate Package Management
    run_command('initexmf --mkmaps')
    run_command('initexmf --update-fndb')
    install_latex_packages()
    
    # Step 5: Compile LaTeX File
    print(f"Compiling {latex_file} with template {template_name}...")
    
    # Path to the templates directory within the package
    template_dir = Path(__file__).resolve().parent / 'templates'
    template_path = template_dir / f"{template_name}.cls"
    
    # Check if the specified template exists
    if not template_path.is_file():
        print(f"Template '{template_name}' not found.")
        sys.exit(1)
    
    # Copy the template to the current directory
    temp_copy_path = Path(latex_file).stem + ".cls"
    if not check_file_exists(temp_copy_path):
        subprocess.run(f'copy "{template_path}" "{temp_copy_path}"', shell=True)
     # if else
    # Compile the LaTeX file
    #run_command(f"pdflatex -jobname={Path(latex_file).stem} -synctex=1 -interaction=nonstopmode {latex_file}")

    # Decide which LaTeX compiler to use based on the template name
    if template_name == "temp3":
        latex_command = f"xelatex -interaction=nonstopmode {latex_file}"
    else:
        latex_command = f"pdflatex -jobname={Path(latex_file).stem} -synctex=1 -interaction=nonstopmode {latex_file}"
    
    # Run the appropriate LaTeX compiler
    run_command(latex_command)
def main():
    
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: latexgen <latex-file> [template-name]")
        sys.exit(1)

    latex_file = sys.argv[1]
    template_name = sys.argv[2] if len(sys.argv) == 3 else 'default'

    compile_latex(latex_file, template_name)

if __name__ == "__main__":
    main()
