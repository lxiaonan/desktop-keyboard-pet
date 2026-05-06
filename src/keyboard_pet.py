import ctypes
import json
import math
import os
from pathlib import Path
import queue
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None

if sys.platform.startswith("win"):
    import winreg
    import winsound
else:
    winreg = None
    winsound = None


TRANSPARENT = "#ff00ff"
SIZES = ("mini", "small", "normal", "large")
APP_NAME = "KeyboardPet"
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
MUTEX_NAME = "Global\\KeyboardPetPandaSingleInstance"
WATER_REMINDER_SECONDS = 30 * 60
MOVE_REMINDER_SECONDS = 60 * 60
REMINDER_POPUP_SECONDS = 60
DEFAULT_VOCAB_BANK = "junior"


def resource_path(*parts):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base.joinpath(*parts)


def skin_path(*parts):
    return resource_path("assets", "skins", "panda", *parts)


def vocab_path(*parts):
    return resource_path("assets", "vocab", *parts)


def config_path():
    app_data = os.environ.get("APPDATA")
    base = Path(app_data) if app_data else Path.home()
    return base / "KeyboardPet" / "settings.json"


def startup_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    script = resource_path("run_silent.bat")
    return f'"{script}"'


def startup_enabled():
    if not winreg:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except OSError:
        return False


def set_startup_enabled(enabled):
    if not winreg:
        return
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


class SingleInstance:
    ERROR_ALREADY_EXISTS = 183

    def __init__(self):
        self.handle = None
        if sys.platform.startswith("win"):
            self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            self.kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
            self.kernel32.CreateMutexW.restype = ctypes.c_void_p
            self.kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
            self.kernel32.CloseHandle.restype = ctypes.c_bool
        else:
            self.kernel32 = None

    def acquire(self):
        if not self.kernel32:
            return True
        self.handle = self.kernel32.CreateMutexW(None, True, MUTEX_NAME)
        if not self.handle:
            return True
        return ctypes.get_last_error() != self.ERROR_ALREADY_EXISTS

    def release(self):
        if self.kernel32 and self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None


