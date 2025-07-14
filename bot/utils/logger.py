#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام التسجيل للبوت
Bot logging system
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from config.settings import LOG_LEVEL, LOG_FILE, DEBUG

def setup_logging():
    """
    إعداد نظام التسجيل
    Setup logging system
    """
    
    # إنشاء مُسجل رئيسي
    # Create main logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # تنسيق الرسائل
    # Message formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # معالج وحدة التحكم
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # معالج الملف (إذا لم يكن في وضع التطوير)
    # File handler (if not in development mode)
    if not DEBUG:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # إعداد مُسجل telegram
    # Setup telegram logger
    telegram_logger = logging.getLogger('telegram')
    telegram_logger.setLevel(logging.INFO)
    
    # إعداد مُسجل httpx
    # Setup httpx logger
    httpx_logger = logging.getLogger('httpx')
    httpx_logger.setLevel(logging.WARNING)
    
    logger.info("تم إعداد نظام التسجيل بنجاح")
