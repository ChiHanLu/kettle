# claude-sounds

**English** · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md)

Claude Code makes a sound when something worth hearing happens — it finished, it
needs your permission, it's been waiting on you, the API rate-limited you and the
whole turn died. Every event is independently switchable. Nothing plays until you
say so.

macOS · Windows · Linux. No dependencies — only what your OS already ships.

---

## Install

```bash
claude plugin marketplace add https://github.com/ChiHanLu/claude-sounds
claude plugin install claude-sounds@claude-sounds --scope user
```

Local checkout instead:

```bash
git clone https://github.com/ChiHanLu/claude-sounds
claude plugin marketplace add ./claude-sounds
claude plugin install claude-sounds@claude-sounds --scope user
```

Restart Claude Code. **It installs silent on purpose** — the master switch is off.

---

## 30 seconds

Inside Claude Code, everything is `/sounds`:

```
/sounds on            turn it on (recommended set: done, needs-you, idle, subagent, error)
/sounds               see exactly what's wired to what
/sounds test          hear all of them right now
/sounds off           silence
```

You can also talk to it: *"make the done sound quieter"*, *"don't beep after 10pm"*,
*"say something when it breaks"* — Claude translates that into the right command.

Or run it straight from a terminal, no Claude involved:

```bash
python3 ~/.claude/plugins/cache/claude-sounds/claude-sounds/*/skills/sounds/scripts/sounds.py
```

---

## Commands

```
sounds                      full picture: master switch, volume, quiet hours, every event
sounds on | off             master switch
sounds on stop | off stop   one event

sounds stop done            set a sound
sounds stop done,up         comma = pick one at random each time
sounds stop say:all done    speak it instead of chiming
sounds stop ~/x/ding.mp3    any file path
sounds stop off             same as `sounds off stop`

sounds test [event]         play it for real, with every rule applied
sounds list                 every sound you can name on this machine
sounds volume 0.3 [event]   globally, or just one event
sounds quiet 22:00-09:00    silent window (spans midnight correctly)
sounds quiet off
sounds focus on | off       stay silent while the terminal is the front app
sounds preset               back to the recommended set
sounds preset off           every event off
```

There is no `set` verb. `sounds <event> <sound>` **is** the setter. Event names and
sound names are two namespaces that never overlap, so it's never ambiguous.

---

## Events

| name | hook event | fires when | in preset |
|---|---|---|:-:|
| `stop` | `Stop` | Claude finished this turn | ● |
| `ask` | `Notification:permission_prompt` | a permission prompt appeared | ● |
| `idle` | `Notification:idle_prompt` | Claude has been waiting on you | ● |
| `sub` | `SubagentStop` | a subagent finished | ● |
| `error` | `StopFailure` | the turn **died** on an API error — rate limit, overload | ● |
| `fail` | `PostToolUseFailure` | a command or edit failed | |
| `denied` | `PermissionDenied` | auto mode blocked a tool call | |
| `compact` | `PreCompact` | context is about to be compacted | |
| `start` | `SessionStart` | session started (startup only, not resume) | |
| `end` | `SessionEnd` | session ended | |
| `task` | `TaskCompleted` | a background task completed | |

`error` is the one people don't think to set up and then miss the most: when Claude
gets rate-limited, the turn just stops. Without a sound you find out five minutes later.

---

## Sounds

Eight portable aliases, so the same config works on any machine:

| alias | macOS | Windows | Linux |
|---|---|---|---|
| `done` | Glass | chimes | complete |
| `ding` | Ping | Windows Ding | bell |
| `soft` | Pop | Windows Balloon | message |
| `up` | Blow | Windows Notify | dialog-information |
| `alert` | Funk | Windows Notify System Generic | message |
| `boom` | Basso | Windows Critical Stop | dialog-warning |
| `hmm` | Purr | Windows Background | dialog-question |
| `down` | Sosumi | Windows Exclamation | dialog-error |

Each alias has several fallbacks per platform, so a missing file on one Windows build
doesn't leave you silent.

You can also name a raw system sound directly — `sounds stop Glass`, `sounds stop tada`.
`sounds list` shows everything available.

### Your own sounds

Drop files into `~/.claude/sounds/` — `.wav` `.mp3` `.aiff` `.oga` `.m4a` `.flac`.

```bash
cp ~/Downloads/tada.mp3 ~/.claude/sounds/
sounds list          # tada now shows up
sounds stop tada
sounds test stop
```

Absolute paths work too: `sounds stop ~/Music/whatever.wav`.

---

## Config

`~/.claude/sounds.json`. Lives outside the plugin, so updates never wipe it.
Use the CLI — it validates names and tells you what's missing — but this is the shape:

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
    "StopFailure":                    { "sounds": ["boom"], "say": "rate limited" },
    "PreCompact":                     { "sounds": ["hmm"], "enabled": false }
  }
}
```

- Top-level `enabled: false` mutes everything regardless of per-event settings
- More than one entry in `sounds` → one is picked at random each time
- Per-event `volume` overrides the global one
- `say` and `sounds` can coexist, or you can use `say` alone

---

## Platform notes

| | sound | speech | volume |
|---|---|---|---|
| **macOS** | `afplay` | `say` | yes |
| **Windows** | PowerShell `MediaPlayer` | `System.Speech` | yes |
| **Linux** | first of `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay` / `play` | `spd-say` or `espeak` | all but `aplay` |

**`focus` is macOS-only.** Windows needs a P/Invoke shim and Wayland exposes no
focused-window API at all, so `sounds focus on` refuses on those platforms rather
than silently doing nothing.

---

## Troubleshooting

**No sound at all.** In order: `sounds` (is master ON? is that event `on`?) →
is the SOUND column marked `(!missing)`? → `sounds test stop` prints the exact reason
it stayed quiet → `sounds list` to see what actually resolves on this machine.

**A sound plays twice.** You still have hand-written `afplay` / `powershell` hooks in
`~/.claude/settings.json`. Plugin hooks are *merged* with yours, not substituted.
Delete the old `"hooks"` block.

**Linux is silent.** `which paplay ffplay mpv aplay` — install one
(`sudo apt install pulseaudio-utils`). For speech: `sudo apt install speech-dispatcher`.

**Windows is silent.** Check PowerShell is reachable and that
`C:\Windows\Media\chimes.wav` exists; some Server SKUs ship no media files —
put your own into `~/.claude/sounds/`.

**Everything is slow after installing.** Shouldn't happen: playback is detached and
the hook returns in ~30 ms. Verify with
`time python3 .../sounds.py hook Stop`. If it's over 200 ms, file an issue.

---

## How it works

One Python script. Claude Code hooks call `sounds.py hook <Event>`, which reads the
config, spawns the OS player **detached**, and exits immediately — `Stop` and
`SubagentStop` block the turn until the hook returns, so waiting on audio would stall
Claude on every single reply.

Self-check: `python3 skills/sounds/scripts/sounds.py --selftest`

MIT.
