#!/usr/bin/env python3
"""
会议自动录制脚本
当检测到 Zoom 或 Google Meet 会议开始时，自动按下豆包的录制快捷键 Command+Shift+Z
"""

import subprocess
import time
import sys

# 确保输出立即刷新
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 配置
CHECK_INTERVAL = 2  # 检查间隔（秒）


def is_zoom_meeting():
    """检查是否在 Zoom 会议中"""
    try:
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
        if "meeting" in window_names:
            return True
        return False
    except Exception:
        return False


def is_google_meet():
    """检查是否在 Google Meet 会议中（真正加入会议，不是首页或等待页面）"""
    try:
        # 检查 Chrome 中是否有正在进行的 Google Meet 会议
        # URL 格式: meet.google.com/xxx-xxxx-xxx (会议中)
        # 排除: meet.google.com/landing (首页), meet.google.com/new (创建页面)
        script = '''
        tell application "System Events"
            if exists (process "Google Chrome") then
                tell application "Google Chrome"
                    set meetFound to false
                    repeat with w in windows
                        repeat with t in tabs of w
                            set tabURL to URL of t
                            set tabTitle to title of t
                            -- 检查是否是会议 URL (包含会议代码 xxx-xxxx-xxx)
                            -- 排除首页、创建页面等
                            if tabURL contains "meet.google.com/" then
                                if tabURL does not contain "/landing" and tabURL does not contain "/new" and tabURL does not contain "/lookup" then
                                    -- 检查标题是否表明在会议中 (不是 "Google Meet" 首页标题)
                                    if tabTitle does not start with "Google Meet" or tabTitle contains "Meet -" then
                                        set meetFound to true
                                        exit repeat
                                    end if
                                end if
                            end if
                        end repeat
                        if meetFound then exit repeat
                    end repeat
                    return meetFound
                end tell
            else
                return false
            end if
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False


def is_in_meeting():
    """检查是否在任何会议中"""
    return is_zoom_meeting() or is_google_meet()


def get_meeting_type():
    """获取当前会议类型"""
    if is_zoom_meeting():
        return "Zoom"
    if is_google_meet():
        return "Google Meet"
    return None


def trigger_doubao_record():
    """触发豆包录制快捷键 Command+Shift+Z"""
    try:
        script = '''
        tell application "System Events"
            key code 6 using {command down, shift down}
        end tell
        '''
        subprocess.run(["osascript", "-e", script], check=True)
        print("✓ 已触发豆包录制快捷键 (Command+Shift+Z)")
        return True
    except Exception as e:
        print(f"触发快捷键失败: {e}")
        return False


def main():
    print("=" * 50)
    print("会议自动录制脚本")
    print("支持: Zoom, Google Meet")
    print("检测到会议时将自动触发豆包录制")
    print("快捷键: Command+Shift+Z")
    print("=" * 50)
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("按 Ctrl+C 停止脚本")
    print("-" * 50)

    is_recording = False
    current_meeting_type = None

    try:
        while True:
            meeting_type = get_meeting_type()

            if meeting_type and not is_recording:
                # 会议开始，开始录制
                print(f"\n[{time.strftime('%H:%M:%S')}] 检测到 {meeting_type} 会议开始!")
                time.sleep(2)
                trigger_doubao_record()
                print("    → 开始录制")
                is_recording = True
                current_meeting_type = meeting_type

            elif not meeting_type and is_recording:
                # 会议结束
                print(f"\n[{time.strftime('%H:%M:%S')}] {current_meeting_type} 会议已结束")
                is_recording = False
                current_meeting_type = None

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n脚本已停止")


if __name__ == "__main__":
    main()
