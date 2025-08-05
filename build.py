import os
import platform
import shutil
import subprocess
import sys

# Get the absolute path of the directory where the script is located.
# This makes the script runnable from any location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_NAME = "zen.script"
APP_VERSION = "1.0.0"  # Application version
SCRIPT_FILE = os.path.join(BASE_DIR, "zen_script.py")
ICON_PNG = os.path.join(BASE_DIR, "logo_zen_dot.png")
ICON_ICO = os.path.join(BASE_DIR, "logo_zen_dot.ico")
ICON_SVG = os.path.join(BASE_DIR, "logo_zen_dot.svg")
ICON_ICNS = os.path.join(BASE_DIR, "logo_zen_dot.icns") # For macOS .app bundle
ISS_FILE = os.path.join(BASE_DIR, "zen.script.iss")

def build():
    """Build the application using PyInstaller."""
    print(f"Starting build for {platform.system()}...")

    # Clean up previous build artifacts
    for item in ["dist", "build", "installers", f"{APP_NAME}.spec"]:
        path = os.path.join(BASE_DIR, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

    # PyInstaller command arguments
    command = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        f"--add-data={ICON_PNG}{os.pathsep}.",   # For runtime icon
        SCRIPT_FILE,
    ]

    # Add platform-specific options
    system = platform.system()
    if system == "Windows":
        command.insert(6, f"--add-data={ICON_ICO}{os.pathsep}.") # Add ico for windows runtime
        command.insert(4, f"--icon={ICON_ICO}")
    elif system == "Darwin":  # macOS
        command.insert(4, f"--icon={ICON_ICNS}")
        # The --onefile and --windowed flags on macOS create a .app bundle in dist/

    print(f"Running command: {' '.join(command)}")
    
    try:
        subprocess.check_call(command)
        print("\nBuild successful!")

        # Post-build steps for installer creation
        if system == "Windows":
            print(f"Executable created in: {os.path.join(BASE_DIR, 'dist')}")
            create_windows_installer()
        elif system == "Darwin":
            print(f"App bundle created in: {os.path.join(BASE_DIR, 'dist')}")
            create_mac_dmg()
        elif system == "Linux":
            print(f"Binary created in: {os.path.join(BASE_DIR, 'dist')}")
            create_arch_package()

    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}", file=sys.stderr)
        sys.exit(1)

def find_iscc():
    """
    Find the Inno Setup compiler (iscc.exe).
    Checks the system PATH first, then common default installation locations.
    """
    # 1. Check system PATH
    iscc = shutil.which("iscc")
    if iscc:
        return iscc

    # 2. If not in PATH, check default installation locations for Inno Setup 6
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    
    default_paths = [
        os.path.join(program_files_x86, "Inno Setup 6", "iscc.exe"),
        os.path.join(program_files, "Inno Setup 6", "iscc.exe"),
    ]

    for path in default_paths:
        if os.path.exists(path):
            print(f"Found Inno Setup compiler at: {path}")
            return path
            
    return None

def create_mac_dmg():
    """Creates a macOS disk image (.dmg) containing the .app bundle."""
    print("\nCreating macOS disk image (.dmg)...")

    # Check for create-dmg tool
    if not shutil.which("create-dmg"):
        print("\n[ERROR] 'create-dmg' command not found.", file=sys.stderr)
        print("Please install it using Homebrew: 'brew install create-dmg'", file=sys.stderr)
        sys.exit(1)

    # Paths for the DMG creation
    dist_path = os.path.join(BASE_DIR, "dist")
    app_bundle_path = os.path.join(dist_path, f"{APP_NAME}.app")
    installer_dir = os.path.join(BASE_DIR, "installers")
    dmg_path = os.path.join(installer_dir, f"{APP_NAME}-{APP_VERSION}.dmg")

    # Ensure the app bundle exists
    if not os.path.exists(app_bundle_path):
        print(f"\n[ERROR] App bundle not found at '{app_bundle_path}'", file=sys.stderr)
        sys.exit(1)

    # Create installers directory if it doesn't exist
    os.makedirs(installer_dir, exist_ok=True)

    # Command to create the DMG
    command = [
        "create-dmg",
        "--volname", f"{APP_NAME} {APP_VERSION}",
        "--window-pos", "200", "120",
        "--window-size", "600", "400",
        "--icon-size", "100",
        "--icon", f"{APP_NAME}.app", "175", "170",
        "--hide-extension", f"{APP_NAME}.app",
        "--app-drop-link", "425", "170",
        dmg_path,
        app_bundle_path,
    ]

    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.check_call(command)
        print(f"\nDMG created successfully at: {dmg_path}")
    except subprocess.CalledProcessError as e:
        print(f"\nDMG creation failed with error: {e}", file=sys.stderr)
        sys.exit(1)