class GlobalInputPoller:
    """Polls global input state, so the pet reacts even when another app is focused."""

    VK_LBUTTON = 0x01
    VK_RBUTTON = 0x02

    def __init__(self, events):
        self.events = events
        self.stop_event = threading.Event()
        self.thread = None
        self.previous_keys = set()
        self.previous_mouse = {"left": False, "right": False}
        self.key_codes = [
            code
            for code in range(0x08, 0xFF)
            if code not in (self.VK_LBUTTON, self.VK_RBUTTON)
        ]

        if sys.platform.startswith("win"):
            self.user32 = ctypes.WinDLL("user32", use_last_error=True)
            self.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
            self.user32.GetAsyncKeyState.restype = ctypes.c_short
        else:
            self.user32 = None

    def start(self):
        if not self.user32:
            self.events.put(("input_error", "Only Windows global input polling is supported"))
            return
        self.thread = threading.Thread(target=self._run, name="GlobalInputPoller", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _pressed(self, vk_code):
        return bool(self.user32.GetAsyncKeyState(vk_code) & 0x8000)

    def _run(self):
        while not self.stop_event.is_set():
            now = time.monotonic()
            current_keys = {code for code in self.key_codes if self._pressed(code)}
            fresh_keys = current_keys - self.previous_keys
            if fresh_keys:
                self.events.put_nowait(("key", min(fresh_keys), now))
            self.previous_keys = current_keys

            mouse_state = {
                "left": self._pressed(self.VK_LBUTTON),
                "right": self._pressed(self.VK_RBUTTON),
            }
            for button, pressed in mouse_state.items():
                if pressed != self.previous_mouse[button]:
                    event_name = "mouse_down" if pressed else "mouse_up"
                    self.events.put_nowait((event_name, button, now))
            self.previous_mouse = mouse_state
            time.sleep(0.02)


class PetApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Keyboard Pet")
        self.root.configure(bg=TRANSPARENT)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT)

        self.settings = self._load_settings()
        self.size_name = self.settings.get("size", "normal")
        if self.size_name not in SIZES:
            self.size_name = "normal"
        self.pet_frames = self._load_pet_frames()
        self.top_pad = 10
        self.side_pad = 6
        self.frame = 0
        self.current_image = self._choose_image()
        self._refresh_dimensions()
        self.window_x = None
        self.window_y = None

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=TRANSPARENT,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.events = queue.Queue()
        self.input_poller = GlobalInputPoller(self.events)
        self.typing_until = 0.0
        self.type_started_at = 0.0
        self.type_key_index = 0
        self.previous_type_key_index = -1
        self.mouse_down = {"left": False, "right": False}
        self.click_until = 0.0
        self.click_started_at = 0.0
        self.last_click_button = "left"
        self.pet_until = 0.0
        self.pet_started_at = 0.0
        self.last_activity_at = time.monotonic()
        self.last_blink_at = self.last_activity_at + 2.0
        self.blink_started_at = 0.0
        self.next_blink_in = random.uniform(3.0, 6.0)
        self.recent_key_times = []
        self.encourage_until = 0.0
        self.encourage_text = ""
        self.previous_encourage_text = ""
        self.last_encourage_at = 0.0
        self.hovering = False
        self.hover_started_at = 0.0
        self.last_hovering = False
        self.last_avoid_save_at = 0.0
        self.last_sound_at = 0.0
        self.drag_offset = (0, 0)
        self.key_bursts = []
        self.always_on_top = tk.BooleanVar(value=bool(self.settings.get("topmost", True)))
        self.sound_enabled = tk.BooleanVar(value=bool(self.settings.get("sound", False)))
        self.avoid_enabled = tk.BooleanVar(value=bool(self.settings.get("avoid_mouse", True)))
        self.reminders_enabled = tk.BooleanVar(value=bool(self.settings.get("reminders", True)))
        self.startup_enabled = tk.BooleanVar(value=startup_enabled())
        self.root.attributes("-topmost", self.always_on_top.get())
        self.tray_icon = None
        now = time.monotonic()
        self.next_water_reminder_at = now + float(self.settings.get("water_reminder_remaining", WATER_REMINDER_SECONDS))
        self.next_move_reminder_at = now + float(self.settings.get("move_reminder_remaining", MOVE_REMINDER_SECONDS))
        self.active_reminder = None
        self.reminder_window = None
        self.reminder_auto_close_id = None
        self.word_banks = self._load_word_banks()
        self.vocab_bank_id = self.settings.get("vocab_bank", DEFAULT_VOCAB_BANK)
        if self.vocab_bank_id not in self.word_banks:
            self.vocab_bank_id = next(iter(self.word_banks), DEFAULT_VOCAB_BANK)
        self.vocab_progress = self.settings.get("vocab_progress", {})
        if not isinstance(self.vocab_progress, dict):
            self.vocab_progress = {}
        self.vocab_window = None
        self.current_vocab_word = None
        self.current_vocab_answer_visible = True
        self.vocab_vars = {}

        self._make_menu()
        self._bind_window()
        self._restore_or_place_default()

    def run(self):
        self.input_poller.start()
        self._start_tray()
        self.root.after(30, self._tick)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()

    def close(self):
        self.input_poller.stop()
        self._save_settings()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.destroy()

    def _load_settings(self):
        path = config_path()
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
        return {}

    def _save_settings(self):
        path = config_path()
        payload = {
            "size": self.size_name,
            "topmost": self.always_on_top.get(),
            "sound": self.sound_enabled.get(),
            "avoid_mouse": self.avoid_enabled.get(),
            "reminders": self.reminders_enabled.get(),
            "water_reminder_remaining": max(1, int(self.next_water_reminder_at - time.monotonic())),
            "move_reminder_remaining": max(1, int(self.next_move_reminder_at - time.monotonic())),
            "vocab_bank": self.vocab_bank_id,
            "vocab_progress": self.vocab_progress,
            "x": self.window_x if self.window_x is not None else self.root.winfo_x(),
            "y": self.window_y if self.window_y is not None else self.root.winfo_y(),
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _make_menu(self):
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="迷你大小", command=lambda: self._set_size("mini"))
        self.menu.add_command(label="小一点", command=lambda: self._set_size("small"))
        self.menu.add_command(label="正常大小", command=lambda: self._set_size("normal"))
        self.menu.add_command(label="大一点", command=lambda: self._set_size("large"))
        self.menu.add_separator()
        self.menu.add_checkbutton(
            label="置顶显示",
            variable=self.always_on_top,
            command=self._toggle_topmost,
        )
        self.menu.add_checkbutton(
            label="开机启动",
            variable=self.startup_enabled,
            command=self._toggle_startup,
        )
        self.menu.add_checkbutton(
            label="音效",
            variable=self.sound_enabled,
            command=self._toggle_sound,
        )
        self.menu.add_checkbutton(
            label="避让鼠标",
            variable=self.avoid_enabled,
            command=self._toggle_avoid,
        )
        self.menu.add_checkbutton(
            label="健康提醒",
            variable=self.reminders_enabled,
            command=self._toggle_reminders,
        )
        self.menu.add_command(label="摸鱼背单词", command=self._open_vocab_window)
        self.menu.add_command(label="回到右下角", command=self._place_default)
        self.menu.add_separator()
        self.menu.add_command(label="退出", command=self.close)

    def _start_tray(self):
        if not pystray or not Image:
            return
        icon_path = skin_path("panda_pet_normal_idle.png")
        try:
            icon_image = Image.open(icon_path).convert("RGBA")
        except OSError:
            return

        def after(callback):
            return lambda icon=None, item=None: self.root.after(0, callback)

        menu = pystray.Menu(
            pystray.MenuItem("显示/隐藏", after(self._toggle_visible)),
            pystray.MenuItem(
                "大小",
                pystray.Menu(
                    pystray.MenuItem("迷你大小", after(lambda: self._set_size("mini"))),
                    pystray.MenuItem("小一点", after(lambda: self._set_size("small"))),
                    pystray.MenuItem("正常大小", after(lambda: self._set_size("normal"))),
                    pystray.MenuItem("大一点", after(lambda: self._set_size("large"))),
                ),
            ),
            pystray.MenuItem("置顶显示", after(self._toggle_topmost_from_tray)),
            pystray.MenuItem("开机启动", after(self._toggle_startup_from_tray)),
            pystray.MenuItem("音效", after(self._toggle_sound_from_tray)),
            pystray.MenuItem("避让鼠标", after(self._toggle_avoid_from_tray)),
            pystray.MenuItem("健康提醒", after(self._toggle_reminders_from_tray)),
            pystray.MenuItem("摸鱼背单词", after(self._open_vocab_window)),
            pystray.MenuItem("回到右下角", after(self._place_default)),
            pystray.MenuItem("退出", after(self.close)),
        )
        self.tray_icon = pystray.Icon(APP_NAME, icon_image, "熊猫键盘手", menu)
        self.tray_icon.run_detached()

    def _bind_window(self):
        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._drag)
        self.root.bind("<ButtonRelease-1>", self._end_drag)
        self.root.bind("<Button-3>", self._show_menu)
        self.root.bind("<KeyPress>", lambda event: self._mark_typing())

    def _place_default(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, screen_w - self.width - 42)
        y = max(0, screen_h - self.height - 82)
        self.window_x = x
        self.window_y = y
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self._save_settings()

    def _restore_or_place_default(self):
        x = self.window_x if self.window_x is not None else self.settings.get("x")
        y = self.window_y if self.window_y is not None else self.settings.get("y")
        if isinstance(x, int) and isinstance(y, int):
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            x = min(max(0, x), max(0, screen_w - self.width))
            y = min(max(0, y), max(0, screen_h - self.height))
            self.window_x = x
            self.window_y = y
            self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
            return
        self._place_default()

    def _set_size(self, name):
        self.size_name = name
        self.current_image = self._choose_image()
        self._refresh_dimensions()
        self.canvas.configure(width=self.width, height=self.height)
        self._restore_or_place_default()
        self._save_settings()

    def _refresh_dimensions(self):
        self.image_w = self.current_image.width()
        self.image_h = self.current_image.height()
        self.asset_scale = self.image_w / 310
        self.width = self.image_w + self.side_pad * 2
        self.height = self.image_h + self.top_pad + 8

    def _load_pet_frames(self):
        sizes = SIZES
        animations = {
            "idle": ("idle_0",),
            "blink": tuple(f"blink_{index}" for index in range(5)),
            "sleep": tuple(f"sleep_{index}" for index in range(6)),
            "pet": tuple(f"pet_{index}" for index in range(6)),
            "hover": tuple(f"hover_{index}" for index in range(6)),
            "mouse_left": tuple(f"mouse_left_{index}" for index in range(6)),
            "mouse_right": tuple(f"mouse_right_{index}" for index in range(6)),
        }
        type_key_count = 10
        frames = {}
        try:
            for size in sizes:
                frames[size] = {}
                for animation, names in animations.items():
                    frames[size][animation] = []
                    fallback_path = skin_path(f"panda_pet_{size}.png")
                    for name in names:
                        frame_path = skin_path(f"panda_pet_{size}_{name}.png")
                        path = frame_path if frame_path.exists() else fallback_path
                        frames[size][animation].append(tk.PhotoImage(file=path))
                frames[size]["type"] = []
                for key_index in range(type_key_count):
                    key_frames = []
                    for frame_index in range(6):
                        frame_path = resource_path(
                            "assets",
                            "skins",
                            "panda",
                            f"panda_pet_{size}_type_key{key_index}_{frame_index}.png",
                        )
                        fallback_path = skin_path(f"panda_pet_{size}_type_{frame_index}.png")
                        path = frame_path if frame_path.exists() else fallback_path
                        key_frames.append(tk.PhotoImage(file=path))
                    frames[size]["type"].append(key_frames)
        except tk.TclError as exc:
            messagebox.showerror("资源加载失败", f"找不到熊猫宠物图片：\n{exc}")
            raise
        return frames

    def _load_word_banks(self):
        path = vocab_path("word_banks.json")
        try:
            with path.open("r", encoding="utf-8") as file:
                banks = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(banks, dict):
            return {}
        clean_banks = {}
        for bank_id, bank in banks.items():
            if not isinstance(bank, dict):
                continue
            words = bank.get("words", [])
            if not isinstance(words, list):
                continue
            clean_words = []
            for item in words:
                if isinstance(item, dict) and item.get("word") and item.get("meaning"):
                    clean_words.append(item)
            if clean_words:
                clean_banks[bank_id] = {
                    "label": bank.get("label", bank_id),
                    "words": clean_words,
                }
        return clean_banks

    def _toggle_topmost(self):
        self.root.attributes("-topmost", self.always_on_top.get())
        self._save_settings()

    def _toggle_topmost_from_tray(self):
        self.always_on_top.set(not self.always_on_top.get())
        self._toggle_topmost()

    def _toggle_startup(self):
        set_startup_enabled(self.startup_enabled.get())
        self._save_settings()

    def _toggle_startup_from_tray(self):
        self.startup_enabled.set(not self.startup_enabled.get())
        self._toggle_startup()

    def _toggle_sound(self):
        self._save_settings()
        self._play_sound("pet")

    def _toggle_sound_from_tray(self):
        self.sound_enabled.set(not self.sound_enabled.get())
        self._toggle_sound()

    def _toggle_avoid(self):
        self._save_settings()

    def _toggle_avoid_from_tray(self):
        self.avoid_enabled.set(not self.avoid_enabled.get())
        self._toggle_avoid()

    def _toggle_reminders(self):
        now = time.monotonic()
        if self.reminders_enabled.get():
            self.next_water_reminder_at = now + WATER_REMINDER_SECONDS
            self.next_move_reminder_at = now + MOVE_REMINDER_SECONDS
        else:
            self._close_reminder()
        self._save_settings()

    def _toggle_reminders_from_tray(self):
        self.reminders_enabled.set(not self.reminders_enabled.get())
        self._toggle_reminders()

    def _toggle_visible(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.root.attributes("-topmost", self.always_on_top.get())
        else:
            self.root.withdraw()

    def _open_vocab_window(self):
        if self.vocab_window and self.vocab_window.winfo_exists():
            self.vocab_window.deiconify()
            self.vocab_window.lift()
            return
        if not self.word_banks:
            messagebox.showwarning("摸鱼背单词", "没有找到可用词库。")
            return

        window = tk.Toplevel(self.root)
        self.vocab_window = window
        window.title("摸鱼背单词")
        window.attributes("-topmost", True)
        window.resizable(False, False)
        window.configure(bg="#f8fafc")
        window.protocol("WM_DELETE_WINDOW", self._close_vocab_window)

        frame = tk.Frame(window, bg="#f8fafc", padx=14, pady=12)
        frame.pack(fill="both", expand=True)

        self.vocab_vars = {
            "bank": tk.StringVar(value=self.word_banks[self.vocab_bank_id]["label"]),
            "word": tk.StringVar(value=""),
            "phonetic": tk.StringVar(value=""),
            "meaning": tk.StringVar(value=""),
            "example": tk.StringVar(value=""),
            "progress": tk.StringVar(value=""),
        }

        bank_labels = [self.word_banks[bank_id]["label"] for bank_id in self.word_banks]
        bank_combo = ttk.Combobox(
            frame,
            textvariable=self.vocab_vars["bank"],
            values=bank_labels,
            width=18,
            state="readonly",
        )
        bank_combo.grid(row=0, column=0, columnspan=3, sticky="ew")
        bank_combo.bind("<<ComboboxSelected>>", self._on_vocab_bank_changed)

        tk.Label(
            frame,
            textvariable=self.vocab_vars["word"],
            bg="#f8fafc",
            fg="#0f172a",
            font=("Segoe UI", 18, "bold"),
            pady=6,
        ).grid(row=1, column=0, columnspan=3, sticky="ew")
        tk.Label(
            frame,
            textvariable=self.vocab_vars["phonetic"],
            bg="#f8fafc",
            fg="#64748b",
            font=("Segoe UI", 10),
        ).grid(row=2, column=0, columnspan=3, sticky="ew")
        tk.Label(
            frame,
            textvariable=self.vocab_vars["meaning"],
            bg="#f8fafc",
            fg="#9a3412",
            font=("Microsoft YaHei UI", 10, "bold"),
            wraplength=260,
            justify="center",
            pady=5,
        ).grid(row=3, column=0, columnspan=3, sticky="ew")
        tk.Label(
            frame,
            textvariable=self.vocab_vars["example"],
            bg="#f8fafc",
            fg="#334155",
            font=("Segoe UI", 9),
            wraplength=260,
            justify="center",
            pady=4,
        ).grid(row=4, column=0, columnspan=3, sticky="ew")
        tk.Label(
            frame,
            textvariable=self.vocab_vars["progress"],
            bg="#f8fafc",
            fg="#64748b",
            font=("Microsoft YaHei UI", 8),
        ).grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 6))

        tk.Button(frame, text="不认识", command=lambda: self._rate_vocab(False), width=8).grid(row=6, column=0, padx=3)
        tk.Button(frame, text="下一个", command=self._next_vocab_word, width=8).grid(row=6, column=1, padx=3)
        tk.Button(frame, text="认识", command=lambda: self._rate_vocab(True), width=8).grid(row=6, column=2, padx=3)
        tk.Button(frame, text="显示/隐藏释义", command=self._toggle_vocab_answer, width=26).grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )

        self._next_vocab_word()
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        current_x, current_y = self._current_window_position()
        x = max(0, current_x - width - 14)
        y = max(0, current_y)
        if x == 0:
            x = min(window.winfo_screenwidth() - width, current_x + self.width + 14)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _close_vocab_window(self):
        if self.vocab_window:
            try:
                self.vocab_window.destroy()
            except tk.TclError:
                pass
            self.vocab_window = None
        self._save_settings()

    def _on_vocab_bank_changed(self, event=None):
        label = self.vocab_vars["bank"].get()
        for bank_id, bank in self.word_banks.items():
            if bank["label"] == label:
                self.vocab_bank_id = bank_id
                break
        self._save_settings()
        self._next_vocab_word()

    def _vocab_record(self, bank_id, word):
        bank_progress = self.vocab_progress.setdefault(bank_id, {})
        return bank_progress.setdefault(
            word,
            {"known": 0, "missed": 0, "seen": 0, "streak": 0, "last": 0},
        )

    def _pick_vocab_word(self):
        words = self.word_banks[self.vocab_bank_id]["words"]
        scored = []
        for item in words:
            record = self._vocab_record(self.vocab_bank_id, item["word"])
            score = record.get("known", 0) - record.get("missed", 0) * 2 + record.get("streak", 0)
            scored.append((score, random.random(), item))
        scored.sort(key=lambda value: (value[0], value[1]))
        pool_size = max(3, min(len(scored), len(scored) // 2 or 1))
        return random.choice(scored[:pool_size])[2]

    def _next_vocab_word(self):
        if not self.word_banks:
            return
        self.current_vocab_word = self._pick_vocab_word()
        self.current_vocab_answer_visible = True
        self._refresh_vocab_card()

    def _refresh_vocab_card(self):
        if not self.current_vocab_word or not self.vocab_vars:
            return
        item = self.current_vocab_word
        record = self._vocab_record(self.vocab_bank_id, item["word"])
        total = len(self.word_banks[self.vocab_bank_id]["words"])
        learned = sum(
            1
            for data in self.vocab_progress.get(self.vocab_bank_id, {}).values()
            if data.get("known", 0) > data.get("missed", 0)
        )
        self.vocab_vars["word"].set(item.get("word", ""))
        self.vocab_vars["phonetic"].set(item.get("phonetic", ""))
        if self.current_vocab_answer_visible:
            self.vocab_vars["meaning"].set(item.get("meaning", ""))
            self.vocab_vars["example"].set(item.get("example", ""))
        else:
            self.vocab_vars["meaning"].set("点击“显示/隐藏释义”查看答案")
            self.vocab_vars["example"].set("")
        self.vocab_vars["progress"].set(
            f"{self.word_banks[self.vocab_bank_id]['label']} · 已掌握 {learned}/{total} · 当前见过 {record.get('seen', 0)} 次"
        )

    def _toggle_vocab_answer(self):
        self.current_vocab_answer_visible = not self.current_vocab_answer_visible
        self._refresh_vocab_card()

    def _rate_vocab(self, known):
        if not self.current_vocab_word:
            return
        record = self._vocab_record(self.vocab_bank_id, self.current_vocab_word["word"])
        record["seen"] = record.get("seen", 0) + 1
        record["last"] = int(time.time())
        if known:
            record["known"] = record.get("known", 0) + 1
            record["streak"] = record.get("streak", 0) + 1
            self.encourage_text = "记住啦"
        else:
            record["missed"] = record.get("missed", 0) + 1
            record["streak"] = 0
            self.encourage_text = "再看一眼"
        self.encourage_until = time.monotonic() + 1.6
        self._save_settings()
        self._next_vocab_word()

    def _current_window_position(self):
        x = self.window_x if self.window_x is not None else self.root.winfo_x()
        y = self.window_y if self.window_y is not None else self.root.winfo_y()
        return x, y

    def _start_drag(self, event):
        self._mark_pet()
        self._mark_mouse("left", True)
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())

    def _drag(self, event):
        dx, dy = self.drag_offset
        self.window_x = event.x_root - dx
        self.window_y = event.y_root - dy
        self.root.geometry(f"+{self.window_x}+{self.window_y}")

    def _end_drag(self, event):
        self._mark_mouse("left", False)
        self.window_x = self.root.winfo_x()
        self.window_y = self.root.winfo_y()
        self._save_settings()

    def _show_menu(self, event):
        self._mark_mouse("right", True)
        self.menu.tk_popup(event.x_root, event.y_root)

    def _mark_typing(self, vk_code=0):
        now = time.monotonic()
        if now < self.typing_until - 0.12:
            return
        self.typing_until = now + 0.32
        self.type_started_at = now
        self.last_activity_at = now
        self._play_sound("key")
        key_count = len(self.pet_frames[self.size_name]["type"])
        next_key = random.randrange(key_count)
        if key_count > 1 and next_key == self.previous_type_key_index:
            next_key = (next_key + random.randrange(1, key_count)) % key_count
        self.type_key_index = next_key
        self.previous_type_key_index = next_key
        self.key_bursts.append(now)
        self.key_bursts = [item for item in self.key_bursts if now - item < 0.45]
        self.recent_key_times.append(now)
        self.recent_key_times = [item for item in self.recent_key_times if now - item < 10.0]
        if len(self.recent_key_times) >= 14 and now - self.last_encourage_at > 8.0:
            messages = ("加油", "写得好快", "很稳", "注意休息", "继续冲", "手感来了")
            candidates = [message for message in messages if message != self.previous_encourage_text]
            self.encourage_text = random.choice(candidates)
            self.previous_encourage_text = self.encourage_text
            self.encourage_until = now + 2.8
            self.last_encourage_at = now

    def _mark_mouse(self, button, pressed):
        now = time.monotonic()
        self.mouse_down[button] = pressed
        if pressed:
            self.last_activity_at = now
            self.last_click_button = button
            self.click_started_at = now
            self.click_until = now + 0.30
            self._play_sound("mouse")

    def _mark_pet(self):
        now = time.monotonic()
        self.pet_started_at = now
        self.pet_until = now + 0.62
        self.last_activity_at = now
        self._play_sound("pet")

    def _play_sound(self, kind):
        if not self.sound_enabled.get() or not winsound:
            return
        now = time.monotonic()
        if now - self.last_sound_at < 0.08:
            return
        self.last_sound_at = now
        tones = {
            "key": (880, 22),
            "mouse": (620, 28),
            "pet": (1046, 36),
        }
        frequency, duration = tones.get(kind, tones["pet"])
        threading.Thread(
            target=lambda: winsound.Beep(frequency, duration),
            name="PetSound",
            daemon=True,
        ).start()

    def _tick(self):
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break

            if event[0] == "key":
                self._mark_typing(event[1])
            elif event[0] == "mouse_down":
                self._mark_mouse(event[1], True)
            elif event[0] == "mouse_up":
                self._mark_mouse(event[1], False)
            elif event[0] == "input_error":
                self._show_input_error(event[1])

        self._update_hover_state()
        self._avoid_pointer()
        self._check_reminders()
        self.frame += 1
        self._draw()
        self.root.after(30, self._tick)

    def _check_reminders(self):
        if not self.reminders_enabled.get() or self.reminder_window is not None:
            return
        now = time.monotonic()
        if now >= self.next_move_reminder_at:
            self._show_reminder("move")
        elif now >= self.next_water_reminder_at:
            self._show_reminder("water")

    def _show_reminder(self, kind):
        self.active_reminder = kind
        if kind == "water":
            title = "喝水提醒"
            message = "已经半小时啦，记得喝口水。"
            self.next_water_reminder_at = time.monotonic() + WATER_REMINDER_SECONDS
        else:
            title = "活动提醒"
            message = "已经一小时啦，起来活动一下身体。"
            now = time.monotonic()
            self.next_move_reminder_at = now + MOVE_REMINDER_SECONDS
            self.next_water_reminder_at = max(self.next_water_reminder_at, now + 5)

        self._save_settings()
        self._play_sound("pet")
        window = tk.Toplevel(self.root)
        self.reminder_window = window
        window.title(title)
        window.attributes("-topmost", True)
        window.resizable(False, False)
        window.configure(bg="#fff7ed")
        window.protocol("WM_DELETE_WINDOW", self._close_reminder)

        frame = tk.Frame(window, bg="#fff7ed", padx=18, pady=14)
        frame.pack(fill="both", expand=True)
        tk.Label(
            frame,
            text=title,
            bg="#fff7ed",
            fg="#9a3412",
            font=("Microsoft YaHei UI", 12, "bold"),
        ).pack(anchor="w")
        tk.Label(
            frame,
            text=message,
            bg="#fff7ed",
            fg="#334155",
            font=("Microsoft YaHei UI", 10),
            pady=8,
        ).pack(anchor="w")
        tk.Button(
            frame,
            text="确认",
            command=self._close_reminder,
            font=("Microsoft YaHei UI", 9),
            width=9,
        ).pack(anchor="e", pady=(4, 0))

        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()
        x = max(0, screen_w - width - 40)
        y = max(0, screen_h - height - self.height - 110)
        window.geometry(f"{width}x{height}+{x}+{y}")
        self.reminder_auto_close_id = self.root.after(REMINDER_POPUP_SECONDS * 1000, self._close_reminder)

    def _close_reminder(self):
        if self.reminder_auto_close_id:
            self.root.after_cancel(self.reminder_auto_close_id)
            self.reminder_auto_close_id = None
        if self.reminder_window:
            try:
                self.reminder_window.destroy()
            except tk.TclError:
                pass
            self.reminder_window = None
        self.active_reminder = None

    def _update_hover_state(self):
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        x1, y1 = self._current_window_position()
        inside = x1 <= pointer_x <= x1 + self.width and y1 <= pointer_y <= y1 + self.height
        self.hovering = inside and not any(self.mouse_down.values())
        if self.hovering and not self.last_hovering:
            self.hover_started_at = time.monotonic()
            self.last_activity_at = self.hover_started_at
        self.last_hovering = self.hovering

    def _avoid_pointer(self):
        if not self.avoid_enabled.get() or any(self.mouse_down.values()):
            return
        now = time.monotonic()
        if not self.hovering or now - self.hover_started_at < 0.75:
            return
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        current_x, current_y = self._current_window_position()
        center_x = current_x + self.width / 2
        center_y = current_y + self.height / 2
        dx = center_x - pointer_x
        dy = center_y - pointer_y
        length = max(1.0, math.hypot(dx, dy))
        step = 5
        new_x = int(current_x + dx / length * step)
        new_y = int(current_y + dy / length * step)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.window_x = min(max(0, new_x), max(0, screen_w - self.width))
        self.window_y = min(max(0, new_y), max(0, screen_h - self.height))
        self.root.geometry(f"+{self.window_x}+{self.window_y}")
        if now - self.last_avoid_save_at > 1.0:
            self.last_avoid_save_at = now
            self._save_settings()

    def _show_input_error(self, detail):
        messagebox.showwarning(
            "全局输入监听没有启动",
            "当前只支持 Windows 全局输入监听。窗口获得焦点时仍可预览键盘动画。\n\n"
            f"错误信息：{detail}",
        )

    def _active_animation(self):
        now = time.monotonic()
        if now < self.pet_until:
            return "pet"
        if self.mouse_down["left"] or (now < self.click_until and self.last_click_button == "left"):
            return "mouse_left"
        if self.mouse_down["right"] or (now < self.click_until and self.last_click_button == "right"):
            return "mouse_right"
        if now < self.typing_until:
            return "type"
        if self.hovering and now - self.last_activity_at < 10.0:
            return "hover"
        if now - self.last_activity_at > 18.0:
            return "sleep"
        if now - self.last_blink_at > self.next_blink_in:
            self.blink_started_at = now
            self.last_blink_at = now
            self.next_blink_in = random.uniform(3.0, 6.0)
        if now - self.blink_started_at < 0.25:
            return "blink"
        return "idle"

    def _animation_index(self, animation):
        if animation == "type":
            elapsed = max(0.0, time.monotonic() - self.type_started_at)
            frame_count = len(self.pet_frames[self.size_name][animation][self.type_key_index])
            return min(
                int(elapsed / 0.052),
                frame_count - 1,
            )
        if animation.startswith("mouse"):
            elapsed = max(0.0, time.monotonic() - self.click_started_at)
            return min(int(elapsed / 0.050), len(self.pet_frames[self.size_name][animation]) - 1)
        if animation == "pet":
            elapsed = max(0.0, time.monotonic() - self.pet_started_at)
            return min(int(elapsed / 0.070), len(self.pet_frames[self.size_name][animation]) - 1)
        if animation == "blink":
            elapsed = max(0.0, time.monotonic() - self.blink_started_at)
            return min(int(elapsed / 0.050), len(self.pet_frames[self.size_name][animation]) - 1)
        if animation == "sleep":
            return (self.frame // 18) % len(self.pet_frames[self.size_name][animation])
        if animation == "hover":
            elapsed = max(0.0, time.monotonic() - self.hover_started_at)
            return int(elapsed / 0.080) % len(self.pet_frames[self.size_name][animation])
        return 0

    def _choose_image(self):
        animation = self._active_animation() if hasattr(self, "typing_until") else "idle"
        if animation == "type":
            return self.pet_frames[self.size_name][animation][self.type_key_index][0]
        return self.pet_frames[self.size_name][animation][0]

    def _draw(self):
        animation = self._active_animation()
        frame_index = self._animation_index(animation)
        if animation == "type":
            self.current_image = self.pet_frames[self.size_name][animation][self.type_key_index][frame_index]
        else:
            self.current_image = self.pet_frames[self.size_name][animation][frame_index]

        typing = animation == "type"
        clicking = animation.startswith("mouse")
        lift = 0
        if typing:
            lift = math.sin(self.frame / 2.8) * 2.0
        elif clicking:
            lift = 1.5
        else:
            lift = math.sin(self.frame / 18) * 0.8

        self.canvas.delete("all")
        self.canvas.create_image(self.width / 2, self.top_pad + lift, image=self.current_image, anchor="n")
        self._draw_gaze()
        self._draw_encouragement()

    def _draw_gaze(self):
        if self._active_animation() != "idle":
            return
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        current_x, current_y = self._current_window_position()
        center_x = current_x + self.width / 2
        center_y = current_y + self.height * 0.42
        dx = max(-1.0, min(1.0, (pointer_x - center_x) / 240))
        dy = max(-1.0, min(1.0, (pointer_y - center_y) / 180))
        s = self.asset_scale
        offset_x = dx * 3.2 * s
        offset_y = dy * 2.4 * s
        image_x = self.side_pad
        image_y = self.top_pad
        for eye_x, eye_y in ((99, 143), (208, 143)):
            x = image_x + eye_x * s + offset_x
            y = image_y + eye_y * s + offset_y
            self.canvas.create_oval(
                x - 2.2 * s,
                y - 2.2 * s,
                x + 2.2 * s,
                y + 2.2 * s,
                fill="#ffffff",
                outline="",
            )

    def _draw_encouragement(self):
        if time.monotonic() >= self.encourage_until:
            return
        text = self.encourage_text
        font_size = max(8, int(10 * self.asset_scale))
        x = self.width / 2
        y = 9
        bubble_w = max(38, len(text) * font_size + 16)
        bubble_h = 19
        self.canvas.create_rectangle(
            x - bubble_w / 2,
            y - bubble_h / 2,
            x + bubble_w / 2,
            y + bubble_h / 2,
            fill="#fff7ed",
            outline="#f59e0b",
            width=1,
        )
        self.canvas.create_text(
            x,
            y,
            text=text,
            fill="#9a3412",
            font=("Microsoft YaHei UI", font_size, "bold"),
        )


def main():
    instance = SingleInstance()
    if not instance.acquire():
        return
    app = PetApp()
    try:
        app.run()
    finally:
        instance.release()


if __name__ == "__main__":
    main()
