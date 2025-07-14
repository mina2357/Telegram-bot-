#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعدادات البوت الرئيسية
Main bot configuration settings
"""

import os
from typing import List

# إعدادات البوت الأساسية
# Basic bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", None)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# إعدادات قاعدة البيانات
# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_data.db")

# إعدادات التسجيل
# Logging settings
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOG_FILE = "bot.log"

# إعدادات التحقق
# Verification settings
VERIFICATION_TIMEOUT = 300  # 5 دقائق للتحقق
VERIFICATION_ATTEMPTS = 3   # عدد المحاولات المسموحة

# إعدادات الإشراف
# Moderation settings
MUTE_DURATION = 3600       # مدة الكتم بالثواني (ساعة واحدة)
WARN_LIMIT = 3             # عدد التحذيرات قبل الطرد
SPAM_THRESHOLD = 5         # عدد الرسائل المتتالية لاعتبارها سبام

# رسائل البوت بالعربية
# Bot messages in Arabic
MESSAGES = {
    "welcome": "🎉 مرحباً بك في المجموعة!\nيرجى التحقق من هويتك خلال 5 دقائق.",
    "verification_success": "✅ تم التحقق بنجاح! مرحباً بك في المجموعة.",
    "verification_failed": "❌ فشل في التحقق. تم طردك من المجموعة.",
    "verification_timeout": "⏰ انتهت مهلة التحقق. تم طردك من المجموعة.",
    "banned_word": "🚫 تم حذف رسالتك لاحتوائها على كلمات محظورة.",
    "user_warned": "⚠️ تم تحذيرك. التحذير رقم {count} من {limit}.",
    "user_muted": "🔇 تم كتم العضو لمدة {duration} دقيقة.",
    "user_kicked": "👋 تم طرد العضو من المجموعة.",
    "spam_detected": "🚨 تم اكتشاف سبام! تم حذف الرسائل.",
    "admin_only": "🔐 هذا الأمر متاح للمشرفين فقط.",
    "group_only": "👥 هذا الأمر يعمل في المجموعات فقط."
}

# قائمة المشرفين المخولين
# Authorized administrators list
AUTHORIZED_ADMINS: List[int] = []

# إعدادات الأمان
# Security settings
ENABLE_BADWORDS_FILTER = True
ENABLE_SPAM_DETECTION = True
ENABLE_VERIFICATION = True
ENABLE_ANTI_RAID = True

# قائمة المجموعات المسموحة (اختياري)
# Allowed groups list (optional)
ALLOWED_GROUPS: List[int] = []
