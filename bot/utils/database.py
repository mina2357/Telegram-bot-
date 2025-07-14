#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إدارة قاعدة البيانات
Database management
"""

import logging
import sqlite3
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """
    فئة إدارة قاعدة البيانات
    Database management class
    """
    
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """
        تهيئة قاعدة البيانات
        Initialize database
        """
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.create_tables()
            logger.info("تم تهيئة قاعدة البيانات بنجاح")
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
    
    def create_tables(self):
        """
        إنشاء جداول قاعدة البيانات
        Create database tables
        """
        try:
            cursor = self.connection.cursor()
            
            # جدول المستخدمين
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_banned BOOLEAN DEFAULT FALSE,
                    UNIQUE(user_id, chat_id)
                )
            ''')
            
            # جدول التحقق
            # Verification table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    challenge_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    success BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # جدول الإشراف
            # Moderation table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderation_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    admin_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    reason TEXT,
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول التحذيرات
            # Warnings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    reason TEXT,
                    count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المخالفات
            # Violations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    violation_type TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الرسائل
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الكتم
            # Mutes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mutes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    duration INTEGER NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            self.connection.commit()
            logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول قاعدة البيانات: {e}")
    
    async def save_user(self, user_id: int, chat_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None):
        """
        حفظ بيانات المستخدم
        Save user data
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, chat_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, chat_id, username, first_name, last_name))
            
            self.connection.commit()
            logger.debug(f"تم حفظ بيانات المستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات المستخدم: {e}")
    
    async def save_verification_challenge(self, chat_id: int, user_id: int, challenge: Dict):
        """
        حفظ تحدي التحقق
        Save verification challenge
        """
        try:
            cursor = self.connection.cursor()
            challenge_data = str(challenge)
            
            cursor.execute('''
                INSERT INTO verifications (chat_id, user_id, challenge_data)
                VALUES (?, ?, ?)
            ''', (chat_id, user_id, challenge_data))
            
            self.connection.commit()
            logger.debug(f"تم حفظ تحدي التحقق للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ تحدي التحقق: {e}")
    
    async def complete_verification(self, chat_id: int, user_id: int, success: bool):
        """
        إكمال التحقق
        Complete verification
        """
        try:
            cursor = self.connection.cursor()
            
            # تحديث حالة التحقق
            cursor.execute('''
                UPDATE verifications 
                SET completed_at = CURRENT_TIMESTAMP, success = ?
                WHERE chat_id = ? AND user_id = ? AND completed_at IS NULL
            ''', (success, chat_id, user_id))
            
            # تحديث حالة المستخدم
            if success:
                cursor.execute('''
                    UPDATE users 
                    SET is_verified = TRUE
                    WHERE chat_id = ? AND user_id = ?
                ''', (chat_id, user_id))
            
            self.connection.commit()
            logger.debug(f"تم إكمال التحقق للمستخدم {user_id}: {success}")
            
        except Exception as e:
            logger.error(f"خطأ في إكمال التحقق: {e}")
    
    async def is_user_verified(self, chat_id: int, user_id: int) -> bool:
        """
        فحص إذا كان المستخدم متحققاً
        Check if user is verified
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT is_verified FROM users 
                WHERE chat_id = ? AND user_id = ?
            ''', (chat_id, user_id))
            
            result = cursor.fetchone()
            return result['is_verified'] if result else False
            
        except Exception as e:
            logger.error(f"خطأ في فحص تحقق المستخدم: {e}")
            return False
    
    async def save_mute(self, chat_id: int, user_id: int, duration: int, reason: str):
        """
        حفظ معلومات الكتم
        Save mute information
        """
        try:
            cursor = self.connection.cursor()
            expires_at = datetime.now().timestamp() + duration
            
            cursor.execute('''
                INSERT INTO mutes (chat_id, user_id, duration, reason, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (chat_id, user_id, duration, reason, expires_at))
            
            self.connection.commit()
            logger.debug(f"تم حفظ معلومات الكتم للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ معلومات الكتم: {e}")
    
    async def remove_mute(self, chat_id: int, user_id: int):
        """
        إزالة الكتم
        Remove mute
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE mutes 
                SET is_active = FALSE
                WHERE chat_id = ? AND user_id = ? AND is_active = TRUE
            ''', (chat_id, user_id))
            
            self.connection.commit()
            logger.debug(f"تم إزالة الكتم للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في إزالة الكتم: {e}")
    
    async def save_warning(self, chat_id: int, user_id: int, reason: str, count: int):
        """
        حفظ التحذير
        Save warning
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO warnings (chat_id, user_id, reason, count)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, user_id, reason, count))
            
            self.connection.commit()
            logger.debug(f"تم حفظ التحذير للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ التحذير: {e}")
    
    async def clear_warnings(self, chat_id: int, user_id: int):
        """
        مسح التحذيرات
        Clear warnings
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                DELETE FROM warnings 
                WHERE chat_id = ? AND user_id = ?
            ''', (chat_id, user_id))
            
            self.connection.commit()
            logger.debug(f"تم مسح التحذيرات للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في مسح التحذيرات: {e}")
    
    async def log_violation(self, chat_id: int, user_id: int, violation_type: str, content: str):
        """
        تسجيل مخالفة
        Log violation
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO violations (chat_id, user_id, violation_type, content)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, user_id, violation_type, content))
            
            self.connection.commit()
            logger.debug(f"تم تسجيل مخالفة {violation_type} للمستخدم {user_id}")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل المخالفة: {e}")
    
    async def log_message(self, chat_id: int, user_id: int, message_text: str):
        """
        تسجيل رسالة
        Log message
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO messages (chat_id, user_id, message_text)
                VALUES (?, ?, ?)
            ''', (chat_id, user_id, message_text))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل الرسالة: {e}")
    
    async def get_verification_stats(self, chat_id: int) -> Dict:
        """
        الحصول على إحصائيات التحقق
        Get verification statistics
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_verifications,
                    COUNT(CASE WHEN success = 1 THEN 1 END) as successful_verifications,
                    COUNT(CASE WHEN success = 0 THEN 1 END) as failed_verifications
                FROM verifications 
                WHERE chat_id = ?
            ''', (chat_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else {}
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات التحقق: {e}")
            return {}
    
    async def get_moderation_stats(self, chat_id: int) -> Dict:
        """
        الحصول على إحصائيات الإشراف
        Get moderation statistics
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_actions,
                    COUNT(CASE WHEN action_type = 'mute' THEN 1 END) as mutes,
                    COUNT(CASE WHEN action_type = 'ban' THEN 1 END) as bans,
                    COUNT(CASE WHEN action_type = 'warn' THEN 1 END) as warnings
                FROM moderation_actions 
                WHERE chat_id = ?
            ''', (chat_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else {}
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الإشراف: {e}")
            return {}
    
    def close(self):
        """
        إغلاق الاتصال بقاعدة البيانات
        Close database connection
        """
        if self.connection:
            self.connection.close()
            logger.info("تم إغلاق الاتصال بقاعدة البيانات")
