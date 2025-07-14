#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالجات الأحداث للبوت
Event handlers for the bot
"""

from .admin import register_admin_handlers
from .verification import register_verification_handlers
from .moderation import register_moderation_handlers
from .commands import register_command_handlers

def register_all_handlers(app):
    """
    تسجيل جميع معالجات الأحداث
    Register all event handlers
    """
    register_command_handlers(app)
    register_verification_handlers(app)
    register_moderation_handlers(app)
    register_admin_handlers(app)
