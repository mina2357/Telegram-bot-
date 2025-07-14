#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
خدمة التحقق من الأعضاء الجدد
New member verification service
"""

import logging
import random
from typing import Dict, Optional
from bot.utils.database import Database

logger = logging.getLogger(__name__)

class VerificationService:
    """
    خدمة التحقق من الأعضاء الجدد
    Service for verifying new members
    """
    
    def __init__(self):
        self.db = Database()
        self.verification_challenges = {}
        
        # أسئلة التحقق
        # Verification questions
        self.questions = [
            {
                "question": "كم عدد أيام الأسبوع؟",
                "correct": "7",
                "wrong": ["5", "6", "8", "10"]
            },
            {
                "question": "ما هو لون الشمس؟",
                "correct": "أصفر",
                "wrong": ["أحمر", "أزرق", "أخضر", "أسود"]
            },
            {
                "question": "كم عدد أصابع اليد الواحدة؟",
                "correct": "5",
                "wrong": ["4", "6", "3", "7"]
            },
            {
                "question": "ما هو الحيوان الذي يعطي الحليب؟",
                "correct": "البقرة",
                "wrong": ["الحصان", "الكلب", "القط", "الطائر"]
            },
            {
                "question": "في أي فصل تتساقط الأوراق؟",
                "correct": "الخريف",
                "wrong": ["الربيع", "الصيف", "الشتاء", "الصيف"]
            }
        ]
    
    async def create_challenge(self, chat_id: int, user_id: int) -> Optional[Dict]:
        """
        إنشاء تحدي التحقق
        Create verification challenge
        """
        try:
            # اختيار سؤال عشوائي
            # Select random question
            question = random.choice(self.questions)
            
            # إنشاء التحدي
            # Create challenge
            challenge = {
                "question": question["question"],
                "answer": question["correct"],
                "correct_answer": question["correct"],
                "wrong_answers": random.sample(question["wrong"], 3)
            }
            
            # حفظ التحدي
            # Save challenge
            challenge_key = f"{chat_id}_{user_id}"
            self.verification_challenges[challenge_key] = {
                "challenge": challenge,
                "attempts": 0,
                "max_attempts": 3
            }
            
            # حفظ في قاعدة البيانات
            # Save to database
            await self.db.save_verification_challenge(
                chat_id=chat_id,
                user_id=user_id,
                challenge=challenge
            )
            
            logger.info(f"تم إنشاء تحدي التحقق للمستخدم {user_id} في المجموعة {chat_id}")
            
            return challenge
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تحدي التحقق: {e}")
            return None
    
    async def verify_user(self, chat_id: int, user_id: int) -> bool:
        """
        التحقق من إجابة المستخدم
        Verify user answer
        """
        try:
            challenge_key = f"{chat_id}_{user_id}"
            
            if challenge_key in self.verification_challenges:
                # إزالة التحدي
                # Remove challenge
                del self.verification_challenges[challenge_key]
                
                # تحديث قاعدة البيانات
                # Update database
                await self.db.complete_verification(
                    chat_id=chat_id,
                    user_id=user_id,
                    success=True
                )
                
                logger.info(f"تم التحقق من المستخدم {user_id} بنجاح في المجموعة {chat_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من المستخدم: {e}")
            return False
    
    async def handle_wrong_answer(self, chat_id: int, user_id: int, context) -> bool:
        """
        معالجة الإجابة الخاطئة
        Handle wrong answer
        """
        try:
            challenge_key = f"{chat_id}_{user_id}"
            
            if challenge_key not in self.verification_challenges:
                return False
            
            # زيادة عدد المحاولات
            # Increase attempts
            self.verification_challenges[challenge_key]["attempts"] += 1
            attempts = self.verification_challenges[challenge_key]["attempts"]
            max_attempts = self.verification_challenges[challenge_key]["max_attempts"]
            
            # فحص إذا تم استنفاد المحاولات
            # Check if attempts exhausted
            if attempts >= max_attempts:
                # إزالة التحدي
                # Remove challenge
                del self.verification_challenges[challenge_key]
                
                # طرد المستخدم
                # Kick user
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                
                # تحديث قاعدة البيانات
                # Update database
                await self.db.complete_verification(
                    chat_id=chat_id,
                    user_id=user_id,
                    success=False
                )
                
                logger.info(f"تم طرد المستخدم {user_id} لفشل التحقق في المجموعة {chat_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإجابة الخاطئة: {e}")
            return False
    
    async def is_user_verified(self, chat_id: int, user_id: int) -> bool:
        """
        فحص إذا كان المستخدم متحققاً
        Check if user is verified
        """
        try:
            return await self.db.is_user_verified(chat_id, user_id)
        except Exception as e:
            logger.error(f"خطأ في فحص تحقق المستخدم: {e}")
            return False
    
    async def get_verification_stats(self, chat_id: int) -> Dict:
        """
        الحصول على إحصائيات التحقق
        Get verification statistics
        """
        try:
            return await self.db.get_verification_stats(chat_id)
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات التحقق: {e}")
            return {}
