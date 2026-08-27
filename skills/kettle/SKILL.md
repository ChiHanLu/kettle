---
name: kettle
description: Control Claude Code's sound cues - which hook events make a sound, which sound, volume, quiet hours, custom audio files. Use when the user wants Claude to beep/chime/speak when it finishes, when it needs permission, when it errors out, or wants to mute, change, preview, or add sounds. Triggers on "kettle", "sound", "beep", "chime", "notify me when done", "音效", "提示音", "静音", "靜音".
---

# kettle

A sound plays at Claude Code hook events. Everything is driven by one CLI — never
hand-edit the config file, the CLI validates names and reports what's missing.

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/kettle/scripts/kettle.py" <args>
```

Config lives at `~/.claude/kettle/config.json`, custom audio at `~/.claude/kettle/sounds/`.
Both survive plugin updates.

## The two namespaces (they never collide)

**Events** — when a sound fires:

| short | hook event | fires when |
|---|---|---|
| `stop` | `Stop` | Claude finished this turn |
| `ask` | `Notification:permission_prompt` | a permission prompt appeared |
| `idle` | `Notification:idle_prompt` | Claude has been waiting on you |
| `sub` | `SubagentStop` | a subagent finished |
| `error` | `StopFailure` | the turn died on an API error (rate limit, overload) |
| `fail` | `PostToolUseFailure` | a command or edit failed |
| `denied` | `PermissionDenied` | auto mode blocked a tool call |
| `compact` | `PreCompact` | context is about to be compacted |
| `start` | `SessionStart` | session started (startup only, not resume) |
| `end` | `SessionEnd` | session ended |
| `task` | `TaskCompleted` | a background task completed |

`kettle preset` turns on: `stop ask idle sub error`. Everything else stays off.

**Sounds** — portable aliases that map to whatever the OS actually ships:
`done ding soft up alert boom hmm down`.
You can also name a raw system sound (`Glass`, `chimes`), a file in
`~/.claude/kettle/sounds/`, or any path.

## Commands

```
kettle                      full picture: master switch, volume, quiet, every event
kettle on | off             master switch
kettle on stop | off stop   one event
kettle stop done            set a sound
kettle stop done,up         comma = pick one at random each time
kettle stop say:all done    speak instead of chime
kettle stop ~/x/ding.mp3    any file
kettle stop off             same as `kettle off stop`
kettle test [event]         actually play it, all rules applied
kettle list                 every nameable sound on this machine
kettle volume 0.3 [event]   global, or one event
kettle quiet 22:00-09:00    silent window (spans midnight fine) | kettle quiet off
kettle focus on | off       stay silent while the terminal is the front app (macOS only)
kettle preset | preset off  recommended set / all events off
```

## Translating prose into commands

| user says | run |
|---|---|
| "make some noise when you're done" | `kettle on` (then `kettle test stop`) |
| "too loud" | `kettle volume 0.2` |
| "the subagent one is annoying" | `kettle off sub` |
| "don't beep at night" | `kettle quiet 22:00-09:00` |
| "only when I'm not looking" | `kettle focus on` |
| "say something when it breaks" | `kettle error say:something broke` |
| "what sounds do I have" | `kettle list` |
| "I added my own mp3" | `kettle list` then `kettle <event> <name>` |
| "turn it all off" | `kettle off` |

After a change that affects a specific event, offer `kettle test <event>` so the user
hears it immediately.

## Notes

- Installed silent on purpose. Nothing plays until `kettle on`.
- Hooks are fire-and-forget: playback is detached, the hook exits immediately.
  `Stop` and `SubagentStop` block the turn, so this matters — never make the
  hook wait on audio.
- Sound not found → silence, no error. `kettle` marks it `(!missing)` and
  `kettle list` shows what does resolve.
- Linux needs one of `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay`;
  speech needs `spd-say` or `espeak`.
- Focus detection is macOS-only; `kettle focus on` refuses elsewhere rather than
  pretending to work.

## Self-check

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/kettle/scripts/kettle.py" --selftest
```
