---
id: l10
title: "Running commands: subprocess, pathlib and logging"
quiz: quiz-01.yaml
resources: [../resources/ch04/disk_report_broken.py, ../resources/ch04/disk_report_solution.py, ../resources/ch04/disk_report_test.py]
sources: [17, 19, 27, 39, 40, 114]
---
After this lesson you can run an external command safely from Python, handle its failure modes, use `pathlib` and `logging` instead of string paths and `print`, set a meaningful exit code, and find the four classic bugs in a short ops script.

## Shortcut

Download the three `disk_report_*.py` files into one folder. This is a fix-the-bug exercise, so the test file targets the broken script by default:

```bash
python disk_report_test.py                      # tests disk_report_broken.py: fails
python disk_report_test.py disk_report_solution # tests the fixed version: passes
```

In the course's test run the broken script printed `FAILED (failures=6, errors=2)` out of 10 tests, and the solution printed `Ran 10 tests` and `OK` on Python 3.13 and 3.11. No test runs a real command: `run_df` takes the runner as an argument and the tests pass a fake one.

## subprocess.run

`subprocess.run(args, ...)` runs a command, waits for it and returns a `CompletedProcess`; the docs recommend it for every case it can handle [27]. The arguments that matter:

| Argument | Effect |
| --- | --- |
| `args` | A list such as `["df", "-P", "-k", path]`. A sequence is generally preferred over a string [27]. |
| `capture_output=True` | Captures stdout and stderr [27]. |
| `text=True` | Decodes to `str`. By default the streams are binary, so captured output is `bytes` [27]. |
| `check=True` | A non-zero exit code raises `CalledProcessError`, which holds the exit code, `cmd` and any captured output [27]. |
| `timeout=10` | On expiry the child is killed and waited for, then `TimeoutExpired` is raised [27]. |
| `shell=True` | Runs the command through a shell. Avoid unless you need pipes or wildcards [27]. |

The result has `returncode` (0 usually means success; a negative `-N` means the child was killed by signal N on POSIX), `stdout` and `stderr` [27].

```python
import subprocess
result = subprocess.run(["ls", "-l", "/dev/null"], capture_output=True, text=True, check=True, timeout=10)
print(result.returncode, result.stdout)
```

**Why a list and not a string.** The library never implicitly calls a shell, so every character, shell metacharacters included, reaches the child as plain data [27]. With `shell=True` it is your job to quote everything, "to avoid shell injection vulnerabilities" [27]. `f"df -k {path}"` with `path = "/tmp; rm -rf ~"` becomes two commands. If you start from a command-line string, `shlex.split()` makes the list [27].

**Errors.** `CalledProcessError` and `TimeoutExpired` both derive from `SubprocessError` [27]. Starting a program that does not exist raises `OSError` [27], so a robust wrapper catches all three. Output captured in `TimeoutExpired` is bytes even with `text=True` [27].

## pathlib in one screen

`pathlib.Path` replaces `os.path` string juggling [40]:

```python
from pathlib import Path
p = Path("/var/log") / "vmapi" / "app.log"      # the / operator joins
p.name, p.suffix, p.parent                       # ('app.log', '.log', PosixPath('/var/log/vmapi'))
p.exists(), p.is_file()
text = p.read_text()                             # opens, reads, closes
Path("out").mkdir(parents=True, exist_ok=True)   # like mkdir -p
sorted(Path(".").glob("*.py"))                   # glob results come in no particular order
```

`glob()` returns matches in no particular order, so sort when order matters [40]. `write_text()` overwrites an existing file [40].

## logging, not print

Use one logger per module: `logger = logging.getLogger(__name__)`, and call `debug`, `info`, `warning`, `error` or `critical` on it [39]. The default level is `WARNING`, so `info` messages vanish unless you configure logging [39]. Configure once, at program start, before any logger calls:

```python
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger.warning("%s is %d%% full", mount, percent)    # arguments, not an f-string
```

Why not `print`? The HOWTO's table sends ordinary console output to `print()`, but events in the normal operation of a program, status monitoring and fault investigation to a logger [39]. A logger has levels you can filter, timestamps and a destination you can change without editing every call.

## Exit codes and sys.exit

