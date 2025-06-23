import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from app.core.config import settings
from app.core.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)


class LanguageHandler:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'ru': 'Russian',
            'hi': 'Hindi'
        }
        
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text
        """
        try:
            # Check cache first
            cache_key = f"lang_detect:{hash(text)}"
            cached_lang = await redis_client.get(cache_key)
            if cached_lang:
                return cached_lang
            
            # Detect language
            detected_lang = detect(text)
            
            # Cache the result
            await redis_client.set(cache_key, detected_lang, expire=3600)
            
            return detected_lang if detected_lang in self.supported_languages else 'en'
            
        except LangDetectException:
            return 'en'  # Default to English
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return 'en'
    
    async def translate_text(self, text: str, target_language: str, source_language: str = None) -> str:
        """
        Translate text to target language using Google Translate API
        """
        try:
            if not settings.GOOGLE_TRANSLATE_API_KEY:
                logger.warning("Google Translate API key not configured")
                return text
            
            # Check cache first
            cache_key = f"translate:{hash(text)}:{source_language}:{target_language}"
            cached_translation = await redis_client.get(cache_key)
            if cached_translation:
                return cached_translation
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return text
            
            # Prepare API request
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': settings.GOOGLE_TRANSLATE_API_KEY,
                'q': text,
                'target': target_language,
                'format': 'text'
            }
            
            if source_language:
                params['source'] = source_language
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params)
                response.raise_for_status()
                
                result = response.json()
                translated_text = result['data']['translations'][0]['translatedText']
                
                # Cache the result
                await redis_client.set(cache_key, translated_text, expire=3600)
                
                return translated_text
                
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    async def get_language_name(self, language_code: str) -> str:
        """
        Get human-readable language name
        """
        return self.supported_languages.get(language_code, 'Unknown')
    
    async def is_supported_language(self, language_code: str) -> bool:
        """
        Check if language is supported
        """
        return language_code in self.supported_languages
    
    async def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages
        """
        return self.supported_languages.copy()


# Global instance
language_handler = LanguageHandler()