# 🎮 SaveGem – Cloud Save Manager for PC Games

## 📌 Overview
**SaveGem** is a simple desktop application built with **Tkinter** that allows players to **upload and download save files to Google Cloud**.  

It’s designed for games that:
- Don’t have official cloud save support.
- Host servers directly on the player’s PC.
- Require manual save sharing between friends or across multiple devices.

With SaveGem, you can seamlessly keep your save games **backed up and in sync**.

---

## 🚀 Features
- ✅ Upload local save files to Google Cloud  
- ✅ Download the latest save files from the cloud  
- ✅ Easy-to-use desktop UI (Tkinter)  
- ✅ Works for any game where saves are stored locally  
- ✅ Has XBOX Live integration to see if any friends are currently playing
- ✅ Just to not mess anything we do backup of your save before replacing it with the one from cloud (just in case..)

---

## 🛠️ Installation
### Prerequisites
- **Python 3.9+** (with `pip`)  
- Google Cloud credentials (service account or OAuth client)  
- In order to work exe or just be able to use application you need file called `credentials.json` in root of project

### Install dependencies (Windows)
```bash
./build.sh