A script tells its caller (cron, CI, a shell `&&`) whether it worked through its exit code. `sys.exit(n)` raises `SystemExit`; an integer is the exit status and zero means success, `None` means zero, and any other object is printed to stderr with exit code 1 [17]. `SystemExit` is not a subclass of `Exception` [19], so a bare `except Exception` does not swallow it. Keep a `main()` that returns an int and call `sys.exit(main())` at the bottom: easy to test and explicit about codes.

## The fix-the-bug exercise: disk_report (20 minutes)

`disk_report_broken.py` parses `df -P -k` output (`-P` is POSIX output format and `-k` means 1K blocks [114]) and warns about full filesystems. It runs. Four bugs are planted; the tests fail until you fix them. The functions take a `runner` argument so no real command runs.

**Hints.** (1) Look at how the command line is built. (2) What happens when `df` exits with 1? (3) What type is `result.stdout`? (4) Count the header lines against the slice.

### Walkthrough

1. **`shell=True` with an interpolated path.** `runner(f"df -P -k {path}", shell=True, ...)` is injectable. Fix: `["df", "-P", "-k", path]`, no shell. [27]
2. **Unchecked return code.** Without `check=True` a failed `df` returns empty output, and the report says "nothing is full". Fix: `check=True`; `main()` already maps the exception to exit code 2. [27]
3. **bytes versus str.** Without `text=True`, `result.stdout` is `bytes`, and `parse_df` calls `.splitlines()` and `.rstrip("%")` with `str` arguments, which fails on bytes. Fix: `text=True`. [27]
4. **Off by one.** `text.splitlines()[2:]` skips the header and the first filesystem. Fix: `[1:]`.

The same family of mistakes covers units. The 1024-blocks column is in KiB, so GiB is `/ 1024 / 1024`; dividing once labels MiB as GiB. The test file checks `97.9` GiB for `102687672` blocks.

**Complexity.** `parse_df` is O(L) for L lines; one `df` process per path. Alternative: `shutil.disk_usage()` avoids the subprocess and the text parsing entirely (not covered by this course's sources).

## Gotchas

- **`shell=True` with user input.** Injection. Pass a list. [27]
- **Ignoring `returncode`.** Without `check=True` a failure looks like empty success. [27]
- **Forgetting `text=True`.** Output is bytes by default. [27]
- **No `timeout`.** A hung command hangs the script; on timeout the child is killed and `TimeoutExpired` is raised. [27]
- **`print` for diagnostics.** No levels, no timestamps, and it mixes with real output. Use a module logger. [39]
- **`except Exception` around `sys.exit`.** `SystemExit` is not an `Exception`, so it passes through; but `except:` or `BaseException` would catch it. [19]
- **`Popen.wait()` with `stdout=PIPE`.** For enough output the child can block and the call deadlocks; use `communicate()` or `run()`. [27]

:::low-confidence
The exercise parses the six-column layout shown in the starter and was run only on synthetic text, never on a real `df`. Output on your system may differ in columns or wrapping; check `man df` before trusting the parser on real hosts.
:::

:::key-takeaways
- Pass a list to `subprocess.run`; add `capture_output=True, text=True, check=True, timeout=...`. [27]
- Catch `CalledProcessError`, `TimeoutExpired` and `OSError` at the edge; map them to an exit code. [27]
- `pathlib.Path` with `/`, `read_text`, `glob` replaces `os.path` strings. [40]
- One logger per module, configured once with `basicConfig`; default level is WARNING. [39]
- `sys.exit(int)` sets the exit status; `SystemExit` is not an `Exception`. [17] [19]
:::

:::glossary
- **Shell injection**: tricking a command run through a shell into executing extra commands hidden in its input.
- **Exit code**: the small integer a process returns to its caller; zero means success.
- **CalledProcessError**: the exception `subprocess.run` raises when `check=True` and the command exits non-zero.
- **TimeoutExpired**: the exception raised when a command runs longer than its timeout.
- **pathlib**: the standard library module that represents file paths as objects.
- **logger**: an object that records messages at a level such as INFO or ERROR and sends them to handlers.
- **runner**: here, the function passed in to run commands, so tests can replace it.
:::
