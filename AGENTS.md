# AGENTS.md

This file is the project guide for AI coding agents working on this repository. Keep it practical, current, and specific. If behavior, commands, assets, or project rules change, update this file in the same change.

## Project Overview

`desktop-keyboard-pet` is a lightweight Windows desktop panda pet. It floats above the desktop and reacts locally to keyboard and mouse activity.

Primary goals:

- Stay lightweight and local-only.
- React to keyboard and mouse state without reading typed text.
- Provide cute but non-disruptive companionship during work.
- Keep the skin/action-pack structure easy to extend.
- Remain clean enough for GitHub distribution.

Non-goals for now:

- No AI chat runtime.
- No cloud service.
- No telemetry.
- No invasive input logging.
- No admin-only features.

## Repository Layout

```text
.
├─ src/
│  └─ keyboard_pet.py
├─ assets/
│  └─ skins/
│     └─ panda/
│  └─ vocab/
│     └─ word_banks.json
├─ README.md
├─ AGENTS.md
├─ requirements.txt
├─ run.bat
├─ run_silent.bat
├─ build_exe.ps1
└─ .gitignore
```

Important files:

- `src/keyboard_pet.py`: main application logic.
- `assets/skins/panda`: active panda skin and animation frames.
- `assets/skins/panda/skin.json`: skin metadata.
- `assets/vocab/word_banks.json`: built-in starter vocabulary banks.
- `README.md`: bilingual user-facing documentation.
- `requirements.txt`: runtime Python dependencies.
- `build_exe.ps1`: PyInstaller build script.
- `run.bat`: run with a console window.
- `run_silent.bat`: run with `pythonw`, no console window.

## Runtime And Platform

Target platform:

- Windows desktop.

Runtime:

- Python 3.10+ recommended.
- Tkinter for the transparent desktop window.
- Pillow for image/tray icon handling.
- pystray for the Windows tray menu.
- Windows APIs through `ctypes`, `winreg`, and `winsound`.

Dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run Commands

Manual launch:

```powershell
.\run.bat
```

Silent launch:

```powershell
.\run_silent.bat
```

Build EXE:

```powershell
.\build_exe.ps1
```

Generated EXE path:

```text
dist\KeyboardPet.exe
```

## Verification Commands

Use these before finalizing changes:

```powershell
python -m py_compile src\keyboard_pet.py
python -c "from src.keyboard_pet import PetApp; app=PetApp(); app.root.after(500, app.close); app.run(); print('smoke-ok')"
```

Reminder popup smoke test:

```powershell
python -c "from src.keyboard_pet import PetApp; app=PetApp(); app._show_reminder('water'); print(app.reminder_window is not None); app._close_reminder(); app.root.destroy()"
```

Startup registry test must restore state in the same command:

```powershell
python -c "from src.keyboard_pet import set_startup_enabled, startup_enabled; before=startup_enabled(); set_startup_enabled(True); mid=startup_enabled(); set_startup_enabled(False); after=startup_enabled(); print(before, mid, after)"
```

Do not leave startup enabled during automated tests unless the user explicitly asks.

## Current Features

- Transparent always-on-top Tkinter desktop pet window.
- Global keyboard and mouse detection via Windows `GetAsyncKeyState`.
- Single-instance mutex: repeated launches do not create multiple pandas.
- Keyboard animation with random single-key highlight, 10 key variants, 6 frames each.
- Mouse left/right click animation integrated into the original mouse image layer.
- Idle blink and sleepy animations.
- Hover interaction with blush/wave frames.
- Petting interaction with visible head-pat hand, blush, and sparkles.
- Light progression system with mood, energy, cleanliness, fullness, bond, level, and exp.
- Feeding interaction that raises fullness and restores a bit of mood and energy.
- Bath window that raises cleanliness, mood, and bond.
- Typing encouragement bubbles.
- Optional sound effects via `winsound.Beep`, default off.
- Optional cursor avoidance, default on.
- Health reminders, default on:
  - Water reminder every 30 minutes.
  - Movement reminder every 60 minutes.
  - Popup auto-closes after 1 minute or closes on confirmation.
