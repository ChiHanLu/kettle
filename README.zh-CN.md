# kettle

[English](README.md) · [繁體中文](README.zh-TW.md) · **简体中文**

**把水壶放上去，然后走开。** Claude Code 会在说完的时候、要跟你要权限的时候、
等你太久的时候发出声音 —— 以及**这一轮被 API 打死**的时候。从房间另一头看过去，
死掉的终端跟还在跑长得一模一样。

最后那个才是这个 plugin 存在的理由。其他通知 plugin 都只告诉你「做完了」，
没有一个会告诉你「它没做完」。

11 个 hook 事件，每个都能单独开关。你不开它就不出声。

macOS · Windows · Linux。零依赖，只用操作系统本来就有的东西。

![kettle demo](assets/demo.gif)

*GIF 没有声音 —— [**点这里看有声音的版本**](assets/demo.mp4)（22 秒），声音才是重点。*

---

## 安装

```bash
claude plugin marketplace add https://github.com/ChiHanLu/kettle
claude plugin install kettle@kettle --scope user
```

或者先 clone 下来装本地版：

```bash
git clone https://github.com/ChiHanLu/kettle
claude plugin marketplace add ./kettle
claude plugin install kettle@kettle --scope user
```

重启 Claude Code。**它是故意装成静音的** —— 总开关默认为关。

---

## 30 秒上手

在 Claude Code 里面，全部都是 `/kettle`：

```
/kettle on            打开（推荐组：说完、要权限、空闲、子 agent、出错）
/kettle               看现在谁对应谁
/kettle test          马上全部听一遍
/kettle off           全部安静
```

你也可以直接用说的：「完成音小声一点」「晚上十点以后别吵」
「出事的时候用语音播报」—— Claude 会自己翻译成对应命令。

也可以完全不经过 Claude，直接在终端里跑：

```bash
python3 ~/.claude/plugins/cache/kettle/kettle/*/skills/kettle/scripts/kettle.py
```

---

## 命令

```
kettle                      全貌：总开关、音量、静音时段、每个事件的状态
kettle on | off             总开关
kettle on stop | off stop   只开/关单个事件

kettle stop done            设置声音
kettle stop done,up         逗号 = 每次随机挑一个
kettle stop 说:好了          用语音代替提示音（say: / 说: / 說: 都认）
kettle stop ~/x/ding.mp3    直接指定文件路径
kettle stop off             等同 `kettle off stop`

kettle test [event]         按当前设置实际播一次（所有规则照跑）
kettle list                 这台机器上所有能叫出名字的声音
kettle volume 0.3 [event]   全局音量，或只调某一个事件
kettle quiet 22:00-09:00    静音时段（跨零点也算得对）
kettle quiet off
kettle focus on | off       终端在最前面时就闭嘴
kettle preset               回到推荐组
kettle preset off           所有事件全关
```

**没有 `set` 这个动词**。`kettle <事件> <声音>` 本身就是赋值。
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

当然也可以直接写系统声音原名 —— `kettle stop Glass`、`kettle stop tada`。
`kettle list` 会列出全部可用的。

### 加入自己的声音

把文件丢进 `~/.claude/kettle/sounds/` 就行，支持 `.wav` `.mp3` `.aiff` `.oga` `.m4a` `.flac`。

```bash
cp ~/Downloads/tada.mp3 ~/.claude/kettle/sounds/
kettle list          # tada 出现了
kettle stop tada
kettle test stop
```

也可以直接给绝对路径：`kettle stop ~/Music/whatever.wav`。

---

## 配置文件

`~/.claude/kettle/config.json`。放在插件外面，所以更新插件不会被覆盖。
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
- `kettle` 有两个以上 → 每次随机挑一个
- 事件级的 `volume` 覆盖全局音量
- `say` 和 `kettle` 可以共存，也可以只留 `say`

---

## 各平台情况

| | 声音 | 语音 | 音量 |
|---|---|---|---|
| **macOS** | `afplay` | `say` | 支持 |
| **Windows** | PowerShell `MediaPlayer` | `System.Speech` | 支持 |
| **Linux** | 依次寻找 `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay` / `play` | `spd-say` 或 `espeak` | 除 `aplay` 外都支持 |

**`focus` 只有 macOS 能用。** Windows 需要写 P/Invoke、Wayland 根本没有获取前台窗口的 API，
所以在这两个平台上 `kettle focus on` 会直接拒绝，而不是假装生效然后默默没作用。

---

## 疑难排查

**完全没声音。** 按顺序查：`kettle`（总开关是 ON 吗？那个事件是 `on` 吗？）→
SOUND 列有没有标 `(!missing)`？→ `kettle test stop` 会直接打印它为什么没响 →
`kettle list` 看这台机器实际能找到哪些声音。

**同一个声音响两次。** 你的 `~/.claude/settings.json` 里还留着手写的
`afplay` / `powershell` hook。插件 hooks 跟你的设置是**合并**而不是替换，
把旧的 `"hooks"` 段删掉就行。

**Linux 没声音。** `which paplay ffplay mpv aplay`，装一个即可
（`sudo apt install pulseaudio-utils`）。需要语音的话 `sudo apt install speech-dispatcher`。

**Windows 没声音。** 确认 PowerShell 可用，以及 `C:\Windows\Media\chimes.wav` 存在；
有些 Server 版本根本不附带音效文件，这种情况就自己放文件到 `~/.claude/kettle/sounds/`。

**装完之后整体变慢。** 不应该发生：播放是 detach 出去的，hook 大约 30 毫秒就返回。
用 `time python3 .../kettle.py hook Stop` 量一下，超过 200 毫秒请提 issue。

---

## 工作原理

就一个 Python 脚本。Claude Code 的 hook 会调用 `kettle.py hook <Event>`，
它读配置、把系统播放器**扔到后台**、然后立刻退出 —— 因为 `Stop` 和 `SubagentStop`
是阻塞式 hook，会等命令返回才继续，如果在这里等音频播完，Claude 每回一句话都会卡住。

自检：`python3 skills/kettle/scripts/kettle.py --selftest`

MIT 许可证。
