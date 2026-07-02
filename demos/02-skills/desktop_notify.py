import platform
import subprocess
import sys

def run(title: str = "BYOE 提醒", message: str = "", **kwargs) -> str:
    """
    发送桌面系统通知。

    让 AI 可以在长时间任务完成后、或需要提醒用户时发送系统原生通知。
    支持 Windows (Toast)、macOS (Notification Center) 和 Linux (libnotify)。

    参数:
        title: 通知标题（默认: "BYOE 提醒"）
        message: 通知正文内容
    """
    system = platform.system()

    try:
        if system == "Windows":
            ps = f'''
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.BalloonTipTitle = "{title}"
$notify.BalloonTipText = "{message}"
$notify.Visible = $true
$notify.ShowBalloonTip(5000)
Start-Sleep -Seconds 5
$notify.Dispose()
'''
            subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, timeout=15)
            return f"✅ 已在 Windows 上发送通知：{title}"

        elif system == "Darwin":
            subprocess.run(["osascript", "-e",
                           f'display notification "{message}" with title "{title}"'],
                           capture_output=True, timeout=10)
            return f"✅ 已在 macOS 上发送通知：{title}"

        elif system == "Linux":
            subprocess.run(["notify-send", title, message],
                           capture_output=True, timeout=10)
            return f"✅ 已在 Linux 上发送通知：{title}"

        else:
            return f"❌ 不支持的操作系统：{system}"

    except FileNotFoundError as e:
        return f"❌ 当前系统缺少通知工具：{e}"
    except subprocess.TimeoutExpired:
        return "❌ 发送通知超时"
    except Exception as e:
        return f"❌ 通知发送失败：{e}"
