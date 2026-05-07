# Windows 桌面键盘萌宠 / Windows Keyboard Pet

一只轻量的 Windows 桌面熊猫萌宠。它会悬浮在桌面上，跟随你的键盘和鼠标动作：你敲键盘时它也会敲键盘，你点击鼠标时它的小鼠标会按下去；空闲时会眨眼、犯困，鼠标靠近时会互动。

A lightweight Windows desktop panda pet. It floats on your desktop and reacts to your input: it types when you type, clicks its mouse when you click, blinks and gets sleepy while idle, and reacts when your cursor hovers over it.

## 功能 / Features

### 中文

- **全局键盘响应**：使用 Windows `GetAsyncKeyState` 轮询全局输入状态，不需要宠物窗口获得焦点。
- **键盘动画**：每次敲击会随机选择一个键，只亮这一颗键，并播放 6 帧按下/回弹动画。
- **鼠标左右键动画**：左键/右键点击会在原图鼠标区域内做按压和高亮，不会跳出额外图层。
- **眼睛跟随鼠标**：待机时熊猫眼神会轻微朝鼠标方向移动。
- **空闲动画**：自动眨眼；长时间没有输入时会进入犯困/睡觉状态。
- **悬停互动**：鼠标放在熊猫身上会触发脸红和轻微挥手动画。
- **摸头互动**：左键点击或拖动熊猫时，会触发摸头、脸红、小闪光动画。
- **轻养成系统**：内置心情、体力、清洁、饱腹、亲密度、等级，状态会随着时间和互动缓慢变化。
- **喂食、洗澡、休息**：可以喂零食恢复饱腹，给熊猫洗澡提升清洁，也可以主动让它休息恢复体力。
- **状态可视化反馈**：脏了、饿了、困了、心情差时，熊猫会有对应的小视觉提示。
- **长时间打字鼓励**：连续输入一段时间后，会偶尔冒出“加油”“写得好快”“注意休息”等小气泡，并避免连续重复同一句。
- **避让鼠标**：默认开启。鼠标停在熊猫身上一小会儿，它会轻轻挪开。
- **系统托盘菜单**：托盘图标提供显示/隐藏、大小、置顶、开机启动、音效、避让鼠标、健康提醒、回到右下角、退出。
- **右键菜单**：在熊猫身上右键可打开常用菜单。
- **可选音效**：默认关闭。开启后，键盘、鼠标、摸头会有短促提示音。
- **健康提醒**：默认开启。每 30 分钟提醒喝水，每 1 小时提醒起身活动；弹窗会保留 1 分钟，点击确认可立即收起。
- **摸鱼背单词**：右键菜单和托盘菜单可打开单词闪卡，支持初中、高中、四级、六级、雅思 5 类内置完整词库，并记录认识/不认识进度。
- **可选开机启动**：使用当前用户 Windows Run 注册表项，不需要管理员权限。
- **记住设置**：自动保存大小、位置、置顶、音效、避让鼠标、健康提醒设置。
- **单实例限制**：重复运行 `run_silent.bat` 不会生成多只熊猫。
- **皮肤/动作包结构**：当前熊猫皮肤放在 `assets\skins\panda`，方便后续扩展其它角色。

### English

- **Global keyboard reaction**: Uses Windows `GetAsyncKeyState`, so the pet reacts even when another app is focused.
- **Keyboard animation**: Each key press randomly picks one key, lights only that key, and plays a 6-frame press/release animation.
- **Mouse click animation**: Left/right clicks animate directly inside the original mouse area, without adding a detached overlay.
- **Mouse-following eyes**: While idle, the panda’s eyes subtly follow the cursor.
- **Idle animation**: The panda blinks automatically and becomes sleepy after a period of inactivity.
- **Hover interaction**: Hovering over the panda triggers a blush and a subtle waving animation.
- **Petting interaction**: Clicking or dragging the panda triggers a petting animation with blush and small sparkles.
- **Light progression system**: Includes mood, energy, cleanliness, fullness, bond, and level, all of which change gradually over time and interaction.
- **Feeding, bathing, and resting**: Feed snacks to restore fullness, bathe the panda to improve cleanliness, or let it rest to recover energy.
- **Visible status feedback**: The panda shows small visual hints when it gets dirty, hungry, sleepy, or unhappy.
- **Typing encouragement**: After sustained typing, the panda occasionally shows short encouragement bubbles.
- **Cursor avoidance**: Enabled by default. If the cursor rests on the panda for a moment, it gently moves away.
- **System tray menu**: The tray icon supports show/hide, size, topmost, startup, sound, cursor avoidance, health reminders, reset position, and exit.
- **Right-click menu**: Right-click the panda to open the common actions menu.
- **Optional sound effects**: Disabled by default. When enabled, typing, clicking, and petting play short beeps.
- **Health reminders**: Enabled by default. Reminds you to drink water every 30 minutes and move around every 1 hour. The popup stays for 1 minute or closes when confirmed.
- **Vocabulary flashcards**: Open from the right-click or tray menu. Includes full built-in banks for junior high, senior high, CET-4, CET-6, and IELTS, with simple known/unknown progress tracking.
- **Optional startup on login**: Uses the current user’s Windows Run registry key. Admin permission is not required.
- **Persistent settings**: Saves size, position, topmost state, sound, cursor avoidance, and health reminder settings.
- **Single-instance lock**: Running `run_silent.bat` repeatedly will not spawn multiple pandas.
- **Skin/action-pack layout**: The current panda skin lives in `assets\skins\panda`, making future skins easier to add.

