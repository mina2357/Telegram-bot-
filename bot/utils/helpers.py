#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
الدوال المساعدة للبوت
Bot helper functions
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from telegram import User, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

logger = logging.getLogger(__name__)

async def is_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    فحص إذا كان المستخدم مشرفاً
    Check if user is an admin
    """
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"خطأ في فحص صلاحيات المشرف: {e}")
        return False

async def is_bot_admin(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    فحص إذا كان البوت مشرفاً
    Check if bot is an admin
    """
    try:
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        return bot_member.status == ChatMemberStatus.ADMINISTRATOR
    except Exception as e:
        logger.error(f"خطأ في فحص صلاحيات البوت: {e}")
        return False

def get_user_mention(user: User) -> str:
    """
    الحصول على منشن المستخدم
    Get user mention
    """
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return f"[{user.first_name}](tg://user?id={user.id})"
    else:
        return f"[User](tg://user?id={user.id})"

def get_user_display_name(user: User) -> str:
    """
    الحصول على اسم المستخدم للعرض
    Get user display name
    """
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif user.username:
        return user.username
    else:
        return f"User {user.id}"

def format_time(seconds: int) -> str:
    """
    تنسيق الوقت بالثواني إلى نص مقروء
    Format time in seconds to readable text
    """
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقيقة"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ساعة"
    else:
        days = seconds // 86400
        return f"{days} يوم"

def format_datetime(dt: datetime) -> str:
    """
    تنسيق التاريخ والوقت
    Format datetime
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_duration(duration_str: str) -> Optional[int]:
    """
    تحليل مدة زمنية من نص
    Parse duration from text
    """
    try:
        duration_str = duration_str.lower().strip()
        
        if duration_str.endswith('s') or duration_str.endswith('ث'):
            return int(duration_str[:-1])
        elif duration_str.endswith('m') or duration_str.endswith('د'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('h') or duration_str.endswith('س'):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith('d') or duration_str.endswith('ي'):
            return int(duration_str[:-1]) * 86400
        else:
            # افتراض أنه بالدقائق
            # Assume it's in minutes
            return int(duration_str) * 60
    except ValueError:
        return None

def escape_markdown(text: str) -> str:
    """
    تشفير نص لاستخدامه في Markdown
    Escape text for use in Markdown
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def clean_text(text: str) -> str:
    """
    تنظيف النص من الأحرف غير المرغوب فيها
    Clean text from unwanted characters
    """
    # إزالة الأحرف الخاصة والرموز
    # Remove special characters and symbols
    import re
    
    # الاحتفاظ بالأحرف العربية والإنجليزية والأرقام والفراغات
    # Keep Arabic, English letters, numbers, and spaces
    cleaned = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\s]', '', text)
    
    # إزالة الفراغات الإضافية
    # Remove extra spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

def is_arabic_text(text: str) -> bool:
    """
    فحص إذا كان النص يحتوي على أحرف عربية
    Check if text contains Arabic characters
    """
    import re
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(arabic_pattern.search(text))

def get_file_size_mb(file_size_bytes: int) -> float:
    """
    تحويل حجم الملف من بايت إلى ميجابايت
    Convert file size from bytes to MB
    """
    return round(file_size_bytes / (1024 * 1024), 2)

def is_valid_username(username: str) -> bool:
    """
    فحص صحة اسم المستخدم
    Validate username
    """
    import re
    
    # اسم المستخدم يجب أن يبدأ بحرف ويحتوي على أحرف وأرقام و _ فقط
    # Username should start with letter and contain only letters, numbers, and _
    pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    return bool(pattern.match(username)) and len(username) >= 3

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    قطع النص إلى الحد المسموح
    Truncate text to maximum length
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

async def send_typing_action(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """
    إرسال إشارة الكتابة
    Send typing action
    """
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception as e:
        logger.error(f"خطأ في إرسال إشارة الكتابة: {e}")

def get_command_args(text: str) -> list:
    """
    استخراج معاملات الأمر من النص
    Extract command arguments from text
    """
    parts = text.split()
    if len(parts) > 1:
        return parts[1:]
    return []

def build_keyboard_from_list(items: list, columns: int = 2) -> list:
    """
    بناء لوحة مفاتيح من قائمة
    Build keyboard from list
    """
    keyboard = []
    for i in range(0, len(items), columns):
        row = items[i:i + columns]
        keyboard.append(row)
    return keyboard
