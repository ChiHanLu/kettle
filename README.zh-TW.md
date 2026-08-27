# claude-sounds

[English](README.md) · **繁體中文** · [简体中文](README.zh-CN.md)

在值得你注意的時刻，Claude Code 會出聲 —— 講完了、要跟你要權限、等你太久、
或者被 API 限流整輪直接掛掉。每個事件都能獨立開關。裝好之後預設全靜音，你不開它就不吵。

macOS · Windows · Linux。零相依套件，只用作業系統本來就有的東西。

![claude-sounds demo](assets/demo.gif)

*GIF 沒有聲音 —— [**點這裡看有聲音的版本**](assets/demo.mp4)（22 秒），聲音才是重點。*

---

## 安裝

```bash
claude plugin marketplace add https://github.com/ChiHanLu/claude-sounds
claude plugin install claude-sounds@claude-sounds --scope user
```

或先 clone 下來裝本機版：

```bash
git clone https://github.com/ChiHanLu/claude-sounds
claude plugin marketplace add ./claude-sounds
claude plugin install claude-sounds@claude-sounds --scope user
```

重開 Claude Code。**它是故意裝成靜音的** —— 總開關預設為關。

---

## 30 秒上手

在 Claude Code 裡面，全部都是 `/sounds`：

```
/sounds on            打開（建議組：講完、要權限、閒置、子 agent、出錯）
/sounds               看現在誰對到誰
/sounds test          馬上全部聽一遍
/sounds off           全部安靜
```

你也可以直接用講的：「完成音小聲一點」、「晚上十點以後不要吵」、
「出事的時候用講的」—— Claude 會自己翻成對應指令。

也可以完全不透過 Claude，直接在終端機跑：

```bash
python3 ~/.claude/plugins/cache/claude-sounds/claude-sounds/*/skills/sounds/scripts/sounds.py
```

---

## 指令

```
sounds                      全貌：總開關、音量、靜音時段、每個事件的狀態
sounds on | off             總開關
sounds on stop | off stop   只開/關單一事件

sounds stop done            設定音效
sounds stop done,up         逗號 = 每次隨機挑一個
sounds stop 說:好了          用講的取代音效（say: / 說: / 说: 都認）
sounds stop ~/x/ding.mp3    直接指檔案路徑
sounds stop off             等同 `sounds off stop`

sounds test [event]         照現在的設定實際播一次（所有規則照跑）
sounds list                 這台機器上所有叫得出名字的音效
sounds volume 0.3 [event]   全域音量，或只調某一個事件
sounds quiet 22:00-09:00    靜音時段（跨半夜也算得對）
sounds quiet off
sounds focus on | off       終端機在最前面時就閉嘴
sounds preset               回到建議組
sounds preset off           所有事件全關
```

**沒有 `set` 這個字**。`sounds <事件> <音效>` 本身就是設定。
事件名稱和音效名稱是兩組完全不重疊的命名空間，所以永遠不會搞混。

---

## 事件

| 名稱 | hook 事件 | 什麼時候響 | 建議組 |
|---|---|---|:-:|
| `stop` | `Stop` | Claude 這輪講完了 | ● |
| `ask` | `Notification:permission_prompt` | 跳出權限詢問 | ● |
| `idle` | `Notification:idle_prompt` | 你太久沒回，Claude 在等 | ● |
| `sub` | `SubagentStop` | 子 agent 收工 | ● |
| `error` | `StopFailure` | 這輪**因 API 錯誤直接死掉** —— 限流、伺服器過載 | ● |
| `fail` | `PostToolUseFailure` | 指令或編輯失敗 | |
| `denied` | `PermissionDenied` | auto mode 擋掉某個工具呼叫 | |
| `compact` | `PreCompact` | context 準備被壓縮 | |
| `start` | `SessionStart` | session 開始（只有 startup，resume 不算） | |
| `end` | `SessionEnd` | session 結束 | |
| `task` | `TaskCompleted` | 背景任務完成 | |

`error` 是大家不會想到要設、但事後最想要的一個：被限流的時候整輪就這樣停住，
沒有聲音的話你會過五分鐘才發現。

---

## 音效

八個可攜別名，同一份設定丟到任何機器都不會壞：

