---
name: sounds
description: Control Claude Code's sound cues - which hook events make a sound, which sound, volume, quiet hours, custom audio files. Use when the user wants Claude to beep/chime/speak when it finishes, when it needs permission, when it errors out, or wants to mute, change, preview, or add sounds. Triggers on "sound", "beep", "chime", "notify me when done", "音效", "提示音", "静音", "靜音".
---

# claude-sounds

A sound plays at Claude Code hook events. Everything is driven by one CLI — never
hand-edit the config file, the CLI validates names and reports what's missing.

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/sounds/scripts/sounds.py" <args>
```

Config lives at `~/.claude/sounds.json`, custom audio at `~/.claude/sounds/`.
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

`sounds preset` turns on: `stop ask idle sub error`. Everything else stays off.

**Sounds** — portable aliases that map to whatever the OS actually ships:
`done ding soft up alert boom hmm down`.
You can also name a raw system sound (`Glass`, `chimes`), a file in
`~/.claude/sounds/`, or any path.

## Commands

```
sounds                      full picture: master switch, volume, quiet, every event
sounds on | off             master switch
sounds on stop | off stop   one event
sounds stop done            set a sound
sounds stop done,up         comma = pick one at random each time
sounds stop say:all done    speak instead of chime
sounds stop ~/x/ding.mp3    any file
sounds stop off             same as `sounds off stop`
sounds test [event]         actually play it, all rules applied
sounds list                 every nameable sound on this machine
sounds volume 0.3 [event]   global, or one event
sounds quiet 22:00-09:00    silent window (spans midnight fine) | sounds quiet off
sounds focus on | off       stay silent while the terminal is the front app (macOS only)
sounds preset | preset off  recommended set / all events off
```

## Translating prose into commands

| user says | run |
|---|---|
| "make some noise when you're done" | `sounds on` (then `sounds test stop`) |
| "too loud" | `sounds volume 0.2` |
| "the subagent one is annoying" | `sounds off sub` |
| "don't beep at night" | `sounds quiet 22:00-09:00` |
| "only when I'm not looking" | `sounds focus on` |
| "say something when it breaks" | `sounds error say:something broke` |
| "what sounds do I have" | `sounds list` |
| "I added my own mp3" | `sounds list` then `sounds <event> <name>` |
| "turn it all off" | `sounds off` |

After a change that affects a specific event, offer `sounds test <event>` so the user
hears it immediately.

## Notes

- Installed silent on purpose. Nothing plays until `sounds on`.
- Hooks are fire-and-forget: playback is detached, the hook exits immediately.
  `Stop` and `SubagentStop` block the turn, so this matters — never make the
  hook wait on audio.
- Sound not found → silence, no error. `sounds` marks it `(!missing)` and
  `sounds list` shows what does resolve.
- Linux needs one of `paplay` / `pw-play` / `ffplay` / `mpv` / `aplay`;
  speech needs `spd-say` or `espeak`.
- Focus detection is macOS-only; `sounds focus on` refuses elsewhere rather than
  pretending to work.

## Self-check

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/sounds/scripts/sounds.py" --selftest
```
