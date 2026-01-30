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


def get_zoom_meeting_id():
    """获取当前 Zoom 会议的窗口标题（用于区分不同会议）"""
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
        window_names = result.stdout.strip()
        window_names_lower = window_names.lower()

        # 检查是否是会议窗口
        meeting_indicators = ["zoom meeting", "meeting", "会议"]

        if window_names:
            for indicator in meeting_indicators:
                if indicator in window_names_lower:
                    return window_names  # 返回窗口标题作为会议标识
            # 如果窗口名不是简单的 "Zoom"，可能是会议
            if window_names_lower not in ["zoom", "zoom workplace", ""]:
                return window_names
        return None  # 没有会议
    except Exception as e:
        print(f"检查 Zoom 状态时出错: {e}")
        return None


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

    current_meeting_id = None  # 记录当前会议的标识

    try:
        while True:
            zoom_running = is_zoom_running()

            if not zoom_running:
                if current_meeting_id:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Zoom 已关闭")
                    current_meeting_id = None
                time.sleep(CHECK_INTERVAL)
                continue

            meeting_id = get_zoom_meeting_id()

            if meeting_id and meeting_id != current_meeting_id:
                # 新会议开始（包括第一次会议和切换到新会议）
                print(f"\n[{time.strftime('%H:%M:%S')}] 检测到新的 Zoom 会议!")
                print(f"    会议: {meeting_id}")
                # 等待一小段时间让会议窗口完全加载
                time.sleep(2)
                trigger_doubao_record()
                current_meeting_id = meeting_id

            elif not meeting_id and current_meeting_id:
                # 会议结束
                print(f"\n[{time.strftime('%H:%M:%S')}] Zoom 会议已结束")
                current_meeting_id = None

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n脚本已停止")


if __name__ == "__main__":
    main()