## 运行 / Run

需要 Python。推荐 Python 3.10 或更高版本。

Python is required. Python 3.10 or newer is recommended.

### 显示命令行窗口 / With Console

双击：

Double-click:

```bat
run.bat
```

### 静默运行 / Silent Mode

双击：

Double-click:

```bat
run_silent.bat
```

`run_silent.bat` 会使用 `pythonw` 启动，不显示命令行窗口。程序带有单实例限制，重复双击不会生成多只熊猫。

`run_silent.bat` starts the app with `pythonw`, so no console window is shown. The app is single-instance, so repeated launches will not create multiple pandas.

## 操作 / Controls

### 中文

- **左键点击熊猫**：摸头互动。
- **左键拖动熊猫**：移动位置。
- **右键点击熊猫**：打开菜单。
- **熊猫状态**：查看当前心情、体力、清洁、饱腹、亲密度和等级。
- **托盘图标**：打开托盘菜单，可显示/隐藏、打开摸鱼背单词、切换健康提醒或退出。
- **鼠标悬停**：触发悬停互动；如果避让鼠标开启，停留一小会儿后熊猫会轻轻移开。

### English

- **Left-click the panda**: Petting interaction.
- **Left-drag the panda**: Move it.
- **Right-click the panda**: Open the menu.
- **Care panel**: View mood, energy, cleanliness, fullness, bond, and level.
- **Tray icon**: Open the tray menu, show/hide, open vocabulary flashcards, toggle health reminders, or exit.
- **Hover the cursor**: Triggers hover interaction; if cursor avoidance is enabled, the panda gently moves away after a short delay.

## 菜单说明 / Menu Items

### 中文

- **迷你大小**：约 `84x108`。
- **小一点**：约 `101x130`。
- **正常大小**：约 `117x150`，默认大小，高度为 150px。
- **大一点**：约 `147x188`。
- **置顶显示**：保持熊猫显示在其它窗口上方。
- **开机启动**：登录 Windows 后自动启动。
- **音效**：开启/关闭短促提示音，默认关闭。
- **避让鼠标**：开启/关闭鼠标靠近时轻微移开，默认开启。
- **健康提醒**：开启/关闭喝水和活动提醒，默认开启。
- **熊猫状态**：打开养成状态面板。
- **喂零食**：提升饱腹，并恢复一点心情和体力。
- **给熊猫洗澡**：打开洗澡窗口，完成后提升清洁、心情和亲密度。
- **让熊猫休息**：打开休息窗口，完成后恢复体力和一点心情。
- **摸鱼背单词**：打开单词闪卡窗口，可选择词库并标记认识/不认识。
- **回到右下角**：把熊猫放回屏幕右下角。
- **退出**：关闭程序和托盘图标。

### English

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
- **Vocabulary**: Open the flashcard window, choose a bank, and mark words as known/unknown.
- **Reset Position**: Move the panda back to the bottom-right corner.
- **Exit**: Close the app and tray icon.

## 设置文件 / Settings File

设置会自动保存到：

Settings are saved automatically to:

```text
%APPDATA%\KeyboardPet\settings.json
```

保存内容包括：

Saved values include:

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

如果位置异常，可以删除这个文件，重新运行后会回到右下角。

If the position becomes incorrect, delete this file and restart the app. It will return to the bottom-right corner.

## 皮肤结构 / Skin Structure

当前熊猫皮肤位于：

The current panda skin is located at:

```text
assets\skins\panda
```

主要资源命名规则：

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

其中：

Where:

