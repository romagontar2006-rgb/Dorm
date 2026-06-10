import subprocess
import sys
import os
import webbrowser
import time
import threading
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000/admin.html")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Якщо сервер вже запущений — просто відкрий браузер
    if is_port_in_use(8000):
        webbrowser.open("http://127.0.0.1:8000")
        return

    # Відкриваємо браузер в окремому потоці
    t = threading.Thread(target=open_browser)
    t.daemon = True
    t.start()

    # Запускаємо сервер
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app", "--host", "127.0.0.1", "--port", "8000"
    ])

if __name__ == "__main__":
    main()