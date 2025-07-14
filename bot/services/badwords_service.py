#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
خدمة فلترة الكلمات المحظورة
Bad words filtering service
"""

import logging
import re
from typing import List, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class BadWordsService:
    """
    خدمة فلترة الكلمات المحظورة
    Bad words filtering service
    """
    
    def __init__(self):
        self.badwords: Set[str] = set()
        self.badwords_patterns: List[re.Pattern] = []
        self.load_badwords()
    
    def load_badwords(self):
        """
        تحميل قائمة الكلمات المحظورة
        Load bad words list
        """
        try:
            badwords_file = Path("data/badwords.txt")
            
            if badwords_file.exists():
                with open(badwords_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word and not word.startswith('#'):
                            self.badwords.add(word.lower())
                            
                            # إنشاء نمط للكلمة مع مراعاة الاختلافات
                            # Create pattern for word with variations
                            pattern = self._create_pattern(word)
                            self.badwords_patterns.append(re.compile(pattern, re.IGNORECASE))
                
                logger.info(f"تم تحميل {len(self.badwords)} كلمة محظورة")
            else:
                logger.warning("ملف الكلمات المحظورة غير موجود")
                
        except Exception as e:
            logger.error(f"خطأ في تحميل الكلمات المحظورة: {e}")
    
    def _create_pattern(self, word: str) -> str:
        """
        إنشاء نمط للكلمة مع مراعاة الاختلافات
        Create pattern for word with variations
        """
        # استبدال الأحرف المشابهة
        # Replace similar characters
        replacements = {
            'ا': '[اأإآ]',
            'ة': '[ةه]',
            'ي': '[يى]',
            'و': '[وؤ]',
            'ء': '[ءئ]'
        }
        
        pattern = word
        for char, replacement in replacements.items():
            pattern = pattern.replace(char, replacement)
        
        # إضافة فراغات اختيارية
        # Add optional spaces
        pattern = '\\s*'.join(pattern)
        
        return f'\\b{pattern}\\b'
    
    async def contains_badword(self, text: str) -> bool:
        """
        فحص إذا كان النص يحتوي على كلمات محظورة
        Check if text contains bad words
        """
        try:
            if not text:
                return False
            
            text_lower = text.lower()
            
            # فحص الكلمات المباشرة
            # Check direct words
            for badword in self.badwords:
                if badword in text_lower:
                    logger.info(f"تم اكتشاف كلمة محظورة: {badword}")
                    return True
            
            # فحص الأنماط
            # Check patterns
            for pattern in self.badwords_patterns:
                if pattern.search(text):
                    logger.info(f"تم اكتشاف كلمة محظورة بواسطة النمط: {pattern.pattern}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص الكلمات المحظورة: {e}")
            return False
    
    async def filter_text(self, text: str) -> str:
        """
        فلترة النص وحذف الكلمات المحظورة
        Filter text and remove bad words
        """
        try:
            if not text:
                return text
            
            filtered_text = text
            
            # استبدال الكلمات المحظورة
            # Replace bad words
            for pattern in self.badwords_patterns:
                filtered_text = pattern.sub('***', filtered_text)
            
            return filtered_text
            
        except Exception as e:
            logger.error(f"خطأ في فلترة النص: {e}")
            return text
    
    async def add_badword(self, word: str) -> bool:
        """
        إضافة كلمة محظورة
        Add a bad word
        """
        try:
            word_lower = word.lower().strip()
            
            if word_lower and word_lower not in self.badwords:
                self.badwords.add(word_lower)
                
                # إنشاء نمط للكلمة الجديدة
                # Create pattern for new word
                pattern = self._create_pattern(word_lower)
                self.badwords_patterns.append(re.compile(pattern, re.IGNORECASE))
                
                # حفظ في الملف
                # Save to file
                badwords_file = Path("data/badwords.txt")
                with open(badwords_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{word_lower}")
                
                logger.info(f"تم إضافة كلمة محظورة جديدة: {word_lower}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إضافة كلمة محظورة: {e}")
            return False
    
    async def remove_badword(self, word: str) -> bool:
        """
        إزالة كلمة محظورة
        Remove a bad word
        """
        try:
            word_lower = word.lower().strip()
            
            if word_lower in self.badwords:
                self.badwords.remove(word_lower)
                
                # إزالة النمط
                # Remove pattern
                self.badwords_patterns = [
                    pattern for pattern in self.badwords_patterns
                    if word_lower not in pattern.pattern
                ]
                
                # تحديث الملف
                # Update file
                badwords_file = Path("data/badwords.txt")
                with open(badwords_file, 'w', encoding='utf-8') as f:
                    for badword in sorted(self.badwords):
                        f.write(f"{badword}\n")
                
                logger.info(f"تم إزالة كلمة محظورة: {word_lower}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إزالة كلمة محظورة: {e}")
            return False
    
    async def get_badwords_count(self) -> int:
        """
        الحصول على عدد الكلمات المحظورة
        Get bad words count
        """
        return len(self.badwords)
    
    async def get_badwords_list(self) -> List[str]:
        """
        الحصول على قائمة الكلمات المحظورة
        Get bad words list
        """
        return sorted(list(self.badwords))
    
    async def add_offensive_word(self, word: str) -> bool:
        """
        إضافة كلمة مسيئة جديدة مع تحديث فوري للنظام
        Add new offensive word with immediate system update
        """
        try:
            word = word.strip().lower()
            if not word:
                return False
                
            if word in self.badwords:
                return False  # الكلمة موجودة بالفعل
                
            # إضافة الكلمة إلى المجموعة
            self.badwords.add(word)
            
            # إنشاء نمط للكلمة الجديدة
            pattern = self._create_pattern(word)
            self.badwords_patterns.append(re.compile(pattern, re.IGNORECASE))
            
            # حفظ الكلمة في الملف
            badwords_file = Path("data/badwords.txt")
            with open(badwords_file, 'a', encoding='utf-8') as f:
                f.write(f"\n# كلمة مسيئة مضافة من قبل المشرف\n{word}")
            
            logger.info(f"تمت إضافة كلمة مسيئة جديدة: {word}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة كلمة مسيئة: {e}")
            return False
    
    async def contains_offensive_word(self, text: str) -> bool:
        """
        فحص إذا كان النص يحتوي على كلمات مسيئة
        Check if text contains offensive words
        """
        return await self.contains_badword(text)
