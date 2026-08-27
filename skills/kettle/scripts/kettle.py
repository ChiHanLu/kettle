#!/usr/bin/env python3
"""kettle - Claude Code makes a sound when it needs you. macOS / Windows / Linux.

Config:  ~/.claude/kettle/config.json
Sounds:  ~/.claude/kettle/sounds/   (drop your own .wav/.mp3/.aiff/.oga/.m4a here)

Hooks call `kettle.py hook <EventKey>`. Everything else is the user-facing CLI.
"""

import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
KETTLE_HOME = HOME / ".claude" / "kettle"
CONFIG = Path(os.environ.get("KETTLE_CONFIG", KETTLE_HOME / "config.json"))
USER_SOUNDS = Path(os.environ.get("KETTLE_SOUNDS_DIR", KETTLE_HOME / "sounds"))

if sys.platform.startswith("win"):
    PLAT = "win32"
elif sys.platform == "darwin":
    PLAT = "darwin"
else:
    PLAT = "linux"

EXTS = ["", ".wav", ".mp3", ".aiff", ".aif", ".oga", ".ogg", ".m4a", ".flac"]

SYSTEM_DIRS = {
    "darwin": [Path("/System/Library/Sounds"), HOME / "Library" / "Sounds"],
    "win32": [Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Media"],
    "linux": [
        Path("/usr/share/sounds/freedesktop/stereo"),
        Path("/usr/share/sounds/ubuntu/stereo"),
        Path("/usr/share/sounds"),
    ],
}[PLAT]

# Portable semantic names. Several candidates per platform because Windows
# media filenames drift between releases and Linux distros ship different sets.
ALIASES = {
    "done":  {"darwin": ["Glass"],  "win32": ["chimes", "tada", "Windows Notify System Generic"],
              "linux": ["complete", "bell", "message"]},
    "ding":  {"darwin": ["Ping"],   "win32": ["Windows Ding", "ding", "chimes"],
              "linux": ["bell", "message", "complete"]},
    "soft":  {"darwin": ["Pop"],    "win32": ["Windows Balloon", "Speech On", "ding"],
              "linux": ["audio-volume-change", "device-added", "message", "bell"]},
    "up":    {"darwin": ["Blow"],   "win32": ["Windows Notify", "Windows Notify System Generic", "chimes"],
              "linux": ["dialog-information", "service-login", "message", "bell"]},
    "alert": {"darwin": ["Funk"],   "win32": ["Windows Notify System Generic", "Windows Notify", "notify"],
              "linux": ["message-new-instant", "message", "dialog-information", "bell"]},
    "boom":  {"darwin": ["Basso"],  "win32": ["Windows Critical Stop", "chord", "Windows Foreground"],
              "linux": ["dialog-warning", "suspend-error", "dialog-error", "bell"]},
    "hmm":   {"darwin": ["Purr"],   "win32": ["Windows Background", "Windows Balloon", "ding"],
              "linux": ["window-question", "window-attention", "message", "bell"]},
    "down":  {"darwin": ["Sosumi"], "win32": ["Windows Exclamation", "Windows Error", "chord"],
              "linux": ["dialog-error", "dialog-warning", "bell"]},
}

# short name -> (config key, what it means)
EVENTS = {
    "stop":    ("Stop",                            "Claude finished this turn"),
    "ask":     ("Notification:permission_prompt",  "A permission prompt appeared"),
    "idle":    ("Notification:idle_prompt",        "Claude has been waiting on you"),
    "sub":     ("SubagentStop",                    "A subagent finished"),
    "error":   ("StopFailure",                     "Turn died on an API error (rate limit, overload)"),
    "fail":    ("PostToolUseFailure",              "A command or edit failed"),
    "denied":  ("PermissionDenied",                "Auto mode blocked a tool call"),
    "compact": ("PreCompact",                      "Context is about to be compacted"),
    "start":   ("SessionStart",                    "Session started"),
    "end":     ("SessionEnd",                      "Session ended"),
    "task":    ("TaskCompleted",                   "A background task completed"),
}
KEY_TO_SHORT = {v[0]: k for k, v in EVENTS.items()}

# The recommended set: on when you run `kettle preset`. Everything else is off.
RECOMMENDED = {"Stop", "Notification:permission_prompt", "Notification:idle_prompt",
               "SubagentStop", "StopFailure"}

DEFAULTS = {
    "enabled": False,
    "volume": 0.5,
    "quiet_hours": None,
    "only_when_unfocused": False,
    "events": {
        "Stop":                          {"sounds": ["done", "up"]},
        "Notification:permission_prompt": {"sounds": ["alert"]},
        "Notification:idle_prompt":       {"sounds": ["hmm"]},
        "SubagentStop":                   {"sounds": ["soft"], "volume": 0.3},
        "StopFailure":                    {"sounds": ["boom"], "say": "Claude hit an API error"},
        "PostToolUseFailure":             {"sounds": ["down"], "enabled": False},
        "PermissionDenied":               {"sounds": ["ding"], "enabled": False},
        "PreCompact":                     {"sounds": ["hmm"],  "enabled": False},
        "SessionStart":                   {"sounds": ["up"],   "enabled": False},
        "SessionEnd":                     {"sounds": ["down"], "enabled": False},
        "TaskCompleted":                  {"sounds": ["ding"], "enabled": False},
    },
}

TERMINALS = {"ghostty", "iterm2", "iterm", "terminal", "warp", "alacritty", "kitty",
             "wezterm", "hyper", "tabby", "code", "cursor", "visual studio code",
             "windsurf", "electron"}


# ---------------------------------------------------------------- config

def load():
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return json.loads(json.dumps(DEFAULTS))
    merged = json.loads(json.dumps(DEFAULTS))
    merged.update({k: v for k, v in cfg.items() if k != "events"})
    # A configured event replaces its default outright - merging would resurrect
    # a sound the user just swapped out for say:, and you could never drop one.
    for key, ev in (cfg.get("events") or {}).items():
        merged["events"][key] = ev
    return merged


def save(cfg):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- resolving

def resolve(name):
    """Sound name -> playable Path, or None. Never raises, never prints."""
    if not name:
        return None
    if os.sep in name or "/" in name or name.startswith("~"):
        p = Path(name).expanduser()
        return p if p.is_file() else None

    candidates = ALIASES.get(name.lower(), {}).get(PLAT, []) or []
    for cand in [name, *candidates]:
        for d in [USER_SOUNDS, *SYSTEM_DIRS]:
            for ext in EXTS:
                p = d / (cand + ext)
                if p.is_file():
                    return p
    return None


def available():
    """(aliases_that_resolve, {dir: [stems]}) for `kettle list`."""
    aliases = [a for a in ALIASES if resolve(a)]
    found = {}
    for d in [USER_SOUNDS, *SYSTEM_DIRS]:
        if not d.is_dir():
            continue
        stems = sorted({f.stem for f in d.iterdir()
                        if f.is_file() and f.suffix.lower() in EXTS[1:]})
        if stems:
            found[d] = stems
    return aliases, found


# ---------------------------------------------------------------- playback

def _spawn(cmd):
    kw = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "stdin": subprocess.DEVNULL}
    if PLAT == "win32":
        kw["creationflags"] = 0x08000000 | 0x00000008  # CREATE_NO_WINDOW | DETACHED_PROCESS
    else:
        kw["start_new_session"] = True
    try:
        subprocess.Popen(cmd, **kw)  # fire and forget - blocking hooks depend on this
        return True
    except Exception:
        return False


