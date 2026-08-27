# claude-sounds

[English](README.md) · [繁體中文](README.zh-TW.md) · **简体中文**

在值得你注意的时刻，Claude Code 会发出声音 —— 说完了、要跟你要权限、等你太久，
或者被 API 限流导致整轮直接挂掉。每个事件都能单独开关。装好之后默认全静音，你不开它就不吵。

macOS · Windows · Linux。零依赖，只用操作系统本来就有的东西。

---

## 安装

```bash
claude plugin marketplace add https://github.com/ChiHanLu/claude-sounds
claude plugin install claude-sounds@claude-sounds --scope user
```

或者先 clone 下来装本地版：

```bash
git clone https://github.com/ChiHanLu/claude-sounds
claude plugin marketplace add ./claude-sounds
claude plugin install claude-sounds@claude-sounds --scope user
```

重启 Claude Code。**它是故意装成静音的** —— 总开关默认为关。

---

## 30 秒上手

在 Claude Code 里面，全部都是 `/sounds`：

```
/sounds on            打开（推荐组：说完、要权限、空闲、子 agent、出错）
/sounds               看现在谁对应谁
/sounds test          马上全部听一遍
/sounds off           全部安静
```

你也可以直接用说的：「完成音小声一点」「晚上十点以后别吵」
「出事的时候用语音播报」—— Claude 会自己翻译成对应命令。

也可以完全不经过 Claude，直接在终端里跑：

```bash
python3 ~/.claude/plugins/cache/claude-sounds/claude-sounds/*/skills/sounds/scripts/sounds.py
```

---

## 命令

```
sounds                      全貌：总开关、音量、静音时段、每个事件的状态
sounds on | off             总开关
sounds on stop | off stop   只开/关单个事件

sounds stop done            设置声音
sounds stop done,up         逗号 = 每次随机挑一个
sounds stop 说:好了          用语音代替提示音（say: / 说: / 說: 都认）
sounds stop ~/x/ding.mp3    直接指定文件路径
sounds stop off             等同 `sounds off stop`

sounds test [event]         按当前设置实际播一次（所有规则照跑）
sounds list                 这台机器上所有能叫出名字的声音
sounds volume 0.3 [event]   全局音量，或只调某一个事件
sounds quiet 22:00-09:00    静音时段（跨零点也算得对）
sounds quiet off
sounds focus on | off       终端在最前面时就闭嘴
sounds preset               回到推荐组
sounds preset off           所有事件全关
```

**没有 `set` 这个动词**。`sounds <事件> <声音>` 本身就是赋值。
事件名和声音名是两组完全不重叠的命名空间，所以永远不会有歧义。

---

## 事件

| 名称 | hook 事件 | 什么时候响 | 推荐组 |
|---|---|---|:-:|
| `stop` | `Stop` | Claude 这轮说完了 | ● |
| `ask` | `Notification:permission_prompt` | 弹出权限询问 | ● |
| `idle` | `Notification:idle_prompt` | 你太久没回，Claude 在等 | ● |
| `sub` | `SubagentStop` | 子 agent 收工 | ● |
| `error` | `StopFailure` | 这轮**因 API 错误直接挂掉** —— 限流、服务器过载 | ● |
| `fail` | `PostToolUseFailure` | 命令或编辑失败 | |
| `denied` | `PermissionDenied` | auto mode 拦下某个工具调用 | |
| `compact` | `PreCompact` | 上下文即将被压缩 | |
| `start` | `SessionStart` | 会话开始（仅 startup，resume 不算） | |
| `end` | `SessionEnd` | 会话结束 | |
| `task` | `TaskCompleted` | 后台任务完成 | |

`error` 是大家想不到要设、但事后最想要的一个：被限流时整轮就这么停住，
没有声音的话你会过五分钟才发现。

---

## 声音

八个可移植别名，同一份配置放到任何机器都不会坏：