- `{size}` 是 `mini`、`small`、`normal`、`large`
- `{frame}` 是动画帧编号
- `{key}` 是键盘随机高亮键位编号

皮肤元信息：

Skin metadata:

```text
assets\skins\panda\skin.json
```

当前程序默认加载 `panda` 皮肤。后续如果要添加更多角色，可以按同样结构创建新的皮肤目录，再扩展 `skin_path()` 或加载配置。

The app currently loads the `panda` skin by default. To add more characters later, create another skin folder with the same structure and extend `skin_path()` or add a skin selector.

## 词库结构 / Vocabulary Banks

内置词库位于：

Built-in word banks are stored at:

```text
assets\vocab\word_banks.json
```

当前提供 5 类内置词库：

The current built-in banks are:

- `junior`: 初中英语库，约 1603 词
- `senior`: 高中英语库，约 3677 词
- `cet4`: 四级词库，约 3849 词
- `cet6`: 六级词库，约 5407 词
- `ielts`: 雅思词库，约 5040 词

每个单词条目格式：

Word item format:

```json
{
  "word": "example",
  "phonetic": "/ɪɡˈzæmpəl/",
  "meaning": "n. 例子",
  "example": "This is an example."
}
```

当前词库从开源项目 **ECDICT** 导入，并按标签筛选生成，许可证为 **MIT**。它们适合本地学习和程序演示，但不应宣称为官方考试机构发布的标准词表。

The current banks are imported from the open-source **ECDICT** project and filtered by tags, under the **MIT** license. They work well for local study and app usage, but should not be described as official exam-authority word lists.

## 打包成 EXE / Build EXE

PowerShell 中运行：

Run in PowerShell:

```powershell
.\build_exe.ps1
```

脚本会创建 `.venv`，安装依赖，并用 PyInstaller 打包：

The script creates `.venv`, installs dependencies, and builds with PyInstaller:

```text
dist\KeyboardPet.exe
```

打包依赖：

Build dependencies:

```text
Pillow
pystray
pyinstaller
```

运行依赖记录在：

Runtime dependencies are listed in:

```text
requirements.txt
```

## 给别人使用 / Sharing With Others

最推荐的方式是直接分发打包好的 `exe`。

The recommended way is to share the packaged `exe`.

打包命令：

Build command:

```powershell
.\build_exe.ps1
```

生成文件：

Generated file:

```text
dist\KeyboardPet.exe
```

如果你要发给别人，建议提供：

If you want to share it with other people, ship:

- `KeyboardPet.exe`
- `RELEASE_NOTES_zh-CN.md`

推荐发布目录结构：

Recommended release layout:

```text
release/
  KeyboardPet.exe
  RELEASE_NOTES_zh-CN.md
```

普通用户不需要安装 Python。

End users do not need to install Python.

## 隐私和安全 / Privacy & Safety

### 中文

- 程序不会读取、保存或上传你输入的文字。
- 全局输入监听只判断“某个键是否被按下”和“鼠标左右键是否按下”。
- 鼓励气泡只根据短时间内的按键次数触发。
- 开机启动只写入当前用户的 Windows Run 注册表项。
- 音效使用 Windows `winsound.Beep`，不需要外部音频文件。

### English

- The app does not read, save, or upload typed text.
- Global input polling only checks whether keys and mouse buttons are currently pressed.
- Encouragement bubbles are triggered only by recent key press counts.
- Startup uses the current user’s Windows Run registry key.
- Sound effects use Windows `winsound.Beep`; no external audio files are required.

## 故障排查 / Troubleshooting

### 中文

- **没有托盘图标**：确认已安装依赖 `pystray` 和 `Pillow`。可运行 `python -m pip install -r requirements.txt`。
- **重复启动没有出现新熊猫**：这是正常行为，程序限制为单实例。
- **熊猫位置不对**：删除 `%APPDATA%\KeyboardPet\settings.json` 后重启。
- **音效没有声音**：确认菜单里已开启音效，并检查系统音量。
- **开机启动没生效**：确认菜单里已勾选开机启动；它写入当前用户注册表，不需要管理员权限。

### English

- **No tray icon**: Make sure `pystray` and `Pillow` are installed. Run `python -m pip install -r requirements.txt`.
- **A second panda does not appear**: This is expected. The app is single-instance.
- **Wrong position**: Delete `%APPDATA%\KeyboardPet\settings.json` and restart.
- **No sound**: Make sure sound is enabled in the menu and check system volume.
- **Startup does not work**: Make sure Startup is checked in the menu. It uses the current user registry key and does not require admin rights.