- Vocabulary flashcards from right-click/tray menu:
  - Banks: junior high, senior high, CET-4, CET-6, IELTS.
  - Current counts: junior 1603, senior 3677, CET-4 3849, CET-6 5407, IELTS 5040.
  - Tracks known/unknown counts in settings.
  - Built-in data is imported from ECDICT and filtered by tags.
- System tray menu via `pystray`.
- Optional startup on login via current-user Windows Run registry key.
- Persistent settings stored at `%APPDATA%\KeyboardPet\settings.json`.
- Skin/action assets loaded from `assets/skins/panda`.

## Current Behavior Constants

These are defined in `src/keyboard_pet.py`:

```text
WATER_REMINDER_SECONDS = 30 * 60
MOVE_REMINDER_SECONDS = 60 * 60
REMINDER_POPUP_SECONDS = 60
MUTEX_NAME = Global\KeyboardPetPandaSingleInstance
```

Typing encouragement:

- Threshold: 14 key events within 10 seconds.
- Cooldown: 8 seconds.
- Display time: 2.8 seconds.
- Messages:
  - `加油`
  - `写得好快`
  - `很稳`
  - `注意休息`
  - `继续冲`
  - `手感来了`
- Consecutive duplicate messages are avoided.

Size presets:

- `mini`: about `84x108`.
- `small`: about `101x130`.
- `normal`: about `117x150`; default, 150px high.
- `large`: about `147x188`.

## Settings

Settings file:

```text
%APPDATA%\KeyboardPet\settings.json
```

Current settings shape:

```json
{
  "size": "normal",
  "topmost": true,
  "sound": false,
  "avoid_mouse": true,
  "reminders": true,
  "water_reminder_remaining": 1800,
  "move_reminder_remaining": 3600,
  "vocab_bank": "junior",
  "vocab_progress": {},
  "care_stats": {
    "mood": 72,
    "energy": 78,
    "cleanliness": 76,
    "fullness": 74,
    "bond": 0,
    "level": 1,
    "exp": 0
  },
  "x": 1761,
  "y": 848
}
```

Rules:

- Keep settings backward-compatible.
- If adding a setting, provide a safe default.
- Do not store user input text.
- If position is bad during testing, delete the settings file and restart.

## Skin And Asset Contract

Active skin:

```text
assets/skins/panda
```

Frame naming contract:

```text
panda_pet_{size}.png
panda_pet_{size}_idle_0.png
panda_pet_{size}_blink_{frame}.png
panda_pet_{size}_sleep_{frame}.png
panda_pet_{size}_pet_{frame}.png
panda_pet_{size}_hover_{frame}.png
panda_pet_{size}_mouse_left_{frame}.png
panda_pet_{size}_mouse_right_{frame}.png
panda_pet_{size}_type_{frame}.png
panda_pet_{size}_type_key{key}_{frame}.png
```

Where:

- `{size}` is one of `mini`, `small`, `normal`, `large`.
- `{frame}` is a zero-based animation frame index.
- `{key}` is a zero-based keyboard key variant index.

Current animation counts:

- `idle`: 1 frame.
- `blink`: 5 frames.
- `sleep`: 6 frames.
- `pet`: 6 frames.
- `hover`: 6 frames.
- `mouse_left`: 6 frames.
- `mouse_right`: 6 frames.
- `type`: 10 key variants x 6 frames.

Asset rules:

- Program currently loads from `assets/skins/panda` through `skin_path()`.
- Do not reintroduce duplicate root-level `assets/panda_pet*.png` files.
- When regenerating assets, update the active skin directory.
- Keep PNG assets reasonably small; avoid committing generated build outputs.

## Vocabulary Contract

Vocabulary data lives at:

```text
assets/vocab/word_banks.json
```

Top-level shape:

```json
{
  "junior": {
    "label": "初中英语库",
    "words": [
      {
        "word": "apple",
        "phonetic": "/ˈæpəl/",
        "meaning": "n. 苹果",
        "example": "I eat an apple every day."
      }
    ]
  }
}
```

