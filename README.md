# kettle

**English** · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md)

**Put the kettle on and walk away.** Claude Code makes a sound when it finishes, when
it needs your permission, when it's been waiting on you — and when the turn **died** on
an API error, which from across the room looks exactly like still working.

That last one is the reason this exists. Every other notification plugin tells you it
finished. None of them tell you it didn't.

11 hook events, each independently switchable. Nothing plays until you say so.

macOS · Windows · Linux. No dependencies — only what your OS already ships.

![kettle demo](assets/demo.gif)

*The GIF is silent — [**watch it with sound**](assets/demo.mp4) (22s), which is rather the point.*

---

## Install

```bash
claude plugin marketplace add https://github.com/ChiHanLu/kettle
claude plugin install kettle@kettle --scope user
```

Local checkout instead:

```bash
git clone https://github.com/ChiHanLu/kettle
claude plugin marketplace add ./kettle
claude plugin install kettle@kettle --scope user
```

Restart Claude Code. **It installs silent on purpose** — the master switch is off.

---

## 30 seconds

Inside Claude Code, everything is `/kettle`:

```
/kettle on            turn it on (recommended set: done, needs-you, idle, subagent, error)
/kettle               see exactly what's wired to what
/kettle test          hear all of them right now
/kettle off           silence
```

You can also talk to it: *"make the done sound quieter"*, *"don't beep after 10pm"*,
*"say something when it breaks"* — Claude translates that into the right command.

Or run it straight from a terminal, no Claude involved:

```bash
python3 ~/.claude/plugins/cache/kettle/kettle/*/skills/kettle/scripts/kettle.py
```

---

## Commands

```
kettle                      full picture: master switch, volume, quiet hours, every event
kettle on | off             master switch
kettle on stop | off stop   one event

kettle stop done            set a sound
kettle stop done,up         comma = pick one at random each time
kettle stop say:all done    speak it instead of chiming
kettle stop ~/x/ding.mp3    any file path
kettle stop off             same as `kettle off stop`

kettle test [event]         play it for real, with every rule applied
kettle list                 every sound you can name on this machine
kettle volume 0.3 [event]   globally, or just one event
kettle quiet 22:00-09:00    silent window (spans midnight correctly)
kettle quiet off
kettle focus on | off       stay silent while the terminal is the front app
kettle preset               back to the recommended set
kettle preset off           every event off
```

There is no `set` verb. `kettle <event> <sound>` **is** the setter. Event names and
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
| `soft` | Pop | Windows Balloon | audio-volume-change |
| `up` | Blow | Windows Notify | dialog-information |
| `alert` | Funk | Windows Notify System Generic | message-new-instant |
| `boom` | Basso | Windows Critical Stop | dialog-warning |
| `hmm` | Purr | Windows Background | window-question |
| `down` | Sosumi | Windows Exclamation | dialog-error |

Each alias has several fallbacks per platform, so a missing file on one Windows build
doesn't leave you silent.

You can also name a raw system sound directly — `kettle stop Glass`, `kettle stop tada`.
`kettle list` shows everything available.

### Your own kettle

Drop files into `~/.claude/kettle/sounds/` — `.wav` `.mp3` `.aiff` `.oga` `.m4a` `.flac`.

```bash
cp ~/Downloads/tada.mp3 ~/.claude/kettle/sounds/
kettle list          # tada now shows up
kettle stop tada
kettle test stop
```

Absolute paths work too: `kettle stop ~/Music/whatever.wav`.

---

## Config

`~/.claude/kettle/config.json`. Lives outside the plugin, so updates never wipe it.
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
- More than one entry in `kettle` → one is picked at random each time
- Per-event `volume` overrides the global one
- `say` and `kettle` can coexist, or you can use `say` alone

---

## Platform notes

| | sound | speech | volume |
|---|---|---|---|
| **macOS** | `afplay` | `say` | yes |
| **Windows** | PowerShell `MediaPlayer` | `System.Speech` | yes |
| **Linux** | first of `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay` / `play` | `spd-say` or `espeak` | all but `aplay` |

**`focus` is macOS-only.** Windows needs a P/Invoke shim and Wayland exposes no
focused-window API at all, so `kettle focus on` refuses on those platforms rather
than silently doing nothing.

---

## Troubleshooting

**No sound at all.** In order: `kettle` (is master ON? is that event `on`?) →
is the SOUND column marked `(!missing)`? → `kettle test stop` prints the exact reason
it stayed quiet → `kettle list` to see what actually resolves on this machine.

**A sound plays twice.** You still have hand-written `afplay` / `powershell` hooks in
`~/.claude/settings.json`. Plugin hooks are *merged* with yours, not substituted.
Delete the old `"hooks"` block.

**Linux is silent.** `which paplay ffplay mpv aplay` — install one
(`sudo apt install pulseaudio-utils`). For speech: `sudo apt install speech-dispatcher`.

**Windows is silent.** Check PowerShell is reachable and that
`C:\Windows\Media\chimes.wav` exists; some Server SKUs ship no media files —
put your own into `~/.claude/kettle/sounds/`.

**Everything is slow after installing.** Shouldn't happen: playback is detached and
the hook returns in ~30 ms. Verify with
`time python3 .../kettle.py hook Stop`. If it's over 200 ms, file an issue.

---

## How it works

One Python script. Claude Code hooks call `kettle.py hook <Event>`, which reads the
config, spawns the OS player **detached**, and exits immediately — `Stop` and
`SubagentStop` block the turn until the hook returns, so waiting on audio would stall
Claude on every single reply.

Self-check: `python3 skills/kettle/scripts/kettle.py --selftest`

MIT.
