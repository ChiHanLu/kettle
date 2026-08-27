---
description: Turn Claude's sound cues on/off, change sounds, set volume or quiet hours
argument-hint: "[on|off|test|list|<event> <sound>|volume|quiet|focus|preset]"
allowed-tools: Bash(python3 *)
---

Run exactly this, then relay the output to the user verbatim (keep the table layout intact),
adding a one-line explanation in the user's language if it helps:

```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/kettle/scripts/kettle.py" $ARGUMENTS
```

If the user described what they want in prose instead of CLI syntax
("make the done sound quieter", "shut up after 10pm", "I want a voice when it errors out"),
translate it into the right subcommand first — see the `kettle` skill for the full mapping —
then run it. Never hand-edit `~/.claude/kettle/config.json`; always go through the CLI.
