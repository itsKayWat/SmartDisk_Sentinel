import subprocess
import sys

def install_requirements():
    requirements = [
        'tkinter',  # Usually included with Python
        'pillow',   # For image handling
        'send2trash',  # For safe file deletion
        'psutil'    # For system monitoring
    ]
    
    print("Installing requirements...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except:
            print(f"Error installing {package}")
    
    print("\nInstallation complete!")

if __name__ == "__main__":
    install_requirements()
