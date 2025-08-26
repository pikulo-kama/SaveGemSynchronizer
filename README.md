# 🎮 SaveGem – Save Manager for PC Games

## 📌 Overview
**SaveGem** is a simple desktop application built with **Tkinter** that allows players to **upload and download save files to Google Drive**.  

It’s designed for games that:
- Don’t have official cloud save support.
- Host servers directly on the player’s PC.
- Require manual save sharing between friends or across multiple devices.

With SaveGem, you can seamlessly keep your save games **backed up and in sync**.

---

## 🚀 Features
- ✅ Upload local save files to Google Drive  
- ✅ Download the latest save files from the drive  
- ✅ Easy-to-use desktop UI (Tkinter)  
- ✅ Works for any game where saves are stored locally  
- ✅ Has XBOX Live integration to see if any friends are currently playing
- ✅ Just to not mess anything up we do backup of your save before replacing it with the one from drive (just in case...)

---

## 🛠️ Installation
### Prerequisites
- **Python 3.9+** (with `pip`)  
- Google Cloud credentials (service account or OAuth client)  
- In order to work exe or just be able to use application you need file called `credentials.json` in root of project
- You also need `game-config.file-id.txt` to be present in root directory with ID of Google Drive game config. (See [placeholder file](./game-config-file-id.txt.placeholder)) 

### Install dependencies
#### Linux
```bash
./scripts/build.sh
```
####
Windows
```bash
./scripts/build.ps1
```