#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
خدمة الإشراف والتحكم
Moderation and control service
"""

import logging
import time
from typing import Dict, List, Optional
from collections import defaultdict
from telegram.ext import ContextTypes
from telegram import ChatPermissions
from bot.utils.database import Database
from config.settings import SPAM_THRESHOLD, WARN_LIMIT

logger = logging.getLogger(__name__)

class ModerationService:
    """
    خدمة الإشراف والتحكم
    Moderation and control service
    """
    
    def __init__(self):
        self.db = Database()
        self.user_messages = defaultdict(list)  # تتبع رسائل المستخدمين
        self.muted_users = {}  # المستخدمين المكتومين
        self.user_warnings = defaultdict(int)  # تحذيرات المستخدمين
    
    async def check_spam(self, chat_id: int, user_id: int, message_text: str) -> bool:
        """
        فحص السبام
        Check for spam
        """
        try:
            current_time = time.time()
            user_key = f"{chat_id}_{user_id}"
            
            # تنظيف الرسائل القديمة (أكثر من دقيقة)
            # Clean old messages (older than 1 minute)
            self.user_messages[user_key] = [
                msg for msg in self.user_messages[user_key]
                if current_time - msg['time'] < 60
            ]
            
            # إضافة الرسالة الحالية
            # Add current message
            self.user_messages[user_key].append({
                'text': message_text,
                'time': current_time
            })
            
            # فحص عدد الرسائل
            # Check message count
            recent_messages = len(self.user_messages[user_key])
            
            if recent_messages >= SPAM_THRESHOLD:
                # فحص إذا كانت الرسائل متشابهة
                # Check if messages are similar
                recent_texts = [msg['text'] for msg in self.user_messages[user_key][-5:]]
                similar_count = sum(1 for text in recent_texts if text == message_text)
                
                if similar_count >= 3:
                    logger.info(f"تم اكتشاف سبام من المستخدم {user_id} في المجموعة {chat_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص السبام: {e}")
            return False
    
    async def mute_user(self, chat_id: int, user_id: int, duration: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        كتم مستخدم
        Mute a user
        """
        try:
            # صلاحيات الكتم
            # Mute permissions
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_send_polls=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            
            # تطبيق الكتم
            # Apply mute
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
                until_date=int(time.time()) + duration
            )
            
            # حفظ معلومات الكتم
            # Save mute information
            mute_key = f"{chat_id}_{user_id}"
            self.muted_users[mute_key] = {
                'until': time.time() + duration,
                'duration': duration
            }
            
            # حفظ في قاعدة البيانات
            # Save to database
            await self.db.save_mute(
                chat_id=chat_id,
                user_id=user_id,
                duration=duration,
                reason="تم الكتم من قبل المشرف"
            )
            
            logger.info(f"تم كتم المستخدم {user_id} لمدة {duration} ثانية في المجموعة {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في كتم المستخدم: {e}")
            return False
    
    async def unmute_user(self, chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        إلغاء كتم مستخدم
        Unmute a user
        """
        try:
            # صلاحيات عادية
            # Normal permissions
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
            
            # إلغاء الكتم
            # Remove mute
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions
            )
            
            # إزالة من قائمة المكتومين
            # Remove from muted list
            mute_key = f"{chat_id}_{user_id}"
            if mute_key in self.muted_users:
                del self.muted_users[mute_key]
            
            # تحديث قاعدة البيانات
            # Update database
            await self.db.remove_mute(chat_id=chat_id, user_id=user_id)
            
            logger.info(f"تم إلغاء كتم المستخدم {user_id} في المجموعة {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إلغاء كتم المستخدم: {e}")
            return False
    
    async def is_user_muted(self, chat_id: int, user_id: int) -> bool:
        """
        فحص إذا كان المستخدم مكتوماً
        Check if user is muted
        """
        try:
            mute_key = f"{chat_id}_{user_id}"
            
            if mute_key in self.muted_users:
                mute_info = self.muted_users[mute_key]
                
                # فحص إذا انتهت مدة الكتم
                # Check if mute duration has expired
                if time.time() > mute_info['until']:
                    del self.muted_users[mute_key]
                    return False
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص كتم المستخدم: {e}")
            return False
    
    async def warn_user(self, chat_id: int, user_id: int, reason: str) -> int:
        """
        تحذير مستخدم
        Warn a user
        """
        try:
            warn_key = f"{chat_id}_{user_id}"
            self.user_warnings[warn_key] += 1
            
            warn_count = self.user_warnings[warn_key]
            
            # حفظ التحذير في قاعدة البيانات
            # Save warning to database
            await self.db.save_warning(
                chat_id=chat_id,
                user_id=user_id,
                reason=reason,
                count=warn_count
            )
            
            logger.info(f"تم تحذير المستخدم {user_id} ({warn_count}/{WARN_LIMIT}) في المجموعة {chat_id}")
            
            return warn_count
            
        except Exception as e:
            logger.error(f"خطأ في تحذير المستخدم: {e}")
            return 0
    
    async def get_user_warnings(self, chat_id: int, user_id: int) -> int:
        """
        الحصول على عدد تحذيرات المستخدم
        Get user warning count
        """
        try:
            warn_key = f"{chat_id}_{user_id}"
            return self.user_warnings.get(warn_key, 0)
        except Exception as e:
            logger.error(f"خطأ في الحصول على تحذيرات المستخدم: {e}")
            return 0
    
    async def clear_user_warnings(self, chat_id: int, user_id: int) -> bool:
        """
        مسح تحذيرات المستخدم
        Clear user warnings
        """
        try:
            warn_key = f"{chat_id}_{user_id}"
            if warn_key in self.user_warnings:
                del self.user_warnings[warn_key]
            
            await self.db.clear_warnings(chat_id=chat_id, user_id=user_id)
            
            logger.info(f"تم مسح تحذيرات المستخدم {user_id} في المجموعة {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في مسح تحذيرات المستخدم: {e}")
            return False
    
    async def log_violation(self, chat_id: int, user_id: int, violation_type: str, content: str):
        """
        تسجيل مخالفة
        Log a violation
        """
        try:
            await self.db.log_violation(
                chat_id=chat_id,
                user_id=user_id,
                violation_type=violation_type,
                content=content
            )
            
            logger.info(f"تم تسجيل مخالفة {violation_type} للمستخدم {user_id} في المجموعة {chat_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل المخالفة: {e}")
    
    async def log_message(self, chat_id: int, user_id: int, message_text: str):
        """
        تسجيل رسالة للإحصائيات
        Log message for statistics
        """
        try:
            await self.db.log_message(
                chat_id=chat_id,
                user_id=user_id,
                message_text=message_text
            )
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الرسالة: {e}")
    
    async def get_moderation_stats(self, chat_id: int) -> Dict:
        """
        الحصول على إحصائيات الإشراف
        Get moderation statistics
        """
        try:
            return await self.db.get_moderation_stats(chat_id)
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الإشراف: {e}")
            return {}