Rules:

- Keep JSON UTF-8.
- Keep `word` and `meaning` required.
- `phonetic` and `example` are optional but recommended.
- Current banks are generated from ECDICT tag filters:
  - `zk` -> `junior`
  - `gk` -> `senior`
  - `cet4` -> `cet4`
  - `cet6` -> `cet6`
  - `ielts` -> `ielts`
- ECDICT is MIT-licensed; preserve attribution in docs when describing the source.
- Do not describe these imported banks as official exam authority word lists.
- Progress is stored in `%APPDATA%\KeyboardPet\settings.json` under `vocab_progress`.
- Do not store personal study content outside local settings unless the user explicitly asks.

## Coding Guidelines

- Prefer small, focused changes.
- Prefer standard library and existing dependencies.
- Keep Windows-specific behavior guarded by `sys.platform.startswith("win")`.
- Keep sound optional and default off.
- Keep reminders optional and default on.
- Keep startup registry current-user only; no admin requirement.
- Keep input handling local-only. Do not read, log, save, or upload typed text.
- Keep `README.md` synchronized with user-facing behavior.
- Keep this `AGENTS.md` synchronized with developer-facing behavior.
- When adding or changing word banks, update both README and this file.
- Care defaults should remain lightweight and friendly; avoid overcomplicating the progression loop unless explicitly requested.

## Privacy And Safety Rules

Strict rules:

- Never store typed text.
- Never upload input data.
- Never add network telemetry.
- Never require administrator privileges for normal use.
- Startup changes must use only the current user Run key.
- Reminder logic must be local timers only.

Input model:

- `GetAsyncKeyState` checks key/button state.
- The app only uses key event counts and virtual key codes for animation selection.
- Encouragement is based on recent key count, not content.

## GitHub Hygiene

Before committing:

```powershell
python -m py_compile src\keyboard_pet.py
python -c "from src.keyboard_pet import PetApp; app=PetApp(); app.root.after(500, app.close); app.run(); print('smoke-ok')"
```

Clean generated caches:

```powershell
Remove-Item -Recurse -Force src\__pycache__ -ErrorAction SilentlyContinue
```

Do not commit:

- `__pycache__/`
- `.venv/`
- `build/`
- `dist/`
- `*.spec`
- local logs
- local user settings

`.gitignore` already covers common generated files.

## Known Mistakes And Lessons

- Low-level keyboard/mouse hooks passed simple tests but behaved like focus-only input in real use. Use `GetAsyncKeyState` polling instead.
- Early animation overlays looked disconnected. Important actions now use generated PNG frame sequences.
- Mouse click animation originally drew a new mouse on top of the original image. It now tints/highlights existing mouse pixels.
- Keyboard animation originally lit multiple keys during one action. It now selects one key per action and keeps that key through the frames.
- A separate `150px 高` menu item was confusing. `正常大小` now means 150px high.
- `winfo_x()` and `winfo_y()` can be unreliable immediately after `geometry()`. Track `window_x` and `window_y` internally.
- Repeated `run_silent.bat` launches created multiple pandas. A Windows named mutex now enforces single instance.
- Tray support requires `pystray`; keep it in `requirements.txt` and `build_exe.ps1`.
- Root-level asset duplicates made the repo noisy. Only keep active skin assets under `assets/skins/panda`.
- Vocabulary quality improved after switching from tiny starter data to full MIT-licensed ECDICT imports filtered by tags.

## Future Ideas

Useful but not yet implemented:

- Skin selector UI.
- Skin authoring template with anchor coordinates.
- Preview GIF or screenshots for GitHub README.
- Window-edge behavior such as sitting near screen edges.
- Optional idle schedule profiles.
- A small CLI/script to regenerate frames from `skin.json`.

Avoid adding these until requested:

- AI chat.
- Cloud sync.
- Complex physics/window grabbing.
- Any feature that requires admin rights.
