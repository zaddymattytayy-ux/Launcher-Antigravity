# PyQt6 DLL Load Error - Fix Instructions

The error `ImportError: DLL load failed while importing QtCore: The specified procedure could not be found` is caused by missing Visual C++ Redistributable packages on Windows.

## Solution

### Option 1: Install Visual C++ Redistributable (Recommended)

1. Download and install **Microsoft Visual C++ Redistributable for Visual Studio 2015-2022**:
   - **64-bit**: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - **32-bit**: https://aka.ms/vs/17/release/vc_redist.x86.exe

2. Install both x64 and x86 versions if you're on a 64-bit system (some applications need both)

3. Restart your computer

4. Try running the launcher again:
   ```bash
   python native/main.py
   ```

### Option 2: Clean Reinstall PyQt6

If Option 1 doesn't work, try a clean reinstall:

```bash
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-WebEngine PyQt6-WebEngine-Qt6 PyQt6-sip
pip cache purge
pip install PyQt6==6.6.1 PyQt6-WebEngine==6.6.0
```

### Option 3: Use a Virtual Environment

Create a clean virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r native/requirements.txt
python native/main.py
```

## Verification

To verify PyQt6 is working, run this simple test:

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 works!')"
```

If this prints "PyQt6 works!" without errors, the issue is resolved.
