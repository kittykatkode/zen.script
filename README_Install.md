    cd zen.script
    python zen_script.py
    ```

## How to Build a Standalone Executable

You can package this application into a single executable file that includes all dependencies. This allows you to run it on Windows, macOS, or Linux without installing Python.

1.  **Install dependencies from `requirements.txt`:**
    ```sh
    pip install -r requirements.txt
    ```

2.  **Run the build script:**
    ```sh
    python build.py
    ```

3.  **Find the executable:**
    The standalone application will be located in the `dist` directory. You can copy this file anywhere and run it.

    -   On Windows: `dist/zen.script.exe`
    -   On macOS: `dist/zen.script.app`
    -   On Linux: `dist/zen.script`
