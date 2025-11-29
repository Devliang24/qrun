# Manual Setup Guide for AI Test Framework

Due to network restrictions in the current environment, the following tools need to be installed manually.

## 1. Android SDK Platform Tools (ADB)

1.  **Download**: 
    *   Official: [https://dl.google.com/android/repository/platform-tools-latest-windows.zip](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
    *   Or search for "SDK Platform Tools release notes" to find the download.
2.  **Install**:
    *   Extract the contents to `C:\Android\platform-tools`.
    *   You should see `adb.exe` at `C:\Android\platform-tools\adb.exe`.
3.  **Add to PATH**:
    *   Add `C:\Android\platform-tools` to your System Environment Variables `PATH`.

## 2. Genymotion Emulator

1.  **Download**:
    *   Go to [https://www.genymotion.com/download/](https://www.genymotion.com/download/)
    *   Download the "Desktop" version (with VirtualBox if you don't have it).
2.  **Install**:
    *   Run the installer and follow the prompts.
3.  **Setup Virtual Device**:
    *   Open Genymotion.
    *   Click "+" to add a device.
    *   Select **Google Pixel 3 XL**.
    *   Select **Android 9.0** (API 28).
    *   Name it: `Google Pixel 3 XL` (matches our config).
    *   Install and Start the device.

## 3. Verification

Once installed, run these commands in your terminal:

```powershell
adb version
ai-test check-env
```
