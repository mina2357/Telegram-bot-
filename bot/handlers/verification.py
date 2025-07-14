#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالجات التحقق من الأعضاء الجدد
New member verification handlers
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ChatMemberStatus
from config.settings import MESSAGES, ENABLE_VERIFICATION
from bot.services.verification_service import VerificationService
from bot.utils.helpers import get_user_mention

logger = logging.getLogger(__name__)

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة الأعضاء الجدد
    Handle new members joining the group
    """
    if not ENABLE_VERIFICATION:
        return
    
    chat_member = update.chat_member
    
    # التحقق من انضمام عضو جديد
    # Check if a new member joined
    if (chat_member.old_chat_member.status == ChatMemberStatus.LEFT and 
        chat_member.new_chat_member.status == ChatMemberStatus.MEMBER):
        
        user = chat_member.new_chat_member.user
        chat_id = update.effective_chat.id
        
        # تجاهل البوتات
        # Ignore bots
        if user.is_bot:
            return
        
        logger.info(f"عضو جديد انضم للمجموعة: {user.id}")
        
        verification_service = VerificationService()
        
        # إنشاء تحدي التحقق
        # Create verification challenge
        challenge = await verification_service.create_challenge(chat_id, user.id)
        
        if challenge:
            # إرسال رسالة التحقق
            # Send verification message
            keyboard = InlineKeyboardButton(
                text=f"✅ {challenge['answer']}",
                callback_data=f"verify_{user.id}_{challenge['correct_answer']}"
            )
            
            # إضافة خيارات خاطئة
            # Add wrong options
            buttons = [keyboard]
            for wrong_answer in challenge['wrong_answers']:
                buttons.append(InlineKeyboardButton(
                    text=f"❌ {wrong_answer}",
                    callback_data=f"verify_{user.id}_wrong"
                ))
            
            # خلط الأزرار
            # Shuffle buttons
            import random
            random.shuffle(buttons)
            
            reply_markup = InlineKeyboardMarkup([buttons])
            
            welcome_message = (
                f"🎉 مرحباً {get_user_mention(user)}!\n\n"
                f"للتحقق من هويتك، يرجى حل هذا السؤال:\n"
                f"❓ {challenge['question']}\n\n"
                f"⏰ لديك 5 دقائق للإجابة"
            )
            
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=welcome_message,
                reply_markup=reply_markup
            )
            
            # جدولة حذف الرسالة والعضو في حالة عدم التحقق
            # Schedule message deletion and member removal if verification fails
            context.job_queue.run_once(
                verification_timeout,
                300,  # 5 دقائق
                data={
                    'chat_id': chat_id,
                    'user_id': user.id,
                    'message_id': message.message_id
                }
            )

async def handle_verification_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة استجابة التحقق
    Handle verification callback
    """
    query = update.callback_query
    await query.answer()
    
    # تحليل البيانات
    # Parse callback data
    data_parts = query.data.split('_')
    if len(data_parts) != 3:
        return
    
    action, user_id, answer = data_parts
    user_id = int(user_id)
    
    # التحقق من أن المستخدم الصحيح يجيب
    # Verify that the correct user is answering
    if query.from_user.id != user_id:
        await query.answer("❌ هذا التحقق ليس لك!", show_alert=True)
        return
    
    verification_service = VerificationService()
    
    if answer == "wrong":
        # إجابة خاطئة
        # Wrong answer
        await verification_service.handle_wrong_answer(
            chat_id=query.message.chat.id,
            user_id=user_id,
            context=context
        )
        
        await query.edit_message_text(
            "❌ إجابة خاطئة! حاول مرة أخرى.\n"
            "⚠️ إذا فشلت في 3 محاولات، ستتم إزالتك من المجموعة."
        )
    else:
        # إجابة صحيحة
        # Correct answer
        success = await verification_service.verify_user(
            chat_id=query.message.chat.id,
            user_id=user_id
        )
        
        if success:
            await query.edit_message_text(
                f"✅ تم التحقق بنجاح!\n"
                f"مرحباً بك {get_user_mention(query.from_user)} في المجموعة!"
            )
        else:
            await query.edit_message_text("❌ حدث خطأ أثناء التحقق.")

async def verification_timeout(context: ContextTypes.DEFAULT_TYPE):
    """
    معالجة انتهاء وقت التحقق
    Handle verification timeout
    """
    job_data = context.job.data
    chat_id = job_data['chat_id']
    user_id = job_data['user_id']
    message_id = job_data['message_id']
    
    try:
        # حذف رسالة التحقق
        # Delete verification message
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        
        # طرد العضو
        # Remove member
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        
        # إرسال رسالة إشعار
        # Send notification message
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ انتهت مهلة التحقق للعضو {user_id}. تم طرده من المجموعة."
        )
        
        logger.info(f"تم طرد العضو {user_id} لعدم التحقق في الوقت المحدد")
        
    except Exception as e:
        logger.error(f"خطأ في معالجة انتهاء وقت التحقق: {e}")

def register_verification_handlers(app):
    """
    تسجيل معالجات التحقق
    Register verification handlers
    """
    app.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CallbackQueryHandler(handle_verification_callback, pattern="^verify_"))