def _powershell(script):
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if not exe:
        return False
    # -NoProfile matters: a user profile can add seconds to startup.
    return _spawn([exe, "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script])


def _linux_player(path, vol):
    pct = int(max(0.0, min(1.0, vol)) * 100)
    for exe, build in (
        ("paplay",  lambda: ["paplay", "--volume=%d" % int(pct * 655.36), path]),
        ("pw-play", lambda: ["pw-play", "--volume", "%.2f" % vol, path]),
        ("ffplay",  lambda: ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                             "-volume", str(pct), path]),
        ("mpv",     lambda: ["mpv", "--no-video", "--really-quiet", "--volume=%d" % pct, path]),
        ("aplay",   lambda: ["aplay", "-q", path]),  # ponytail: aplay ignores volume, wav only
        ("play",    lambda: ["play", "-q", "-v", "%.2f" % vol, path]),
    ):
        if shutil.which(exe):
            return build()
    return None


def play(name, vol):
    path = resolve(name)
    if not path:
        return False
    p = str(path)
    if PLAT == "darwin":
        return _spawn(["afplay", "-v", "%.2f" % max(0.0, min(1.0, vol)), p])
    if PLAT == "win32":
        return _powershell(
            "Add-Type -AssemblyName presentationCore;"
            "$p=New-Object System.Windows.Media.MediaPlayer;"
            "$p.Open([uri]'%s');$p.Volume=%.2f;"
            "Start-Sleep -Milliseconds 300;$p.Play();"
            "try{$d=$p.NaturalDuration.TimeSpan.TotalSeconds}catch{$d=3};"
            "Start-Sleep -Seconds ($d+0.3)" % (p.replace("'", "''"), max(0.0, min(1.0, vol)))
        )
    cmd = _linux_player(p, vol)
    return _spawn(cmd) if cmd else False


def speak(text):
    if not text:
        return False
    if PLAT == "darwin":
        return _spawn(["say", text])
    if PLAT == "win32":
        return _powershell(
            "Add-Type -AssemblyName System.Speech;"
            "(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('%s')"
            % text.replace("'", "''")
        )
    for exe, build in (("spd-say", lambda: ["spd-say", "-w", text]),
                       ("espeak-ng", lambda: ["espeak-ng", text]),
                       ("espeak", lambda: ["espeak", text])):
        if shutil.which(exe):
            return _spawn(build())
    return False


# ---------------------------------------------------------------- rules

def in_quiet(spec, now=None):
    """'22:00-09:00' spans midnight correctly."""
    if not spec:
        return False
    try:
        a, b = str(spec).split("-")
        to_min = lambda s: int(s.split(":")[0]) * 60 + int(s.split(":")[1])
        start, end = to_min(a.strip()), to_min(b.strip())
    except Exception:
        return False
    t = now if now is not None else (time.localtime().tm_hour * 60 + time.localtime().tm_min)
    return start <= t < end if start < end else (t >= start or t < end)


def terminal_focused():
    """macOS only. Elsewhere returns False so we never wrongly stay silent."""
    # ponytail: Windows needs P/Invoke, Wayland exposes no focused window at all.
    if PLAT != "darwin":
        return False
    try:
        asn = subprocess.run(["lsappinfo", "front"], capture_output=True, text=True,
                             timeout=1).stdout.strip()
        if not asn:
            return False
        out = subprocess.run(["lsappinfo", "info", "-only", "name", asn],
                             capture_output=True, text=True, timeout=1).stdout
    except Exception:
        return False
    name = out.split("=")[-1].strip().strip('"').lower()
    term = (os.environ.get("TERM_PROGRAM") or "").lower().replace(".app", "")
    return bool(name) and (name in TERMINALS or (term and term in name))


def fire(cfg, key, force=False):
    """Run every rule for one event. Returns a reason string, or None if it played."""
    ev = cfg["events"].get(key)
    if ev is None:
        return "no such event: %s" % key
    if not force:
        if not cfg.get("enabled"):
            return "muted (kettle on)"
        if ev.get("enabled", True) is False:
            return "event off (kettle on %s)" % KEY_TO_SHORT.get(key, key)
        if in_quiet(cfg.get("quiet_hours")):
            return "quiet hours %s" % cfg["quiet_hours"]
        if cfg.get("only_when_unfocused") and terminal_focused():
            return "terminal is focused"

    vol = ev.get("volume", cfg.get("volume", 0.5))
    pool = ev.get("sounds") or []
    ok = play(random.choice(pool), vol) if pool else False
    if ev.get("say"):
        ok = speak(ev["say"]) or ok
    return None if ok else "nothing playable (kettle list)"


# ---------------------------------------------------------------- CLI helpers

def event_key(token):
    t = (token or "").lower()
    if t in EVENTS:
        return EVENTS[t][0]
    for key in EVENTS.values():
        if key[0].lower() == t:
            return key[0]
    return None


def die(msg, code=1):
    print(msg)
    sys.exit(code)


# ---------------------------------------------------------------- commands

USAGE = """kettle - Claude Code makes a sound when it needs you

  kettle                     show everything
  kettle on | off            master switch
  kettle on stop | off stop  one event

  kettle stop done           set a sound
  kettle stop done,up        comma = random pool
  kettle stop say:all done   say: prefix speaks instead
  kettle stop ~/my/ding.mp3  any file path

  kettle test [event]        play it for real, all rules applied
  kettle list                every sound you can name
  kettle volume 0.3 [event]
  kettle quiet 22:00-09:00 | kettle quiet off
  kettle focus on | off      only sound when the terminal isn't in front
  kettle preset | preset off recommended set / all events off

events: """ + "  ".join(EVENTS) + "\nsounds: " + "  ".join(ALIASES)


def _pad(s, n):
    """Left-align in a fixed *display* width - CJK glyphs occupy two columns."""
    import unicodedata
    w = lambda t: sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in t)
    while w(s) > n:
        s = s[:-2] + "…"
    return s + " " * (n - w(s))


