#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالجات الإشراف والتحكم
Moderation and control handlers
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config.settings import ENABLE_BADWORDS_FILTER, ENABLE_SPAM_DETECTION, MESSAGES
from bot.services.moderation_service import ModerationService
from bot.services.badwords_service import BadWordsService
from bot.utils.helpers import is_admin

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة الرسائل للإشراف
    Handle messages for moderation
    """
    logger.info(f"Received message update: {update}")
    
    if not update.message or not update.message.text:
        logger.info("No message or text content, skipping")
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    logger.info(f"Processing message from user {user_id} in chat {chat_id}: {message_text[:50]}...")
    
    # تجاهل رسائل المشرفين
    # Ignore admin messages
    if await is_admin(chat_id, user_id, context):
        return
    
    moderation_service = ModerationService()
    
    # فحص الكلمات المحظورة والمسيئة
    # Check for banned and offensive words
    if ENABLE_BADWORDS_FILTER:
        badwords_service = BadWordsService()
        if await badwords_service.contains_offensive_word(message_text):
            try:
                # حذف الرسالة فوراً
                # Delete the message immediately
                await update.message.delete()
                
                # كتم المستخدم لمدة 5 دقائق (300 ثانية)
                # Mute the user for 5 minutes (300 seconds)
                mute_duration = 300
                mute_success = await moderation_service.mute_user(
                    chat_id=chat_id,
                    user_id=user_id,
                    duration=mute_duration,
                    context=context
                )
                
                if mute_success:
                    # إرسال تحذير بالعربية
                    # Send warning in Arabic
                    warning_message = await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🚫 {update.effective_user.mention_html()}\n"
                             f"تم حذف رسالتك لاحتوائها على كلمات مسيئة وتم كتمك لمدة 5 دقائق.\n"
                             f"يُرجى احترام قوانين المجموعة.",
                        parse_mode='HTML'
                    )
                else:
                    # إرسال تحذير بدون كتم إذا فشل الكتم
                    # Send warning without mute if muting failed
                    warning_message = await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🚫 {update.effective_user.mention_html()}\n"
                             f"تم حذف رسالتك لاحتوائها على كلمات مسيئة.\n"
                             f"يُرجى احترام قوانين المجموعة.",
                        parse_mode='HTML'
                    )
                
                # حذف رسالة التحذير بعد 15 ثانية
                # Delete warning message after 15 seconds
                context.job_queue.run_once(
                    delete_message,
                    15,
                    data={'chat_id': chat_id, 'message_id': warning_message.message_id}
                )
                
                # تسجيل مخالفة
                # Log violation
                await moderation_service.log_violation(
                    chat_id=chat_id,
                    user_id=user_id,
                    violation_type="offensive_word",
                    content=message_text
                )
                
                logger.info(f"تم حذف رسالة تحتوي على كلمات مسيئة وكتم المستخدم {user_id}")
                
            except Exception as e:
                logger.error(f"خطأ في معالجة الكلمة المسيئة: {e}")
            
            return
    
    # فحص السبام
    # Check for spam
    if ENABLE_SPAM_DETECTION:
        is_spam = await moderation_service.check_spam(
            chat_id=chat_id,
            user_id=user_id,
            message_text=message_text
        )
        
        if is_spam:
            try:
                # حذف الرسالة
                # Delete the message
                await update.message.delete()
                
                # كتم المستخدم مؤقتاً
                # Temporarily mute user
                await moderation_service.mute_user(
                    chat_id=chat_id,
                    user_id=user_id,
                    duration=300,  # 5 دقائق
                    context=context
                )
                
                # إرسال تحذير
                # Send warning
                spam_message = await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🚨 {update.effective_user.mention_html()}, "
                         f"تم اكتشاف سبام! تم كتمك لمدة 5 دقائق.",
                    parse_mode='HTML'
                )
                
                # حذف رسالة التحذير بعد 15 ثانية
                # Delete warning message after 15 seconds
                context.job_queue.run_once(
                    delete_message,
                    15,
                    data={'chat_id': chat_id, 'message_id': spam_message.message_id}
                )
                
                logger.info(f"تم كتم المستخدم {user_id} لإرسال سبام")
                
            except Exception as e:
                logger.error(f"خطأ في معالجة السبام: {e}")
            
            return
    
    # تسجيل الرسالة للإحصائيات
    # Log message for statistics
    await moderation_service.log_message(
        chat_id=chat_id,
        user_id=user_id,
        message_text=message_text
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة الصور المرسلة
    Handle sent photos
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # تجاهل رسائل المشرفين
    # Ignore admin messages
    if await is_admin(chat_id, user_id, context):
        return
    
    moderation_service = ModerationService()
    
    # فحص إذا كان العضو مكتوماً
    # Check if user is muted
    is_muted = await moderation_service.is_user_muted(chat_id, user_id)
    
    if is_muted:
        try:
            await update.message.delete()
            logger.info(f"تم حذف صورة من مستخدم مكتوم {user_id}")
        except Exception as e:
            logger.error(f"خطأ في حذف صورة من مستخدم مكتوم: {e}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة الملفات المرسلة
    Handle sent documents
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # تجاهل رسائل المشرفين
    # Ignore admin messages
    if await is_admin(chat_id, user_id, context):
        return
    
    moderation_service = ModerationService()
    
    # فحص إذا كان العضو مكتوماً
    # Check if user is muted
    is_muted = await moderation_service.is_user_muted(chat_id, user_id)
    
    if is_muted:
        try:
            await update.message.delete()
            logger.info(f"تم حذف ملف من مستخدم مكتوم {user_id}")
        except Exception as e:
            logger.error(f"خطأ في حذف ملف من مستخدم مكتوم: {e}")

async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    """
    حذف رسالة مجدولة
    Delete a scheduled message
    """
    job_data = context.job.data
    chat_id = job_data['chat_id']
    message_id = job_data['message_id']
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.error(f"خطأ في حذف الرسالة المجدولة: {e}")

def register_moderation_handlers(app):
    """
    تسجيل معالجات الإشراف
    Register moderation handlers
    """
    logger.info("Registering moderation handlers...")
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    logger.info("Moderation handlers registered successfully")
