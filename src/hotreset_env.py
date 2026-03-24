#
#   hotreset_env.py
#   PySpOS 热重启环境
#
#   By GoutouStdio
#   @ 2022~2026 GoutouStdio. Open all rights.

import os
import sys
import subprocess
import time

FLAG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.hotreset')

def set_flag():
    with open(FLAG_FILE, 'w') as f:
        f.write(str(time.time()))

def clear_flag():
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)

def check_flag():
    return os.path.exists(FLAG_FILE)

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    restart_count = 0
    
    while True:
        restart_count += 1
        clear_flag()
        
        cmd = [sys.executable, '-u', '-c', '''
import sys
sys._launcher_detected = True
for name in list(sys.modules.keys()):
    if not name.startswith('_') and not name.startswith('os') and name not in ('sys', 'builtins', '__builtin__', 'importlib', 'types'):
        del sys.modules[name]
import kernel
kernel.loop()
''']
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=script_dir,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            
            return_code = process.wait()
            
            if check_flag():
                continue
            else:
                break
                
        except KeyboardInterrupt:
            if process.poll() is None:
                process.terminate()
                process.wait()
            break
        except Exception as e:
            print(f"Error: {e}")
            break

def trigger():
    import printk
    printk.info("Hot resetting...")
    set_flag()
    sys.exit(42)

if __name__ == "__main__":
    run()