def cmd_status(cfg):
    print("master   : %s" % ("ON" if cfg.get("enabled") else "OFF   (kettle on)"))
    print("volume   : %s" % cfg.get("volume"))
    print("quiet    : %s" % (cfg.get("quiet_hours") or "-"))
    print("focus    : %s" % ("only when terminal is not in front"
                             if cfg.get("only_when_unfocused") else "-"))
    print("config   : %s" % CONFIG)
    print()
    print("  %-8s %-5s %-26s %s" % ("EVENT", "STATE", "SOUND", "FIRES WHEN"))
    for short, (key, desc) in EVENTS.items():
        ev = cfg["events"].get(key, {})
        state = "on" if ev.get("enabled", True) else "off"
        bits = ",".join(ev.get("sounds") or [])
        if ev.get("say"):
            bits = (bits + " " if bits else "") + 'say:"%s"' % ev["say"]
        if [s for s in (ev.get("sounds") or []) if not resolve(s)]:
            bits += " (!missing)"
        print("  %-8s %-5s %s %s" % (short, state, _pad(bits or "-", 26), desc))
    print("\n`kettle` with no args prints this. `kettle help` for commands.")


def cmd_toggle(cfg, on, rest):
    if rest:
        key = event_key(rest[0]) or die("unknown event: %s\nevents: %s" % (rest[0], " ".join(EVENTS)))
        cfg["events"].setdefault(key, {})["enabled"] = on
        save(cfg)
        print("%s: %s" % (KEY_TO_SHORT[key], "on" if on else "off"))
        if on and not cfg.get("enabled"):
            print("note: master switch is still off - run `kettle on`")
    else:
        cfg["enabled"] = on
        save(cfg)
        print("kettle %s" % ("on" if on else "off"))