| 别名 | macOS | Windows | Linux |
|---|---|---|---|
| `done` | Glass | chimes | complete |
| `ding` | Ping | Windows Ding | bell |
| `soft` | Pop | Windows Balloon | audio-volume-change |
| `up` | Blow | Windows Notify | dialog-information |
| `alert` | Funk | Windows Notify System Generic | message-new-instant |
| `boom` | Basso | Windows Critical Stop | dialog-warning |
| `hmm` | Purr | Windows Background | window-question |
| `down` | Sosumi | Windows Exclamation | dialog-error |

每个别名在各平台都准备了几个备选文件名，所以某个 Windows 版本缺了某个文件也不会变成无声。

当然也可以直接写系统声音原名 —— `sounds stop Glass`、`sounds stop tada`。
`sounds list` 会列出全部可用的。

### 加入自己的声音

把文件丢进 `~/.claude/sounds/` 就行，支持 `.wav` `.mp3` `.aiff` `.oga` `.m4a` `.flac`。

```bash
cp ~/Downloads/tada.mp3 ~/.claude/sounds/
sounds list          # tada 出现了
sounds stop tada
sounds test stop
```

也可以直接给绝对路径：`sounds stop ~/Music/whatever.wav`。

---

## 配置文件

`~/.claude/sounds.json`。放在插件外面，所以更新插件不会被覆盖。
**建议一律用 CLI 改**（它会校验名称并告诉你哪个找不到），格式如下：

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

- 顶层 `enabled: false` 一律静音，覆盖所有事件级设置
- `sounds` 有两个以上 → 每次随机挑一个
- 事件级的 `volume` 覆盖全局音量
- `say` 和 `sounds` 可以共存，也可以只留 `say`

---

## 各平台情况

| | 声音 | 语音 | 音量 |
|---|---|---|---|
| **macOS** | `afplay` | `say` | 支持 |
| **Windows** | PowerShell `MediaPlayer` | `System.Speech` | 支持 |
| **Linux** | 依次寻找 `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay` / `play` | `spd-say` 或 `espeak` | 除 `aplay` 外都支持 |

**`focus` 只有 macOS 能用。** Windows 需要写 P/Invoke、Wayland 根本没有获取前台窗口的 API，
所以在这两个平台上 `sounds focus on` 会直接拒绝，而不是假装生效然后默默没作用。

---

## 疑难排查

**完全没声音。** 按顺序查：`sounds`（总开关是 ON 吗？那个事件是 `on` 吗？）→
SOUND 列有没有标 `(!missing)`？→ `sounds test stop` 会直接打印它为什么没响 →
`sounds list` 看这台机器实际能找到哪些声音。

**同一个声音响两次。** 你的 `~/.claude/settings.json` 里还留着手写的
`afplay` / `powershell` hook。插件 hooks 跟你的设置是**合并**而不是替换，
把旧的 `"hooks"` 段删掉就行。

**Linux 没声音。** `which paplay ffplay mpv aplay`，装一个即可
（`sudo apt install pulseaudio-utils`）。需要语音的话 `sudo apt install speech-dispatcher`。

**Windows 没声音。** 确认 PowerShell 可用，以及 `C:\Windows\Media\chimes.wav` 存在；
有些 Server 版本根本不附带音效文件，这种情况就自己放文件到 `~/.claude/sounds/`。

**装完之后整体变慢。** 不应该发生：播放是 detach 出去的，hook 大约 30 毫秒就返回。
用 `time python3 .../sounds.py hook Stop` 量一下，超过 200 毫秒请提 issue。

---

## 工作原理

就一个 Python 脚本。Claude Code 的 hook 会调用 `sounds.py hook <Event>`，
它读配置、把系统播放器**扔到后台**、然后立刻退出 —— 因为 `Stop` 和 `SubagentStop`
是阻塞式 hook，会等命令返回才继续，如果在这里等音频播完，Claude 每回一句话都会卡住。

自检：`python3 skills/sounds/scripts/sounds.py --selftest`

MIT 许可证。
