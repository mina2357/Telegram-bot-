#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالجات الأوامر العامة
General command handlers
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config.settings import MESSAGES
from bot.utils.helpers import is_admin, get_user_mention

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    أمر البدء
    Start command
    """
    logger.info(f"Received /start command from user {update.effective_user.id}")
    user = update.effective_user
    
    if update.effective_chat.type == 'private':
        # رسالة خاصة
        # Private message
        welcome_text = (
            f"🤖 مرحباً {get_user_mention(user)}!\n\n"
            f"أنا بوت حماية المجموعات. يمكنني مساعدتك في:\n"
            f"• التحقق من الأعضاء الجدد\n"
            f"• فلترة الكلمات المحظورة\n"
            f"• منع السبام\n"
            f"• إدارة المجموعة\n\n"
            f"أضفني إلى مجموعتك واجعلني مشرفاً للاستفادة من جميع الميزات!"
        )
    else:
        # رسالة في المجموعة
        # Group message
        welcome_text = (
            f"👋 مرحباً! أنا بوت حماية المجموعات.\n"
            f"استخدم /help لمعرفة الأوامر المتاحة."
        )
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    أمر المساعدة
    Help command
    """
    logger.info(f"Received /help command from user {update.effective_user.id}")
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # أوامر عامة
    # General commands
    help_text = (
        "📋 **الأوامر المتاحة:**\n\n"
        "👥 **للجميع:**\n"
        "/start - بدء استخدام البوت\n"
        "/help - عرض هذه المساعدة\n"
        "/info - معلومات حول البوت\n\n"
    )
    
    # أوامر المشرفين
    # Admin commands
    if await is_admin(chat_id, user_id, context):
        help_text += (
            "🔐 **للمشرفين:**\n"
            "/ban - حظر عضو (رد على رسالته)\n"
            "/unban - إلغاء حظر عضو\n"
            "/mute - كتم عضو (رد على رسالته)\n"
            "/unmute - إلغاء كتم عضو (رد على رسالته)\n"
            "/warn - تحذير عضو (رد على رسالته)\n"
            "/addbad - إضافة كلمة مسيئة (تحذف الرسالة وتكتم المرسل)\n"
            "/listbad - عرض قائمة الكلمات المسيئة\n"
            "/stats - إحصائيات المجموعة\n"
            "/settings - إعدادات البوت\n\n"
        )
    
    help_text += (
        "💡 **ملاحظات:**\n"
        "• يجب أن يكون البوت مشرفاً للعمل بشكل صحيح\n"
        "• سيتم التحقق من الأعضاء الجدد تلقائياً\n"
        "• الكلمات المحظورة يتم فلترتها تلقائياً\n"
        "• السبام يتم اكتشافه ومنعه تلقائياً"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معلومات حول البوت
    Bot information
    """
    info_text = (
        "🤖 **معلومات البوت:**\n\n"
        "📌 **الاسم:** بوت حماية المجموعات\n"
        "🔢 **الإصدار:** 1.0.0\n"
        "🛡️ **الوظائف:**\n"
        "• التحقق من الأعضاء الجدد\n"
        "• فلترة الكلمات المحظورة\n"
        "• منع السبام والرسائل المتكررة\n"
        "• إدارة المجموعة (حظر، كتم، تحذير)\n"
        "• إحصائيات المجموعة\n\n"
        "👨‍💻 **المطور:** فريق التطوير\n"
        "📧 **الدعم:** للمساعدة، تواصل مع المطورين"
    )
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    إحصائيات المجموعة
    Group statistics
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if not await is_admin(chat_id, user_id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    try:
        # الحصول على معلومات المجموعة
        # Get group information
        chat = await context.bot.get_chat(chat_id)
        member_count = await context.bot.get_chat_member_count(chat_id)
        
        stats_text = (
            f"📊 **إحصائيات المجموعة:**\n\n"
            f"👥 **عدد الأعضاء:** {member_count}\n"
            f"📝 **اسم المجموعة:** {chat.title}\n"
            f"🆔 **معرف المجموعة:** `{chat_id}`\n\n"
            f"🛡️ **حالة الحماية:**\n"
            f"{'✅' if True else '❌'} فلترة الكلمات المحظورة\n"
            f"{'✅' if True else '❌'} منع السبام\n"
            f"{'✅' if True else '❌'} التحقق من الأعضاء الجدد\n"
            f"{'✅' if True else '❌'} الحماية من الغارات"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على إحصائيات المجموعة: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء الحصول على الإحصائيات.")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    إعدادات البوت
    Bot settings
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if not await is_admin(chat_id, user_id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    settings_text = (
        "⚙️ **إعدادات البوت:**\n\n"
        "لتغيير الإعدادات، استخدم الأوامر التالية:\n\n"
        "🔧 **الأوامر المتاحة:**\n"
        "/toggle_verification - تشغيل/إيقاف التحقق من الأعضاء\n"
        "/toggle_badwords - تشغيل/إيقاف فلترة الكلمات المحظورة\n"
        "/toggle_spam - تشغيل/إيقاف منع السبام\n"
        "/toggle_antiraid - تشغيل/إيقاف الحماية من الغارات\n\n"
        "📋 **الإعدادات الحالية:**\n"
        f"{'✅' if True else '❌'} التحقق من الأعضاء الجدد\n"
        f"{'✅' if True else '❌'} فلترة الكلمات المحظورة\n"
        f"{'✅' if True else '❌'} منع السبام\n"
        f"{'✅' if True else '❌'} الحماية من الغارات"
    )
    
    await update.message.reply_text(settings_text, parse_mode='Markdown')

def register_command_handlers(app):
    """
    تسجيل معالجات الأوامر
    Register command handlers
    """
    logger.info("Registering command handlers...")
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("settings", settings_command))
    logger.info("Command handlers registered successfully")
