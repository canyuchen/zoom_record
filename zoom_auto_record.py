#!/usr/bin/env python3
"""
Zoom 会议自动录制脚本
当检测到 Zoom 会议开始时，自动按下豆包的录制快捷键 Command+Shift+Z
"""

import subprocess
import time
import sys

# 确保输出立即刷新
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 配置
CHECK_INTERVAL = 2  # 检查间隔（秒）
ZOOM_PROCESS_NAME = "zoom.us"  # Zoom 进程名


def is_in_meeting():
    """检查是否在 Zoom 会议中"""
    try:
        # 使用 AppleScript 检查 Zoom 窗口标题
        script = '''
        tell application "System Events"
            if exists (process "zoom.us") then
                tell process "zoom.us"
                    set windowNames to name of every window
                    return windowNames as string
                end tell
            else
                return ""
            end if
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        window_names = result.stdout.strip().lower()

        # 只要窗口名包含 "meeting" 就认为在会议中
        if "meeting" in window_names:
            return True
        return False
    except Exception as e:
        print(f"检查 Zoom 状态时出错: {e}")
        return False


def is_zoom_running():
    """检查 Zoom 是否正在运行"""
    try:
        result = subprocess.run(
            ["pgrep", "-x", ZOOM_PROCESS_NAME],
            capture_output=True
        )
        return result.returncode == 0
    except Exception:
        return False


def trigger_doubao_record():
    """触发豆包录制快捷键 Command+Shift+Z"""
    try:
        script = '''
        tell application "System Events"
            key code 6 using {command down, shift down}
        end tell
        '''
        # key code 6 是 Z 键
        subprocess.run(["osascript", "-e", script], check=True)
        print("✓ 已触发豆包录制快捷键 (Command+Shift+Z)")
        return True
    except Exception as e:
        print(f"触发快捷键失败: {e}")
        return False


def main():
    print("=" * 50)
    print("Zoom 会议自动录制脚本")
    print("检测到 Zoom 会议时将自动触发豆包录制")
    print("快捷键: Command+Shift+Z")
    print("=" * 50)
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("按 Ctrl+C 停止脚本")
    print("-" * 50)

    is_recording = False  # 是否正在录制

    try:
        while True:
            zoom_running = is_zoom_running()

            if not zoom_running:
                if is_recording:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Zoom 已关闭")
                    is_recording = False
                time.sleep(CHECK_INTERVAL)
                continue

            in_meeting = is_in_meeting()

            if in_meeting and not is_recording:
                # 会议开始，开始录制
                print(f"\n[{time.strftime('%H:%M:%S')}] 检测到 Zoom 会议开始!")
                # 等待一小段时间让会议窗口完全加载
                time.sleep(2)
                trigger_doubao_record()  # 开始录制
                print("    → 开始录制")
                is_recording = True

            elif not in_meeting and is_recording:
                # 会议结束
                print(f"\n[{time.strftime('%H:%M:%S')}] Zoom 会议已结束")
                is_recording = False

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n脚本已停止")


if __name__ == "__main__":
    main()