def cmd_set(cfg, key, spec):
    ev = cfg["events"].setdefault(key, {})
    low = spec.lower()
    for prefix in ("say:", "說:", "说:", "say：", "說：", "说："):
        if low.startswith(prefix) or spec.startswith(prefix):
            ev["say"] = spec[len(prefix):].strip()
            ev.pop("sounds", None)
            ev["enabled"] = True
            save(cfg)
            print("%s: say %r" % (KEY_TO_SHORT[key], ev["say"]))
            return
    if low == "off":
        return cmd_toggle(cfg, False, [KEY_TO_SHORT[key]])
    pool = [s.strip() for s in spec.split(",") if s.strip()]
    ev["sounds"] = pool
    ev.pop("say", None)
    ev["enabled"] = True
    save(cfg)
    missing = [s for s in pool if not resolve(s)]
    print("%s: %s%s" % (KEY_TO_SHORT[key], ",".join(pool),
                        "   (!not found: %s)" % ",".join(missing) if missing else ""))


def cmd_test(cfg, rest):
    keys = [event_key(rest[0])] if rest else [
        k for k in cfg["events"] if cfg["events"][k].get("enabled", True)]
    if rest and not keys[0]:
        die("unknown event: %s" % rest[0])
    for key in keys:
        why = fire(cfg, key)
        print("  %-8s %s" % (KEY_TO_SHORT.get(key, key), why or "playing"))
        if not why and len(keys) > 1:
            time.sleep(1.2)


