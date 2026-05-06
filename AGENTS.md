# AGENTS.md

## Project Status

This project is a Windows desktop panda pet located at:

```text
C:\Users\luoyn\Desktop\aiproject\desktop-keyboard-pet
```

Current main entry:

```text
src\keyboard_pet.py
```

Run scripts:

```text
run.bat
run_silent.bat
```

The recommended manual launch path is `run_silent.bat`.

## Current Features

- Transparent always-on-top Tkinter desktop pet window.
- Global keyboard and mouse detection via Windows `GetAsyncKeyState`.
- Single-instance mutex: repeated launches do not create multiple pandas.
- Keyboard animation with random single-key highlight, 10 key variants, 6 frames each.
- Mouse left/right click animation integrated into the original mouse image layer.
- Idle blink and sleepy animations.
- Hover interaction with blush/wave frames.
- Petting interaction with stronger head-pat hand, blush, and sparkles.
- Typing encouragement bubbles. Current threshold: 14 key events within 10 seconds, 8 second cooldown. Messages are `加油`, `写得好快`, `很稳`, `注意休息`, `继续冲`, `手感来了`; consecutive duplicate messages are avoided.
- Optional sound effects via `winsound.Beep`, default off.
- Optional cursor avoidance, default on.
- Health reminders, default on. Water reminder every 30 minutes, movement reminder every 60 minutes; reminder popup auto-closes after 1 minute or closes on confirmation.
- System tray menu via `pystray`.
- Optional startup on login via current-user Windows Run registry key.
- Persistent settings stored at `%APPDATA%\KeyboardPet\settings.json`.
- Skin/action assets are loaded from `assets\skins\panda`.

## Important Files

- `src\keyboard_pet.py`: application logic.
- `assets\skins\panda`: active skin and animation frames.
- `README.md`: bilingual user-facing documentation.
- `requirements.txt`: runtime dependencies.
- `build_exe.ps1`: PyInstaller build script.

## Current Size Presets

- `mini`: about `84x108`.
- `small`: about `101x130`.
- `normal`: about `117x150`; default, 150px high.
- `large`: about `147x188`.

## Mistakes And Lessons Learned

- The first global input approach used low-level keyboard/mouse hooks. It passed simple tests but behaved like focus-only input in real use. The project now uses `GetAsyncKeyState` polling instead.
- The first image animation approach overlaid visual effects on top of a static image. It looked disconnected. Important actions now use generated PNG frame sequences.
- Mouse click animation originally drew a new mouse shape on top of the original image, which looked like a jumping layer. It was changed to tint/highlight the existing mouse pixels only.
- Keyboard animation originally lit multiple keys over one action. It now selects one key per action and keeps that same key through all frames.
- A tiny/default size was first added separately as `150px 高`. The user preferred `正常大小` to mean 150px high, so size labels were reorganized.
- Settings were briefly saved as `0,0` because `winfo_x()` and `winfo_y()` can be unreliable immediately after `geometry()`. The app now tracks `window_x` and `window_y` internally.
- Repeated `run_silent.bat` launches created multiple pandas. A Windows named mutex now enforces a single instance.
- Tray support required `pystray`; it is now listed in `requirements.txt` and installed in `build_exe.ps1`.

## Development Notes

- Prefer editing source with `apply_patch`.
- When regenerating assets, update both the active skin directory and any code expecting frame names.
- Keep animation frame names consistent:

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

- Do not rely on reading user text. The app should only react to key/mouse state.
- Startup registry changes should stay current-user only; no admin requirement.
- Sound should remain optional and default off.
- Health reminders should remain optional and default on. Water interval is 30 minutes; movement interval is 1 hour; popup lifetime is 1 minute.

## Verification Commands

```powershell
python -m py_compile src\keyboard_pet.py
python -c "from src.keyboard_pet import PetApp; app=PetApp(); app.root.after(500, app.close); app.run(); print('smoke-ok')"
```

For startup registry behavior, test enable/disable in the same command and restore it to the previous state.
