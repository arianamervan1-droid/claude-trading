"""File-based remote control: `python -m bot.ctl <cmd>` writes control.json, the bot reads it every few seconds."""
import json, os, tempfile

CONTROL = os.getenv("BOT_CONTROL_FILE", "control.json")
STATUS = os.getenv("BOT_STATUS_FILE", "status.json")
DEFAULT = {"paused": False, "flatten": False, "stop": False}


def _read(path, default):
    try:
        with open(path) as f:
            return {**default, **json.load(f)}
    except (FileNotFoundError, ValueError):
        return dict(default)


def _write(path, data):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, path)


def read_control(): return _read(CONTROL, DEFAULT)
def update_control(**kw): _write(CONTROL, {**read_control(), **kw})
def read_status(): return _read(STATUS, {})
def write_status(**kw): _write(STATUS, kw)
