#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نقطة البداية الرئيسية للبوت
Main entry point for the Telegram group protection bot
"""

import logging
import os
from telegram.ext import Application, ContextTypes
from config.settings import BOT_TOKEN, WEBHOOK_URL, DEBUG
from bot.handlers import register_all_handlers
from bot.utils.logger import setup_logging

def main():
    """
    الوظيفة الرئيسية لتشغيل البوت
    Main function to start the bot
    """
    # إعداد نظام التسجيل
    # Setup logging system
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 بدء تشغيل بوت حماية المجموعات")
    
    # فحص وجود التوكن
    # Check if token exists
    if not BOT_TOKEN:
        logger.error("❌ لم يتم العثور على BOT_TOKEN في متغيرات البيئة")
        logger.error("❌ BOT_TOKEN environment variable not found")
        logger.error("يرجى إعداد متغير البيئة BOT_TOKEN بتوكن البوت من @BotFather")
        logger.error("Please set BOT_TOKEN environment variable with your bot token from @BotFather")
        return
    
    # إنشاء تطبيق البوت
    # Create bot application
    try:
        app = Application.builder().token(BOT_TOKEN).build()
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء تطبيق البوت: {e}")
        logger.error(f"❌ Error creating bot application: {e}")
        return
    
    # تسجيل جميع معالجات الأحداث
    # Register all event handlers
    try:
        register_all_handlers(app)
        logger.info("✅ جميع معالجات الأحداث تم تسجيلها بنجاح")
        logger.info("✅ All event handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ خطأ في تسجيل معالجات الأحداث: {e}")
        logger.error(f"❌ Error registering event handlers: {e}")
        return
    
    # تشغيل البوت
    # Start the bot
    try:
        if WEBHOOK_URL:
            logger.info("🌐 تشغيل البوت في وضع Webhook")
            app.run_webhook(
                listen="0.0.0.0",
                port=int(os.environ.get("PORT", 8000)),
                url_path=BOT_TOKEN,
                webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
            )
        else:
            logger.info("🔄 تشغيل البوت في وضع Polling")
            logger.info("Bot is ready to receive messages")
            app.run_polling(
                allowed_updates=['message', 'callback_query', 'chat_member'],
                drop_pending_updates=True
            )
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        logger.error(f"❌ Error starting bot: {e}")
        return

if __name__ == '__main__':
    main()
