# Contributing

**`main` is protected — every change lands through a pull request.** Direct pushes are
rejected, including from the maintainer. Fork, branch, PR.

---

## English

### Before you open a PR

```bash
python3 skills/sounds/scripts/sounds.py --selftest
```

That's the whole test suite and it must pass. There is no framework and none is wanted —
if you add non-trivial logic, add an `assert` to `selftest()`.

Then sanity-check the hot path, because hooks like `Stop` block a Claude turn until the
command returns:

```bash
time python3 skills/sounds/scripts/sounds.py hook Stop   # must stay well under 200ms
```

### What gets merged easily

- **Sound alias fallbacks for a platform you actually run.** The `ALIASES` table guesses
  at Windows and Linux filenames. If a name is wrong on your distro or Windows build,
  fix it — that's the single most useful contribution.
- **A Linux/Windows audio backend that's missing.** Add it to `_linux_player` or the
  PowerShell branch, in preference order, guarded by `shutil.which`.
- **A hook event worth hearing** that isn't wired up yet.
- **Translation fixes** to any of the three READMEs.

### What won't get merged

- New dependencies. This runs on stock Python 3 and whatever the OS already ships. That
  constraint is the point of the project, not an oversight.
- Config-file changes made outside the CLI, or a second way to configure things.
- Abstractions with one implementation.

### House rules

- One script, `skills/sounds/scripts/sounds.py`. Resist splitting it up.
- Playback is always detached (`Popen`, never `wait()`). A hook that waits on audio
  stalls every single Claude reply.
- A missing sound file is silence, never an error message — hook stderr pollutes the
  transcript.
- If you take a deliberate shortcut, mark it `# ponytail:` with the ceiling and the
  upgrade path.
- Bump `version` in `.claude-plugin/plugin.json`. The plugin cache is pinned per version,
  so without a bump nobody sees your change.

---

## 繁體中文

### 送 PR 之前

```bash
python3 skills/sounds/scripts/sounds.py --selftest
```

這就是全部的測試，一定要過。沒有測試框架，也不打算加 —— 如果你加了不平凡的邏輯，
就在 `selftest()` 裡補一條 `assert`。

然後量一下熱路徑，因為 `Stop` 這類 hook 會**卡住** Claude 那一輪直到指令回傳：

```bash
time python3 skills/sounds/scripts/sounds.py hook Stop   # 必須遠低於 200 毫秒
```

### 什麼樣的 PR 會很快被合併

- **你實際在用的平台的音效別名修正。** `ALIASES` 表對 Windows 和 Linux 的檔名是用猜的。
  如果某個名稱在你的發行版或 Windows 版本上是錯的，直接改掉 —— 這是最有價值的貢獻。
- **補上缺的 Linux / Windows 播放後端。** 加進 `_linux_player` 或 PowerShell 分支，
  照優先順序排，並用 `shutil.which` 判斷。
- **值得出聲但還沒接上的 hook 事件。**
- **三份 README 任何一份的翻譯修正。**

### 什麼不會被合併

- 新的相依套件。這個專案只跑在原生 Python 3 加作業系統本來就有的東西上。
  這個限制是專案的核心，不是還沒做完。
- 繞過 CLI 直接改設定檔，或是加第二套設定方式。
- 只有一種實作的抽象層。

### 規矩

- 就一支腳本 `skills/sounds/scripts/sounds.py`，不要拆。
- 播放一律 detach（`Popen`，永遠不要 `wait()`）。在 hook 裡等音效播完，
  Claude 每回一句話都會卡住。
- 找不到音效檔就是靜音，不要噴錯誤訊息 —— hook 的 stderr 會污染 transcript。
- 如果你刻意走捷徑，用 `# ponytail:` 標註它的天花板和之後怎麼補。
- 記得 bump `.claude-plugin/plugin.json` 的 `version`。plugin cache 是照版本號釘死的，
  不 bump 的話沒有人會看到你的改動。

---

## 简体中文

### 提 PR 之前

```bash
python3 skills/sounds/scripts/sounds.py --selftest
```

这就是全部的测试，必须通过。没有测试框架，也不打算加 —— 如果你加了不平凡的逻辑，
就在 `selftest()` 里补一条 `assert`。

然后量一下热路径，因为 `Stop` 这类 hook 会**阻塞** Claude 那一轮直到命令返回：

```bash
time python3 skills/sounds/scripts/sounds.py hook Stop   # 必须远低于 200 毫秒
```

### 什么样的 PR 会很快被合并

- **你实际在用的平台的声音别名修正。** `ALIASES` 表对 Windows 和 Linux 的文件名是猜的。
  如果某个名称在你的发行版或 Windows 版本上是错的，直接改掉 —— 这是最有价值的贡献。
- **补上缺失的 Linux / Windows 播放后端。** 加进 `_linux_player` 或 PowerShell 分支，
  按优先级排序，并用 `shutil.which` 判断。
- **值得出声但还没接上的 hook 事件。**
- **三份 README 任意一份的翻译修正。**

### 什么不会被合并

- 新的依赖。这个项目只跑在原生 Python 3 加操作系统本来就有的东西上。
  这个约束是项目的核心，不是还没做完。
- 绕过 CLI 直接改配置文件，或者加第二套配置方式。
- 只有一种实现的抽象层。

### 规矩

- 就一个脚本 `skills/sounds/scripts/sounds.py`，不要拆。
- 播放一律 detach（`Popen`，永远不要 `wait()`）。在 hook 里等音频播完，
  Claude 每回一句话都会卡住。
- 找不到声音文件就是静音，不要抛错误信息 —— hook 的 stderr 会污染 transcript。
- 如果你刻意走捷径，用 `# ponytail:` 标注它的天花板和以后怎么补。
- 记得 bump `.claude-plugin/plugin.json` 的 `version`。plugin cache 是按版本号钉死的，
  不 bump 的话没有人会看到你的改动。
