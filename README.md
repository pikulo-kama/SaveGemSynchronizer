![GPLv3 License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Code Coverage](https://codecov.io/gh/pikulo-kama/SaveGemSynchronizer/branch/snapshot-4-1-0/graph/badge.svg)

# 💎 SaveGem – Save Manager for PC Games
<img src="assets/application-demo.png" alt="SaveGem Screenshot" width="800"/>

## 📌 Overview
**SaveGem** is a simple desktop application built with **PyQT** that allows players to **upload and download save files to Google Drive**.  

It’s designed for games that:
- Don’t have official cloud save support.
- Host servers directly on the player’s PC.
- Require manual save sharing between friends or across multiple devices.

With SaveGem, you can seamlessly keep your save games **backed up and in sync**.

---

## 🚀 Features
- ✅ Works for any game where saves are stored locally
- ✅ Easy-to-use desktop UI (PyQT)
- ✅ No manual reload! UI updates automatically
- ✅ Upload local save files to Google Drive  
- ✅ Download the latest save files from the drive
- ✅ Backs up previous save files before downloading save from cloud   
- ✅ Shows if any players are currently in the game
- ✅ **Auto Mode**. Allows to upload/download saves automatically!

---

## 🛠️ Building
### Prerequisites
- **Python 3.9+** (with `pip`)  
- Google Cloud credentials (service account or OAuth client)  
- In order to build EXE or just be able to use application you need file called `credentials.json` to be in root of the project
- You also need `config.json` to be present in root directory with ID of Google Drive game config. (See [placeholder file](./config.json.placeholder)) 

### Install dependencies and Build
Application is specific to **Windows**, but you can build it on Linux.
#### Linux
```bash
./scripts/linux/build.sh
```
####
Windows
```powershell
./scripts/windows/build.ps1
```

---

## 📦 Installer (Inno Setup)

The Windows installer for **SaveGem** is built using **[Inno Setup](https://jrsoftware.org/isinfo.php)**.  
We provide an `.iss` script in the repository, so you can create your own installer if needed.

### Build the Installer Yourself
1. Download and install [Inno Setup 6+](https://jrsoftware.org/isdl.php).  
2. Open `scripts/installer/setup.iss`.  
3. Compile the script from within Inno Setup to generate the `.exe` installer.

> ℹ️ **Note**: The `.iss` file is only a configuration script. Inno Setup itself is **not** distributed with SaveGem, you’ll need to install it separately if you want to build the installer.

---

## ⚠️ Important Note: Windows Defender Exclusion
SaveGem includes a process responsible for managing background tasks, which ensures that a single instance of the background worker is always running.

Due to the nature of this process management, Windows Defender (and similar antivirus software) may incorrectly flag the application as a threat (Trojan) and automatically remove it.

### Action Required
To prevent this issue, you must add the SaveGem installation directory to your antivirus exclusion list (e.g., Windows Defender, Avast, etc.) immediately after installation.

### Windows Defender Steps (Example)
1. Open Windows Security.
2. Go to *Virus & threat protection*.
3. Under *Virus & threat protection* settings, click *Manage settings*.
4. Scroll down to *Exclusions* and click *Add or remove exclusions*.
5. Click *Add an exclusion*, *select Folder*, and choose the SaveGem installation directory (e.g., C:\Program Files\SaveGem).

---

## ⚖️ Licensing

- Application code: GPLv3 (see [LICENSE](LICENSE))
- Dependencies and assets: see [NOTICE.md](NOTICE.md) for details
