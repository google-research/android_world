import tkinter as tk
from tkinter import scrolledtext, filedialog
import subprocess
import threading
import os
import time

# 상수 정의
REASONING_ACTION = "com.example.REASONING_REQUEST"
REASONING_RECEIVER = "com.example.iotcore/com.example.adbinterface.receiver.AdbEventReceiver"
SIMULATION_RECEIVER = "com.example.iotcore/com.example.adbinterface.receiver.SimulationAdbCommandReceiver"
LOG_TAG = "GeminiResult"
PUSH_DIR = "/sdcard/Android/data/com.example.iotcore/files/ReasoningInput"

class ADBEventTool:
    def __init__(self, root):
        self.root = root
        self.root.title("ADB Event Tool")

        # 🧠 [1] Reasoning 기능
        tk.Label(root, text="ADB Reasoning 기능", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=4)

        self.send_button = tk.Button(root, text="Reasoning 요청 전송", command=self.send_reasoning_broadcast)
        self.send_button.grid(row=1, column=0, padx=5, pady=5)

        self.clear_button = tk.Button(root, text="전체 로그 초기화", command=self.clear_log)
        self.clear_button.grid(row=1, column=1, padx=5, pady=5)

        self.push_prompt_button = tk.Button(root, text="Prompt 저장 및 Push", command=self.save_and_push_prompt)
        self.push_prompt_button.grid(row=1, column=2, padx=5, pady=5)

        self.push_image_button = tk.Button(root, text="이미지 선택 및 Push", command=self.push_image)
        self.push_image_button.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(root, text="Prompt 입력").grid(row=2, column=0, columnspan=4)
        self.prompt_input = scrolledtext.ScrolledText(root, width=80, height=5, wrap=tk.WORD)
        self.prompt_input.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        tk.Label(root, text="Gemini 결과").grid(row=4, column=0, columnspan=4)
        self.result_output = scrolledtext.ScrolledText(root, width=80, height=5, wrap=tk.WORD)
        self.result_output.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

        # 🧪 ADB 로그 출력
        tk.Label(root, text="ADB 로그 출력").grid(row=6, column=0, columnspan=4)
        self.log_output = scrolledtext.ScrolledText(root, width=80, height=10, wrap=tk.WORD)
        self.log_output.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        # ▶️ [2] Simulation Action 전송
        tk.Label(root, text="Simulation Action 전송", font=("Arial", 10, "bold")).grid(row=8, column=0, columnspan=4, pady=(15, 0))

        self.simulation_input = tk.Entry(root, width=60)
        self.simulation_input.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

        self.simulation_button = tk.Button(root, text="시뮬레이션 전송", command=self.send_simulation_action)
        self.simulation_button.grid(row=9, column=3, padx=5, pady=5)

        # 초기 상태 변수
        self.keep_listening = True
        self.device_connected = False
        self.logcat_process = None

        # 스레드 시작
        self.device_check_thread = threading.Thread(target=self.monitor_devices, daemon=True)
        self.device_check_thread.start()

    def send_reasoning_broadcast(self):
        cmd = ["adb", "shell", "am", "broadcast", "-a", REASONING_ACTION, "-n", REASONING_RECEIVER]
        self.result_output.delete(1.0, tk.END)
        self.log_output.insert(tk.END, "[ADB] Reasoning 요청 전송\n")
        subprocess.run(cmd)

    def monitor_devices(self):
        while self.keep_listening:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            lines = result.stdout.strip().splitlines()
            devices = [line.split()[0] for line in lines[1:] if "device" in line]

            if devices and not self.device_connected:
                self.device_connected = True
                self.restart_logcat()
            elif not devices and self.device_connected:
                self.device_connected = False
                self.stop_logcat()

            time.sleep(3)

    def stop_logcat(self):
        if self.logcat_process:
            self.logcat_process.terminate()
            self.logcat_process = None

    def restart_logcat(self):
        self.stop_logcat()
        self.log_thread = threading.Thread(target=self.monitor_logcat, daemon=True)
        self.log_thread.start()

    def monitor_logcat(self):
        self.logcat_process = subprocess.Popen(
            ["adb", "logcat", f"{LOG_TAG}:I", "*:S"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8"
        )
        for line in self.logcat_process.stdout:
            if not self.keep_listening:
                break

            if LOG_TAG in line:
                parts = line.split(f"{LOG_TAG}:", 1)
                if len(parts) == 2:
                    reasoning_line = parts[1].strip()
                    self.result_output.insert(tk.END, reasoning_line + "\n")
                    self.result_output.see(tk.END)
                    self.log_output.insert(tk.END, "[ADB] Gemini 결과 수신됨\n")
                    self.log_output.see(tk.END)
            else:
                self.log_output.insert(tk.END, line)
                self.log_output.see(tk.END)

    def clear_log(self):
        self.log_output.delete(1.0, tk.END)
        self.result_output.delete(1.0, tk.END)

    def save_and_push_prompt(self):
        prompt_text = self.prompt_input.get("1.0", tk.END).strip()
        if not prompt_text:
            self.log_output.insert(tk.END, "[경고] Prompt 내용이 비어 있습니다.\n")
            return

        with open("prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt_text)

        cmd = ["adb", "push", "prompt.txt", f"{PUSH_DIR}/prompt.txt"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.log_output.insert(tk.END, "[ADB] prompt.txt push 결과:\n" + result.stdout + "\n")

    def push_image(self):
        file_path = filedialog.askopenfilename(title="이미지 파일 선택", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not file_path:
            self.log_output.insert(tk.END, "[취소] 이미지 선택이 취소되었습니다.\n")
            return

        file_name = os.path.basename(file_path)
        target_path = f"{PUSH_DIR}/{file_name}"

        cmd = ["adb", "push", file_path, target_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.log_output.insert(tk.END, f"[ADB] {file_name} push 결과:\n" + result.stdout + "\n")

    def send_simulation_action(self):
        user_input = self.simulation_input.get().strip()
        if not user_input:
            self.log_output.insert(tk.END, "[경고] 사용자 입력이 비어 있습니다.\n")
            return

        quoted_input = f"\"{user_input}\""

        cmd = [
            "adb", "shell", "am", "broadcast",
            "-n", SIMULATION_RECEIVER,
            "--es", "utterance", quoted_input
        ]
        self.log_output.insert(tk.END, f"[ADB] Simulation Action 전송: {quoted_input}\n")
        subprocess.run(cmd)

    def on_close(self):
        self.keep_listening = False
        self.stop_logcat()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ADBEventTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