def cmd_list():
    aliases, found = available()
    print("aliases (portable, use these):")
    for a in ALIASES:
        p = resolve(a)
        print("  %-7s -> %s" % (a, p.name if p else "(!not available on this system)"))
    for d, stems in found.items():
        label = "your sounds" if d == USER_SOUNDS else "system"
        print("\n%s  %s:" % (label, d))
        line = "  "
        for s in stems:
            if len(line) + len(s) > 76:
                print(line)
                line = "  "
            line += s + "  "
        print(line)
    if USER_SOUNDS not in found:
        print("\nyour sounds: drop files into %s" % USER_SOUNDS)


def cmd_volume(cfg, rest):
    if not rest:
        die("usage: kettle volume 0.3 [event]")
    try:
        v = max(0.0, min(1.0, float(rest[0])))
    except ValueError:
        die("volume must be 0.0 - 1.0")
    if len(rest) > 1:
        key = event_key(rest[1]) or die("unknown event: %s" % rest[1])
        cfg["events"].setdefault(key, {})["volume"] = v
        print("%s volume: %s" % (KEY_TO_SHORT[key], v))
    else:
        cfg["volume"] = v
        print("volume: %s" % v)
    save(cfg)


def cmd_quiet(cfg, rest):
    if not rest:
        die("usage: kettle quiet 22:00-09:00 | kettle quiet off")
    if rest[0].lower() == "off":
        cfg["quiet_hours"] = None
    else:
        if in_quiet(rest[0], now=0) is False and in_quiet(rest[0], now=1) is False:
            try:
                a, b = rest[0].split("-")
                int(a.split(":")[0]), int(b.split(":")[1])
            except Exception:
                die("bad range, want HH:MM-HH:MM")
        cfg["quiet_hours"] = rest[0]
    save(cfg)
    print("quiet: %s" % (cfg["quiet_hours"] or "-"))


def cmd_focus(cfg, rest):
    if not rest or rest[0].lower() not in ("on", "off"):
        die("usage: kettle focus on | off")
    want = rest[0].lower() == "on"
    if want and PLAT != "darwin":
        die("focus detection is macOS-only right now - not enabling it on %s" % PLAT)
    cfg["only_when_unfocused"] = want
    save(cfg)
    print("focus: %s" % ("silent while the terminal is in front" if want else "always sound"))


def cmd_preset(cfg, rest):
    off = bool(rest) and rest[0].lower() == "off"
    for key in cfg["events"]:
        cfg["events"][key]["enabled"] = (not off) and key in RECOMMENDED
    save(cfg)
    print("preset: %s" % ("all events off" if off
                          else " ".join(sorted(KEY_TO_SHORT[k] for k in RECOMMENDED))))
    if not off and not cfg.get("enabled"):
        print("note: master switch is still off - run `kettle on`")


# ---------------------------------------------------------------- selftest

