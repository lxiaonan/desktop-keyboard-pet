# Windows Keyboard Pet

[中文 README](./README.md)

A lightweight Windows desktop panda pet. It floats on your desktop and reacts to your input: it types when you type, clicks its mouse when you click, blinks and gets sleepy while idle, and reacts when your cursor hovers over it.

## Quick Start

If you received the packaged version, just double-click:

```text
KeyboardPet.exe
```

After launch, the panda appears near the bottom-right of the desktop. Right-click the panda, or click the panda icon in the system tray, to open the menu.

If you are running from source:

```powershell
python -m pip install -r requirements.txt
.\run_silent.bat
```

To rebuild the executable:

```powershell
.\build_exe.ps1
```

## Features

- **Global keyboard reaction**: Uses Windows `GetAsyncKeyState`, so the pet reacts even when another app is focused.
- **Keyboard animation**: Each key press randomly picks one key, lights only that key, and plays a 6-frame press/release animation.
- **Mouse click animation**: Left/right clicks animate directly inside the original mouse area, without adding a detached overlay.
- **Mouse-following eyes**: While idle, the panda's eyes subtly follow the cursor.
- **Idle animation**: The panda blinks automatically and becomes sleepy after a period of inactivity.
- **Hover interaction**: Hovering over the panda triggers a blush and a subtle waving animation.
- **Petting interaction**: Clicking or dragging the panda triggers a petting animation with blush and small sparkles.
- **Light progression system**: Includes mood, energy, cleanliness, fullness, bond, and level, all of which change gradually over time and interaction.
- **Feeding, bathing, and resting**: Feed snacks to restore fullness, bathe the panda to improve cleanliness, or let it rest to recover energy.
- **Visible status feedback**: The panda shows small visual hints when it gets dirty, hungry, sleepy, or unhappy.
- **Status hint bubbles**: When energy, fullness, or cleanliness gets too low, the panda occasionally explains how to fix it.
- **Typing encouragement**: After sustained typing, the panda occasionally shows short encouragement bubbles.
- **Cursor avoidance**: Enabled by default. If the cursor rests on the panda for a moment, it gently moves away.
- **System tray menu**: The tray icon supports show/hide, size, topmost, startup, sound, cursor avoidance, health reminders, reset position, and exit.
- **Right-click menu**: Right-click the panda to open the common actions menu.
- **Optional sound effects**: Disabled by default. When enabled, typing, clicking, and petting play short beeps.
- **Health reminders**: Enabled by default. Reminds you to drink water every 30 minutes and move around every 1 hour. The popup stays for 1 minute or closes when confirmed.
- **Vocabulary flashcards**: Open from the right-click or tray menu. This repository does not include real vocabulary banks; users can create their own local vocabulary file.
- **Optional startup on login**: Uses the current user's Windows Run registry key. Admin permission is not required.
- **Persistent settings**: Saves size, position, topmost state, sound, cursor avoidance, and health reminder settings.
- **Single-instance lock**: Running `run_silent.bat` or `KeyboardPet.exe` repeatedly will not spawn multiple pandas.
- **Skin/action-pack layout**: The current panda skin lives in `assets\skins\panda`, making future skins easier to add.

## Run

Python is required. Python 3.10 or newer is recommended.

Run with a console window:

```bat
run.bat
```

Run silently:

```bat
run_silent.bat
```

`run_silent.bat` starts the app with `pythonw`, so no console window is shown. The app is single-instance, so repeated launches will not create multiple pandas.

## Controls

- **Left-click the panda**: Petting interaction.
- **Left-drag the panda**: Move it.
- **Right-click the panda**: Open the menu.
- **Care panel**: View mood, energy, cleanliness, fullness, bond, and level.
- **Tray icon**: Open the tray menu, show/hide, open vocabulary flashcards, toggle health reminders, or exit.
- **Hover the cursor**: Triggers hover interaction; if cursor avoidance is enabled, the panda gently moves away after a short delay.

## Menu Items

- **Mini**: About `84x108`.
- **Small**: About `101x130`.
- **Normal**: About `117x150`; the default size, 150px tall.
- **Large**: About `147x188`.
- **Topmost**: Keep the panda above other windows.
- **Startup**: Start automatically after Windows login.
- **Sound**: Toggle short beep effects. Disabled by default.
- **Avoid Cursor**: Toggle gentle cursor avoidance. Enabled by default.
- **Health Reminders**: Toggle water and movement reminders. Enabled by default.
- **Care Panel**: Open the progression/status panel.
- **Feed Snack**: Improve fullness and restore a little mood and energy.
- **Bath**: Open the bath window to improve cleanliness, mood, and bond.
- **Rest**: Open the rest window to recover energy and a bit of mood.
- **Vocabulary**: Open the flashcard window. A local vocabulary file is required.
- **Reset Position**: Move the panda back to the bottom-right corner.
- **Exit**: Close the app and tray icon.

