#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالجات أوامر المشرفين
Admin command handlers
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler
from telegram.constants import ChatMemberStatus
from config.settings import MESSAGES, AUTHORIZED_ADMINS
from bot.utils.helpers import is_admin, get_user_mention
from bot.services.moderation_service import ModerationService
from bot.services.badwords_service import BadWordsService

logger = logging.getLogger(__name__)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    حظر عضو من المجموعة
    Ban a user from the group
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("يرجى الرد على رسالة العضو المراد حظره.")
        return
    
    user_to_ban = update.message.reply_to_message.from_user
    
    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_to_ban.id
        )
        
        await update.message.reply_text(
            f"✅ تم حظر {get_user_mention(user_to_ban)} من المجموعة."
        )
        
        logger.info(f"تم حظر المستخدم {user_to_ban.id} من المجموعة {update.effective_chat.id}")
        
    except Exception as e:
        logger.error(f"خطأ في حظر المستخدم: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء حظر العضو.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    إلغاء حظر عضو من المجموعة
    Unban a user from the group
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("يرجى إدخال معرف المستخدم أو الرد على رسالته.")
        return
    
    try:
        user_id = int(context.args[0])
        
        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id
        )
        
        await update.message.reply_text(f"✅ تم إلغاء حظر المستخدم {user_id}.")
        
        logger.info(f"تم إلغاء حظر المستخدم {user_id} من المجموعة {update.effective_chat.id}")
        
    except ValueError:
        await update.message.reply_text("❌ معرف المستخدم غير صحيح.")
    except Exception as e:
        logger.error(f"خطأ في إلغاء حظر المستخدم: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء إلغاء حظر العضو.")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    كتم عضو في المجموعة
    Mute a user in the group
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("يرجى الرد على رسالة العضو المراد كتمه.")
        return
    
    user_to_mute = update.message.reply_to_message.from_user
    duration = 60  # دقيقة واحدة افتراضياً
    
    if context.args:
        try:
            duration = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ مدة الكتم يجب أن تكون رقماً بالدقائق.")
            return
    
    moderation_service = ModerationService()
    success = await moderation_service.mute_user(
        chat_id=update.effective_chat.id,
        user_id=user_to_mute.id,
        duration=duration * 60,  # تحويل إلى ثواني
        context=context
    )
    
    if success:
        await update.message.reply_text(
            f"🔇 تم كتم {get_user_mention(user_to_mute)} لمدة {duration} دقيقة."
        )
    else:
        await update.message.reply_text("❌ حدث خطأ أثناء كتم العضو.")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    إلغاء كتم عضو في المجموعة
    Unmute a user in the group
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("يرجى الرد على رسالة العضو المراد إلغاء كتمه.")
        return
    
    user_to_unmute = update.message.reply_to_message.from_user
    
    moderation_service = ModerationService()
    success = await moderation_service.unmute_user(
        chat_id=update.effective_chat.id,
        user_id=user_to_unmute.id,
        context=context
    )
    
    if success:
        await update.message.reply_text(
            f"🔊 تم إلغاء كتم {get_user_mention(user_to_unmute)}."
        )
    else:
        await update.message.reply_text("❌ حدث خطأ أثناء إلغاء كتم العضو.")

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    تحذير عضو في المجموعة
    Warn a user in the group
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("يرجى الرد على رسالة العضو المراد تحذيره.")
        return
    
    user_to_warn = update.message.reply_to_message.from_user
    reason = " ".join(context.args) if context.args else "لا يوجد سبب محدد"
    
    moderation_service = ModerationService()
    warn_count = await moderation_service.warn_user(
        chat_id=update.effective_chat.id,
        user_id=user_to_warn.id,
        reason=reason
    )
    
    if warn_count > 0:
        await update.message.reply_text(
            f"⚠️ تم تحذير {get_user_mention(user_to_warn)}\n"
            f"عدد التحذيرات: {warn_count}/3\n"
            f"السبب: {reason}"
        )
    else:
        await update.message.reply_text("❌ حدث خطأ أثناء تحذير العضو.")

async def add_bad_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    إضافة كلمة مسيئة إلى قائمة المنع
    Add an offensive word to the ban list
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("🔐 هذا الأمر متاح للمشرفين فقط.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 الاستخدام: `/addbad كلمة_مسيئة`\n"
            "مثال: `/addbad كلمة_سيئة`"
        )
        return
    
    word_to_add = " ".join(context.args).strip()
    
    if not word_to_add:
        await update.message.reply_text("❌ يرجى إدخال كلمة صحيحة.")
        return
    
    badwords_service = BadWordsService()
    
    try:
        success = await badwords_service.add_offensive_word(word_to_add)
        
        if success:
            await update.message.reply_text(
                f"✅ تم إضافة الكلمة المسيئة بنجاح: `{word_to_add}`\n"
                f"سيتم حذف أي رسالة تحتوي عليها وكتم المرسل لمدة 5 دقائق.",
                parse_mode='Markdown'
            )
            logger.info(f"تم إضافة كلمة مسيئة جديدة: {word_to_add} بواسطة المشرف {update.effective_user.id}")
        else:
            await update.message.reply_text(
                f"❌ الكلمة `{word_to_add}` موجودة بالفعل في قائمة المنع.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"خطأ في إضافة كلمة مسيئة: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء إضافة الكلمة.")

async def list_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    عرض قائمة الكلمات المسيئة الحالية
    Show current list of offensive words
    """
    if not await is_admin(update.effective_chat.id, update.effective_user.id, context):
        await update.message.reply_text("🔐 هذا الأمر متاح للمشرفين فقط.")
        return
    
    badwords_service = BadWordsService()
    
    try:
        words_list = await badwords_service.get_badwords_list()
        words_count = await badwords_service.get_badwords_count()
        
        if words_count == 0:
            await update.message.reply_text("📝 لا توجد كلمات مسيئة في القائمة حالياً.")
            return
        
        # عرض أول 20 كلمة فقط لتجنب الرسائل الطويلة
        display_words = words_list[:20]
        remaining_count = words_count - 20
        
        message = f"📝 **قائمة الكلمات المسيئة** ({words_count} كلمة):\n\n"
        
        for i, word in enumerate(display_words, 1):
            message += f"{i}. `{word}`\n"
        
        if remaining_count > 0:
            message += f"\n... و {remaining_count} كلمة أخرى"
        
        message += "\n\n💡 استخدم `/addbad كلمة` لإضافة كلمة جديدة"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في عرض قائمة الكلمات المسيئة: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء عرض القائمة.")

def register_admin_handlers(app):
    """
    تسجيل معالجات أوامر المشرفين
    Register admin command handlers
    """
    logger.info("Registering admin handlers...")
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("warn", warn_user))
    app.add_handler(CommandHandler("addbad", add_bad_word))
    app.add_handler(CommandHandler("listbad", list_bad_words))
    logger.info("Admin handlers registered successfully")