| 別名 | macOS | Windows | Linux |
|---|---|---|---|
| `done` | Glass | chimes | complete |
| `ding` | Ping | Windows Ding | bell |
| `soft` | Pop | Windows Balloon | audio-volume-change |
| `up` | Blow | Windows Notify | dialog-information |
| `alert` | Funk | Windows Notify System Generic | message-new-instant |
| `boom` | Basso | Windows Critical Stop | dialog-warning |
| `hmm` | Purr | Windows Background | window-question |
| `down` | Sosumi | Windows Exclamation | dialog-error |

每個別名在各平台都準備了好幾個備援檔名，所以某個 Windows 版本少了某個檔也不會變成無聲。

當然也可以直接指定系統音效原名 —— `sounds stop Glass`、`sounds stop tada`。
`sounds list` 會列出全部可用的。

### 加入自己的音效

把檔案丟進 `~/.claude/sounds/` 就好，支援 `.wav` `.mp3` `.aiff` `.oga` `.m4a` `.flac`。

```bash
cp ~/Downloads/tada.mp3 ~/.claude/sounds/
sounds list          # tada 出現了
sounds stop tada
sounds test stop
```

也可以直接給絕對路徑：`sounds stop ~/Music/whatever.wav`。

---

## 設定檔

`~/.claude/sounds.json`。放在 plugin 外面，所以更新 plugin 不會被洗掉。
**建議一律用 CLI 改**（它會驗證名稱並告訴你哪個找不到），格式長這樣：

```json
{
  "enabled": true,
  "volume": 0.5,
  "quiet_hours": "22:00-09:00",
  "only_when_unfocused": false,
  "events": {
    "Stop":                          { "sounds": ["done", "up"] },
    "Notification:permission_prompt": { "sounds": ["alert"] },
    "SubagentStop":                   { "sounds": ["soft"], "volume": 0.3 },
    "StopFailure":                    { "sounds": ["boom"], "say": "被限流了" },
    "PreCompact":                     { "sounds": ["hmm"], "enabled": false }
  }
}
```

- 頂層 `enabled: false` 一律靜音，蓋過所有事件層設定
- `sounds` 有兩個以上 → 每次隨機挑一個
- 事件層的 `volume` 蓋掉全域音量
- `say` 和 `sounds` 可以並存，也可以只留 `say`

---

## 各平台狀況

| | 音效 | 語音 | 音量 |
|---|---|---|---|
| **macOS** | `afplay` | `say` | 支援 |
| **Windows** | PowerShell `MediaPlayer` | `System.Speech` | 支援 |
| **Linux** | 依序找 `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay` / `play` | `spd-say` 或 `espeak` | 除 `aplay` 外都支援 |

**`focus` 只有 macOS 能用。** Windows 要寫 P/Invoke、Wayland 根本沒有取得前景視窗的 API，
所以在這兩個平台上 `sounds focus on` 會直接拒絕你，而不是假裝有效然後默默沒作用。

---

## 疑難排解

**完全沒聲音。** 照順序查：`sounds`（總開關 ON 嗎？那個事件是 `on` 嗎？）→
SOUND 欄位有沒有標 `(!missing)`？→ `sounds test stop` 會直接印出它為什麼沒響 →
`sounds list` 看這台機器實際找得到哪些音效。

**同一個聲音響兩次。** 你的 `~/.claude/settings.json` 裡還留著手寫的
`afplay` / `powershell` hook。plugin hooks 跟你的設定是**合併**不是取代，
把舊的 `"hooks"` 區塊刪掉就好。

**Linux 沒聲音。** `which paplay ffplay mpv aplay`，裝一個就好
（`sudo apt install pulseaudio-utils`）。要語音的話 `sudo apt install speech-dispatcher`。

**Windows 沒聲音。** 確認 PowerShell 叫得到，以及 `C:\Windows\Media\chimes.wav` 存在；
有些 Server 版本根本沒附音效檔，這種情況就自己丟檔案進 `~/.claude/sounds/`。

**裝完之後整個變慢。** 不應該發生：播放是 detach 出去的，hook 約 30 毫秒就回傳。
用 `time python3 .../sounds.py hook Stop` 量一下，超過 200 毫秒請開 issue。

---

## 運作方式

就一支 Python 腳本。Claude Code 的 hook 會呼叫 `sounds.py hook <Event>`，
它讀設定檔、把系統播放器**丟到背景**、然後立刻結束 —— 因為 `Stop` 和 `SubagentStop`
是阻塞式 hook，會等指令回傳才繼續，如果在這裡等音效播完，Claude 每回一句話都會卡住。

自我檢查：`python3 skills/sounds/scripts/sounds.py --selftest`

MIT 授權。