## Settings

Settings are saved automatically to:

```text
%APPDATA%\KeyboardPet\settings.json
```

Saved values include size, position, topmost state, sound, cursor avoidance, health reminders, vocabulary progress, and care stats.

If the position becomes incorrect, delete this file and restart the app. It will return to the bottom-right corner.

## Vocabulary Format

This repository does not commit real vocabulary banks and does not ship a full word list by default. Create your own local vocabulary file:

```text
%APPDATA%\KeyboardPet\word_banks.json
```

If you open Vocabulary without a usable bank, the app will create an example file in the same directory:

```text
%APPDATA%\KeyboardPet\word_banks.example.json
```

The repository also includes a format example:

```text
assets\vocab\word_banks.example.json
```

Vocabulary JSON format:

```json
{
  "junior": {
    "label": "Junior English",
    "words": [
      {
        "word": "apple",
        "phonetic": "/ˈæpəl/",
        "meaning": "n. apple",
        "example": "I eat an apple every day."
      }
    ]
  },
  "custom": {
    "label": "My Word Bank",
    "words": [
      {
        "word": "focus",
        "phonetic": "/ˈfoʊkəs/",
        "meaning": "v. to concentrate; n. center of attention",
        "example": "I need to focus on this task."
      }
    ]
  }
}
```

Fields:

- `word`: required, the word.
- `meaning`: required, the definition or translation.
- `phonetic`: optional, phonetic spelling.
- `example`: optional, example sentence.

You can create any number of banks, such as `junior`, `senior`, `cet4`, `cet6`, `ielts`, or `custom`. Please verify the source and license of any vocabulary data before publishing it in a public repository.

## Skin Structure

The current panda skin is located at:

```text
assets\skins\panda
```

Main asset naming pattern:

```text
panda_pet_{size}_idle_0.png
panda_pet_{size}_blink_{frame}.png
panda_pet_{size}_sleep_{frame}.png
panda_pet_{size}_pet_{frame}.png
panda_pet_{size}_hover_{frame}.png
panda_pet_{size}_mouse_left_{frame}.png
panda_pet_{size}_mouse_right_{frame}.png
panda_pet_{size}_type_key{key}_{frame}.png
```

Where:

- `{size}` is one of `mini`, `small`, `normal`, `large`
- `{frame}` is the animation frame index
- `{key}` is the random keyboard highlight key index

Skin metadata:

```text
assets\skins\panda\skin.json
```

The app currently loads the `panda` skin by default. To add more characters later, create another skin folder with the same structure and extend `skin_path()` or add a skin selector.

## Build EXE

Run in PowerShell:

```powershell
.\build_exe.ps1
```

The script creates `.venv`, installs dependencies, and builds with PyInstaller:

```text
dist\KeyboardPet.exe
```

Build dependencies:

```text
Pillow
pystray
pyinstaller
```

Runtime dependencies are listed in:

```text
requirements.txt
```

## Privacy And Safety

- The app does not read, save, or upload typed text.
- Global input polling only checks whether keys and mouse buttons are currently pressed.
- Encouragement bubbles are triggered only by recent key press counts.
- Vocabulary progress is stored only in the local settings file.
- Startup uses the current user's Windows Run registry key.
- Sound effects use Windows `winsound.Beep`; no external audio files are required.

## Friend Links

- [linux.do](https://linux.do) — Linux and open-source technology community

## Troubleshooting

- **No tray icon**: Make sure `pystray` and `Pillow` are installed. Run `python -m pip install -r requirements.txt`.
- **A second panda does not appear**: This is expected. The app is single-instance.
- **Wrong position**: Delete `%APPDATA%\KeyboardPet\settings.json` and restart.
- **No vocabulary banks**: Create `%APPDATA%\KeyboardPet\word_banks.json`; use `assets\vocab\word_banks.example.json` as the format reference.
- **`Zz` appears above the panda**: Energy is low. Right-click the panda and choose **Rest** to recover.
- **No sound**: Make sure sound is enabled in the menu and check system volume.
- **Startup does not work**: Make sure Startup is checked in the menu. It uses the current user registry key and does not require admin rights.