def create_arch_package():
    """Creates an Arch Linux package (.pkg.tar.zst)."""
    print("\nCreating Arch Linux package...")

    if not shutil.which("makepkg"):
        print("\n[WARNING] 'makepkg' command not found. Skipping Arch package creation.", file=sys.stderr)
        print("This step is intended for Arch Linux or Arch-based distributions.", file=sys.stderr)
        return

    # Define paths
    dist_path = os.path.join(BASE_DIR, 'dist')
    binary_path = os.path.join(dist_path, APP_NAME)
    installer_dir = os.path.join(BASE_DIR, "installers")
    arch_build_dir = os.path.join(BASE_DIR, "build", "arch")
    
    # Ensure the binary exists
    if not os.path.exists(binary_path):
        print(f"\n[ERROR] Binary not found at '{binary_path}'", file=sys.stderr)
        sys.exit(1)

    # Create build directories
    os.makedirs(arch_build_dir, exist_ok=True)
    os.makedirs(installer_dir, exist_ok=True)

    # Create PKGBUILD content
    pkgbuild_content = f"""
# Maintainer: kittykode io <github.com/kittykatkode>
pkgname='{APP_NAME.lower()}'
pkgver='{APP_VERSION}'
pkgrel=1
pkgdesc='A simple, zen-like text editor.'
arch=('x86_64')
url='https://github.com/kittykatkode/zen.script'
license=('MIT')
depends=('tk')
source=('{APP_NAME}'
        '{APP_NAME}.desktop'
        '{os.path.basename(ICON_PNG)}')
sha256sums=('SKIP'
            'SKIP'
            'SKIP')

package() {{
    cd "$srcdir"
    install -Dm755 "{APP_NAME}" "$pkgdir/usr/bin/{APP_NAME}"
    install -Dm644 "{os.path.basename(ICON_PNG)}" "$pkgdir/usr/share/pixmaps/{APP_NAME}.png"
    install -Dm644 "{APP_NAME}.desktop" "$pkgdir/usr/share/applications/{APP_NAME}.desktop"
}}
"""

    # Create .desktop file content
    desktop_file_content = f"""
[Desktop Entry]
Name=zen.script
Comment=A simple, zen-like text editor
Exec={APP_NAME}
Icon={APP_NAME}
Terminal=false
Type=Application
Categories=Utility;TextEditor;
"""

    # Write files to the build directory
    with open(os.path.join(arch_build_dir, "PKGBUILD"), "w") as f:
        f.write(pkgbuild_content.strip())
    with open(os.path.join(arch_build_dir, f"{APP_NAME}.desktop"), "w") as f:
        f.write(desktop_file_content.strip())

    # Copy necessary source files for makepkg
    shutil.copy(binary_path, os.path.join(arch_build_dir, APP_NAME))
    shutil.copy(ICON_PNG, arch_build_dir)

    # Run makepkg
    command = ["makepkg", "-f", "--noconfirm"]
    print(f"Running command: {' '.join(command)} in {arch_build_dir}")
    try:
        subprocess.check_call(command, cwd=arch_build_dir)
        print("\n'makepkg' completed successfully.")
        # Find the created package and move it
        for file in os.listdir(arch_build_dir):
            if file.endswith(".pkg.tar.zst"):
                src_pkg = os.path.join(arch_build_dir, file)
                dest_pkg = os.path.join(installer_dir, file)
                shutil.move(src_pkg, dest_pkg)
                print(f"Arch package moved to: {dest_pkg}")
                return
        print("\n[ERROR] Could not find the generated package file.", file=sys.stderr)
        sys.exit(1)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\nPackage creation failed with error: {e}", file=sys.stderr)
        sys.exit(1)

def create_windows_installer():
    """Creates a Windows installer using Inno Setup."""
    print("\nCreating Windows installer...")
    
    iscc_path = find_iscc()
    if not iscc_path:
        print("\n[ERROR] Inno Setup Compiler (iscc.exe) not found.", file=sys.stderr)
        print("Could not find it in your system's PATH or in default installation directories.", file=sys.stderr)
        print("Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php", file=sys.stderr)
        print("and ensure its installation directory is added to your PATH if installed in a non-standard location.", file=sys.stderr)
        sys.exit(1)

    # Ensure the Inno Setup script file exists
    if not os.path.exists(ISS_FILE):
        print(f"\n[ERROR] Inno Setup script not found at '{ISS_FILE}'", file=sys.stderr)
        sys.exit(1)

    command = [iscc_path, f'/DAppVersion={APP_VERSION}', ISS_FILE]
    
    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.check_call(command)
        print("\nInstaller created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\nInstaller creation failed with error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    build()