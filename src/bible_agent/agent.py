

import logging
from sentient_agent_framework import (
    AbstractAgent,
    Session,
    Query,
    ResponseHandler
)
from .bible_service import BibleService
from .llm_service import LLMService
from utils.verse_parser import VerseParser
from utils.cache import CacheManager
from config.bible_config import BibleConfig
from config.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class BibleAgent(AbstractAgent):
    """
    Bible Verse Agent - Fetches and explains Bible verses.
    
    Features:
    - Fetches verses from bible-api.com
    - Uses FireworksAI Llama for explanations
    - Caches results for faster responses
    - Smart verse reference parsing
    """
    
    GREETING_PATTERNS = [
        "who are you",
        "what can you do",
        "hello",
        "hi",
        "hey",
        "help",
        "about"
    ]
    
    def __init__(self, name: str = "Bible Verse Agent"):
        super().__init__(name)
        
        logger.info(f"📖 Initializing {name}...")
        
        # Initialize services
        self.bible_service = BibleService()
        self.llm_service = LLMService()
        self.verse_parser = VerseParser()
        
        # Initialize cache if enabled
        if BibleConfig.ENABLE_CACHE:
            self.cache_manager = CacheManager(
                cache_dir=".cache",
                ttl_hours=BibleConfig.CACHE_TTL_HOURS
            )
        else:
            self.cache_manager = None
        
        logger.info(f"✅ {name} initialized successfully")
        self._print_startup_info()
    
    def _print_startup_info(self):
        """Print startup information."""
        print("\n" + "=" * 60)
        print(f"📖 {self.name} Started")
        print("=" * 60)
        print(f"📚 Bible API: {BibleConfig.BASE_URL}")
        print(f"📖 Translation: {BibleConfig.DEFAULT_TRANSLATION}")
        print(f"🤖 LLM Model: {LLMConfig.MODEL}")
        print(f"💾 Cache: {'Enabled' if BibleConfig.ENABLE_CACHE else 'Disabled'}")
        if BibleConfig.ENABLE_CACHE:
            print(f"   - TTL: {BibleConfig.CACHE_TTL_HOURS} hours")
        print(f"🎯 Status: Ready to explain Bible verses")
        print("=" * 60 + "\n")
    
    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ):
        """Process user query and provide Bible verse explanation."""
        
        try:
            user_prompt = query.prompt.strip()
            logger.info(f"📨 Query: {user_prompt[:100]}...")
            
            # Check if greeting
            if self._is_greeting(user_prompt):
                await self._handle_greeting(response_handler)
                return
            
            # Try to extract verse reference
            verse_reference = self.verse_parser.extract_verse_reference(user_prompt)
            
            if not verse_reference:
                await response_handler.emit_text_block(
                    "INFO",
                    "❌ I couldn't find a Bible verse reference in your message. "
                    "Please include a verse like 'Matthew 7:7' or 'John 3:16'."
                )
                await response_handler.complete()
                return
            
            logger.info(f"📖 Found verse: {verse_reference}")
            
            # Check cache first
            cache_key = f"{verse_reference}:{user_prompt}"
            if self.cache_manager:
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(f"💾 Cache hit for: {verse_reference}")
                    await response_handler.emit_text_block(
                        "STATUS",
                        "✨ Found cached explanation"
                    )
                    await self._stream_cached_response(
                        cached_result, 
                        response_handler
                    )
                    return
            
            # Fetch verse from Bible API
            await response_handler.emit_text_block(
                "STATUS",
                f"📖 Looking up {verse_reference}..."
            )
            
            verse_data = await self.bible_service.get_verse(verse_reference)
            
            if not verse_data or "error" in verse_data:
                error_msg = verse_data.get("message", "Failed to fetch verse") if verse_data else "Failed to fetch verse"
                await response_handler.emit_error(
                    error_message=error_msg,
                    error_code=404
                )
                await response_handler.complete()
                return
            
            # Emit verse data as JSON
            await response_handler.emit_json("VERSE_DATA", verse_data)
            
            # Display the verse text
            verse_text_formatted = self.bible_service.format_verse_text(verse_data)
            await response_handler.emit_text_block(
                "VERSE_TEXT",
                verse_text_formatted
            )
            
            # Generate explanation using LLM
            await response_handler.emit_text_block(
                "STATUS",
                "🤖 Generating explanation..."
            )
            
            # Stream the explanation
            explanation_stream = response_handler.create_text_stream(
                "EXPLANATION"
            )
            
            # Add header
            await explanation_stream.emit_chunk("\n## 📚 Explanation\n\n")
            
            # Collect explanation for caching
            full_explanation = ""
            
            async for chunk in self.llm_service.explain_verse(
                verse_reference=verse_data.get("reference", verse_reference),
                verse_text=verse_data.get("text", ""),
                user_question=user_prompt
            ):
                await explanation_stream.emit_chunk(chunk)
                full_explanation += chunk
            
            await explanation_stream.complete()
            
            # Cache the result
            if self.cache_manager:
                cache_data = {
                    "verse_reference": verse_reference,
                    "verse_data": verse_data,
                    "verse_text": verse_text_formatted,
                    "explanation": full_explanation
                }
                await self.cache_manager.set(cache_key, cache_data)
                logger.info(f"💾 Cached result for: {verse_reference}")
            
            # Complete the response
            await response_handler.complete()
            logger.info("✅ Query processed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {str(e)}", exc_info=True)
            await response_handler.emit_error(
                error_message=f"An error occurred: {str(e)}",
                error_code=500
            )
            await response_handler.complete()
    
    def _is_greeting(self, prompt: str) -> bool:
        """Check if the prompt is a greeting."""
        prompt_lower = prompt.lower()
        return any(
            pattern in prompt_lower 
            for pattern in self.GREETING_PATTERNS
        )
    
    async def _handle_greeting(self, response_handler: ResponseHandler):
        """Handle greeting queries."""
        greeting_response = f"""
Hello! I'm **{self.name}** 📖

**What I can do:**
- Fetch Bible verses from the {BibleConfig.DEFAULT_TRANSLATION} translation
- Provide detailed explanations of verses
- Answer questions about specific passages
- Explain historical and theological context

**How to use me:**
Simply ask me about any Bible verse! Here are some examples:

**Examples:**
- "According to Matthew 7:7, what did Jesus tell his disciples?"
- "Explain John 3:16"
- "What does Romans 8:28 mean?"
- "Tell me about Psalm 23:1"

**Supported formats:**
- Full names: "Matthew 7:7"
- Abbreviations: "Matt 7:7", "Mt 7:7"
- Verse ranges: "John 3:16-17"

What verse would you like to explore today?
        """.strip()
        
        await response_handler.emit_text_block(
            "GREETING",
            greeting_response
        )
        await response_handler.complete()
    
    async def _stream_cached_response(
        self, 
        cached_data: dict, 
        response_handler: ResponseHandler
    ):
        """Stream a cached response."""
        
        # Emit verse data
        if "verse_data" in cached_data:
            await response_handler.emit_json(
                "VERSE_DATA", 
                cached_data["verse_data"]
            )
        
        # Emit verse text
        if "verse_text" in cached_data:
            await response_handler.emit_text_block(
                "VERSE_TEXT",
                cached_data["verse_text"]
            )
        
        # Stream explanation
        if "explanation" in cached_data:
            explanation_stream = response_handler.create_text_stream(
                "EXPLANATION"
            )
            
            await explanation_stream.emit_chunk("\n## 📚 Explanation\n\n")
            
            # Stream cached explanation in chunks
            explanation = cached_data["explanation"]
            chunk_size = 50  # characters per chunk
            
            for i in range(0, len(explanation), chunk_size):
                chunk = explanation[i:i + chunk_size]
                await explanation_stream.emit_chunk(chunk)
            
            await explanation_stream.complete()
        

        await response_handler.complete()