def selftest():
    for name, per_plat in ALIASES.items():
        for plat in ("darwin", "win32", "linux"):
            assert per_plat.get(plat), "alias %s missing %s" % (name, plat)
    # Two aliases resolving to the same file makes two events indistinguishable -
    # freedesktop has no dialog-question, so alert/soft/hmm silently collided on Linux.
    for plat in ("darwin", "win32", "linux"):
        first = [ALIASES[a][plat][0] for a in ALIASES]
        assert len(set(first)) == len(first), "%s aliases collide: %s" % (plat, first)
    # Everything an alias claims must exist on the platform we're running on.
    for name in ALIASES:
        assert resolve(name), "alias %r resolves to nothing on %s" % (name, PLAT)
    assert len({resolve(a) for a in ALIASES}) == len(ALIASES), "aliases resolve to the same file"

    assert in_quiet("22:00-09:00", now=23 * 60)      # inside, past midnight wrap
    assert in_quiet("22:00-09:00", now=2 * 60)       # inside, after midnight
    assert not in_quiet("22:00-09:00", now=12 * 60)  # outside
    assert in_quiet("09:00-17:00", now=12 * 60)      # inside, same-day range
    assert not in_quiet("09:00-17:00", now=23 * 60)
    assert not in_quiet("09:00-17:00", now=17 * 60)  # end is exclusive
    assert not in_quiet(None) and not in_quiet("garbage")

    assert _pad("abc", 6) == "abc   "
    assert _pad("API 出錯了", 12) == "API 出錯了  "   # 3 CJK glyphs = 6 columns, not 3
    assert _pad("x" * 40, 10).endswith("…") and len(_pad("x" * 40, 10)) == 10

    assert resolve("") is None
    assert resolve("definitely-not-a-real-sound-xyz") is None
    assert resolve("/definitely/not/here.wav") is None

    for key, ev in DEFAULTS["events"].items():
        assert ev.get("sounds") or ev.get("say"), "%s has nothing to play" % key
        for s in ev.get("sounds", []):
            assert s in ALIASES, "%s uses non-alias %r" % (key, s)
    assert RECOMMENDED <= set(DEFAULTS["events"])
    for key in RECOMMENDED:
        assert DEFAULTS["events"][key].get("enabled", True), "%s should default on" % key
    for key, ev in DEFAULTS["events"].items():
        if key not in RECOMMENDED:
            assert ev.get("enabled") is False, "%s should default off" % key
    assert DEFAULTS["enabled"] is False, "must install silent"

    assert set(KEY_TO_SHORT) == set(DEFAULTS["events"]), "EVENTS and DEFAULTS disagree"
    assert event_key("STOP") == "Stop"
    assert event_key("Notification:idle_prompt") == "Notification:idle_prompt"
    assert event_key("nope") is None
    assert not (set(EVENTS) & set(ALIASES)), "event and sound names must not collide"

    off = json.loads(json.dumps(DEFAULTS))
    assert fire(off, "Stop") == "muted (kettle on)"
    off["enabled"] = True
    assert fire(off, "PreCompact").startswith("event off")
    off["quiet_hours"] = "00:00-23:59"
    assert fire(off, "Stop").startswith("quiet hours")
    assert fire(off, "NoSuchEvent").startswith("no such event")

    pool = ["done", "up", "soft"]
    assert all(random.choice(pool) in pool for _ in range(50))

    # A configured event must replace its default, not merge with it, or swapping
    # a chime for say: would leave the old chime playing forever.
    global CONFIG
    orig, tmp = CONFIG, Path(__file__).parent / ".selftest.json"
    try:
        CONFIG = tmp
        save({"enabled": True, "events": {"Stop": {"say": "hi"}}})
        got = load()["events"]["Stop"]
        assert "sounds" not in got and got["say"] == "hi", got
        assert load()["events"]["SessionEnd"]["sounds"] == ["down"], "untouched events keep defaults"
    finally:
        tmp.unlink(missing_ok=True)
        CONFIG = orig

    print("selftest ok  (platform=%s, config=%s)" % (PLAT, CONFIG))


# ---------------------------------------------------------------- main

def main():
    argv = sys.argv[1:]

    if argv and argv[0] == "hook":
        # Hot path. Stay silent and exit 0 no matter what - hooks block the turn.
        try:
            fire(load(), argv[1] if len(argv) > 1 else "")
        except Exception:
            pass
        return 0

    if argv and argv[0] == "--selftest":
        selftest()
        return 0

    if argv and argv[0] in ("help", "-h", "--help"):
        print(USAGE)
        return 0

    cfg = load()
    if not argv:
        cmd_status(cfg)
        return 0

    head, rest = argv[0].lower(), argv[1:]
    if head in ("on", "off"):
        cmd_toggle(cfg, head == "on", rest)
    elif head == "test":
        cmd_test(cfg, rest)
    elif head == "list":
        cmd_list()
    elif head == "volume":
        cmd_volume(cfg, rest)
    elif head == "quiet":
        cmd_quiet(cfg, rest)
    elif head == "focus":
        cmd_focus(cfg, rest)
    elif head == "preset":
        cmd_preset(cfg, rest)
    elif head == "status":
        cmd_status(cfg)
    elif event_key(head):
        if not rest:
            die("usage: kettle %s <sound[,sound]> | say:text | off" % head)
        cmd_set(cfg, event_key(head), " ".join(rest))
    else:
        print("unknown: %s\n" % argv[0])
        print(USAGE)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
