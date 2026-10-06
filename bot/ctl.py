import sys
from .control import read_control, read_status, update_control

HELP = """usage: python -m bot.ctl <command>
  status    show mode, equity, positions, last actions
  pause     stop all trading (open positions are left as they are)
  resume    resume trading
  flatten   sell every position, then pause
  stop      shut the bot down"""


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "status":
        print(read_status() or "no status yet (is the bot running?)"); print(read_control())
    elif cmd == "pause": update_control(paused=True); print("paused")
    elif cmd == "resume": update_control(paused=False, flatten=False); print("resumed")
    elif cmd == "flatten": update_control(flatten=True); print("flatten requested")
    elif cmd == "stop": update_control(stop=True); print("stop requested")
    else: print(HELP); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
