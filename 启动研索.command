#!/bin/bash
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo '请先从 https://www.python.org/downloads/macos/ 安装 Python 3.10 或更高版本。'
  read -r -p '按回车关闭…'
  exit 1
fi
python3 - <<'PY'
import os
import subprocess
import sys
import time
import webbrowser
from urllib.request import urlopen

process = subprocess.Popen([sys.executable, 'server.py'], env={**os.environ, 'PORT': '8000'})
try:
    for _ in range(100):
        if process.poll() is not None:
            input('启动失败，请查看上方错误。按回车关闭…')
            sys.exit(1)
        try:
            with urlopen('http://127.0.0.1:8000/', timeout=.5) as response:
                ready = '德国中小企业' in response.read().decode('utf-8')
            if ready:
                webbrowser.open('http://localhost:8000')
                print('研索已启动。请保持此窗口打开；按 Control+C 停止。')
                break
        except OSError:
            pass
        time.sleep(.1)
    else:
        raise RuntimeError('启动超时，请查看错误信息。')
    process.wait()
except KeyboardInterrupt:
    pass
finally:
    if process.poll() is None:
        process.terminate()
        process.wait()
PY
