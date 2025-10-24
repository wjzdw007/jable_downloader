#!/usr/bin/env python3
"""
Telegram 通知模块

支持两种配置方式：
1. 环境变量（推荐，更安全）
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_CHAT_ID="your_chat_id"

2. config.json 配置文件
   {
     "telegram": {
       "enabled": true,
       "bot_token": "your_token",
       "chat_id": "your_chat_id"
     }
   }

优先级：环境变量 > config.json
"""

import os
import requests
from config import CONF

# 尝试加载 .env 文件（如果安装了 python-dotenv）
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载 .env 文件到环境变量
except ImportError:
    # 没有安装 python-dotenv，跳过（仍然可以使用手动设置的环境变量）
    pass


def send_telegram_message(message, parse_mode='Markdown'):
    """
    发送 Telegram 消息

    Args:
        message: 消息内容（支持 Markdown 格式）
        parse_mode: 解析模式，默认 Markdown

    Returns:
        bool: 发送是否成功
    """
    telegram_config = CONF.get('telegram', {})

    # 优先使用环境变量（更安全）
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN') or telegram_config.get('bot_token')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID') or telegram_config.get('chat_id')

    # 如果设置了环境变量，自动启用
    enabled = bool(bot_token and chat_id) or telegram_config.get('enabled', False)

    if not enabled:
        return False

    if not bot_token or not chat_id:
        print("⚠️  Telegram 通知未配置，跳过")
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode
        }

        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            return True
        else:
            print(f"⚠️  Telegram 通知发送失败: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   错误详情: {error_detail}")
            except:
                print(f"   响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"⚠️  Telegram 通知发送异常: {str(e)}")
        return False


def send_download_success_notification(video_id, video_title, file_size=None, duration=None):
    """
    发送下载成功通知

    Args:
        video_id: 视频 ID
        video_title: 视频标题
        file_size: 文件大小（可选）
        duration: 下载耗时（可选，单位：秒）
    """
    message = f"✅ *视频下载完成*\n\n"
    message += f"*ID*: `{video_id}`\n"
    message += f"*标题*: {video_title}\n"

    if file_size:
        size_mb = file_size / (1024 * 1024)
        message += f"*大小*: {size_mb:.2f} MB\n"

    if duration:
        minutes = int(duration / 60)
        seconds = int(duration % 60)
        message += f"*耗时*: {minutes}分{seconds}秒\n"

    send_telegram_message(message)


def send_download_error_notification(video_id, video_title, error_msg):
    """
    发送下载失败通知

    Args:
        video_id: 视频 ID
        video_title: 视频标题
        error_msg: 错误信息
    """
    message = f"❌ *视频下载失败*\n\n"
    message += f"*ID*: `{video_id}`\n"
    message += f"*标题*: {video_title}\n"
    message += f"*错误*: {error_msg}\n"

    send_telegram_message(message)


def send_batch_complete_notification(total, success, failed, duration=None):
    """
    发送批量下载完成通知

    Args:
        total: 总数
        success: 成功数
        failed: 失败数
        duration: 总耗时（可选，单位：秒）
    """
    message = f"🎉 *批量下载完成*\n\n"
    message += f"*总数*: {total}\n"
    message += f"*成功*: {success} ✅\n"
    message += f"*失败*: {failed} ❌\n"

    if duration:
        hours = int(duration / 3600)
        minutes = int((duration % 3600) / 60)
        message += f"*总耗时*: {hours}小时{minutes}分钟\n"

    success_rate = (success / total * 100) if total > 0 else 0
    message += f"*成功率*: {success_rate:.1f}%\n"

    send_telegram_message(message)


def test_telegram_notification():
    """测试 Telegram 通知配置"""
    telegram_config = CONF.get('telegram', {})

    # 优先使用环境变量（更安全）
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN') or telegram_config.get('bot_token')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID') or telegram_config.get('chat_id')

    # 如果设置了环境变量，自动启用
    enabled = bool(bot_token and chat_id) or telegram_config.get('enabled', False)

    if not enabled:
        print("❌ Telegram 通知未启用")
        print("   请通过以下方式之一配置：")
        print("   1. 设置环境变量：TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
        print("   2. 在 config.json 中添加 telegram 配置")
        return False

    if not bot_token:
        print("❌ 缺少 bot_token")
        return False

    if not chat_id:
        print("❌ 缺少 chat_id")
        return False

    # 显示配置信息（隐藏敏感部分）
    print(f"✓ Bot Token: {bot_token[:10]}...{bot_token[-5:] if len(bot_token) > 15 else ''}")
    print(f"✓ Chat ID: {chat_id}")
    print()
    print("正在发送测试消息...")
    message = "🤖 *Jable Downloader 测试通知*\n\n"
    message += "如果你看到这条消息，说明 Telegram 通知配置成功！\n"
    message += "现在可以接收下载通知了 🎉"

    if send_telegram_message(message):
        print("✅ 测试消息发送成功！")
        print("   请检查 Telegram 是否收到消息")
        return True
    else:
        print("❌ 测试消息发送失败")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Telegram 通知配置测试")
    print("=" * 60)
    print()
    test_telegram_notification()
