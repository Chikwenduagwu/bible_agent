"""
Verse reference parser utility.
Place this in: utils/verse_parser.py
"""

import re
from typing import Optional, List


class VerseParser:
    """Parse Bible verse references from natural language."""
    
    # Common Bible book names and abbreviations
    BOOK_PATTERNS = {
        # Old Testament
        "genesis": ["genesis", "gen", "ge", "gn"],
        "exodus": ["exodus", "exod", "ex", "exo"],
        "leviticus": ["leviticus", "lev", "le", "lv"],
        "numbers": ["numbers", "num", "nu", "nm", "nb"],
        "deuteronomy": ["deuteronomy", "deut", "dt"],
        "joshua": ["joshua", "josh", "jos", "jsh"],
        "judges": ["judges", "judg", "jdg", "jg", "jdgs"],
        "ruth": ["ruth", "rth", "ru"],
        "1 samuel": ["1 samuel", "1 sam", "1sa", "1s"],
        "2 samuel": ["2 samuel", "2 sam", "2sa", "2s"],
        "1 kings": ["1 kings", "1 kgs", "1ki", "1k"],
        "2 kings": ["2 kings", "2 kgs", "2ki", "2k"],
        "psalms": ["psalms", "psalm", "ps", "pslm", "psa", "psm", "pss"],
        "proverbs": ["proverbs", "prov", "pro", "prv", "pr"],
        "isaiah": ["isaiah", "isa", "is"],
        "jeremiah": ["jeremiah", "jer", "je", "jr"],
        
        # New Testament
        "matthew": ["matthew", "matt", "mat", "mt"],
        "mark": ["mark", "mrk", "mar", "mk", "mr"],
        "luke": ["luke", "luk", "lk"],
        "john": ["john", "jhn", "joh", "jn"],
        "acts": ["acts", "act", "ac"],
        "romans": ["romans", "rom", "ro", "rm"],
        "1 corinthians": ["1 corinthians", "1 cor", "1co", "1c"],
        "2 corinthians": ["2 corinthians", "2 cor", "2co", "2c"],
        "galatians": ["galatians", "gal", "ga"],
        "ephesians": ["ephesians", "eph", "ephes"],
        "philippians": ["philippians", "phil", "php", "pp"],
        "colossians": ["colossians", "col", "co"],
        "1 thessalonians": ["1 thessalonians", "1 thess", "1th", "1t"],
        "2 thessalonians": ["2 thessalonians", "2 thess", "2th", "2t"],
        "1 timothy": ["1 timothy", "1 tim", "1ti", "1t"],
        "2 timothy": ["2 timothy", "2 tim", "2ti", "2t"],
        "titus": ["titus", "tit", "ti"],
        "philemon": ["philemon", "phlm", "phm", "pm"],
        "hebrews": ["hebrews", "heb", "he"],
        "james": ["james", "jas", "jm"],
        "1 peter": ["1 peter", "1 pet", "1pe", "1pt", "1p"],
        "2 peter": ["2 peter", "2 pet", "2pe", "2pt", "2p"],
        "1 john": ["1 john", "1 jn", "1j"],
        "2 john": ["2 john", "2 jn", "2j"],
        "3 john": ["3 john", "3 jn", "3j"],
        "jude": ["jude", "jud", "jd"],
        "revelation": ["revelation", "rev", "re", "rv"],
    }
    
    @classmethod
    def extract_verse_reference(cls, text: str) -> Optional[str]:
        """
        Extract a verse reference from text.
        
        Examples:
        - "Matthew 7:7" -> "Matthew 7:7"
        - "according to John 3:16" -> "John 3:16"
        - "read me romans 8:28" -> "Romans 8:28"
        
        Args:
            text: Input text that may contain a verse reference
            
        Returns:
            Standardized verse reference or None
        """
        text_lower = text.lower().strip()
        
        # Pattern: Book Chapter:Verse (e.g., "John 3:16")
        # Also matches ranges like "John 3:16-17" or "John 3:16-4:2"
        pattern = r'\b([123]?\s*[a-z]+)\s+(\d+):(\d+)(?:-(\d+))?(?::(\d+))?'
        
        match = re.search(pattern, text_lower)
        if match:
            book_part = match.group(1).strip()
            chapter = match.group(2)
            verse_start = match.group(3)
            verse_end = match.group(4)
            chapter_end = match.group(5)
            
            # Find the correct book name
            book_name = cls._find_book_name(book_part)
            if not book_name:
                return None
            
            # Build reference
            reference = f"{book_name.title()} {chapter}:{verse_start}"
            
            # Add range if present
            if verse_end:
                reference += f"-{verse_end}"
            if chapter_end:
                reference += f":{chapter_end}"
            
            return reference
        
        return None
    
    @classmethod
    def _find_book_name(cls, book_input: str) -> Optional[str]:
        """Find the standard book name from user input."""
        book_input = book_input.lower().strip()
        
        for standard_name, variations in cls.BOOK_PATTERNS.items():
            if book_input in variations or book_input == standard_name:
                return standard_name
        
        return None
    
    @classmethod
    def extract_all_references(cls, text: str) -> List[str]:
        """
        Extract all verse references from text.
        
        Args:
            text: Input text
            
        Returns:
            List of verse references
        """
        references = []
        text_lower = text.lower()
        
        # Pattern for verses
        pattern = r'\b([123]?\s*[a-z]+)\s+(\d+):(\d+)(?:-(\d+))?'
        
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            book_part = match.group(1).strip()
            chapter = match.group(2)
            verse_start = match.group(3)
            verse_end = match.group(4)
            
            book_name = cls._find_book_name(book_part)
            if book_name:
                reference = f"{book_name.title()} {chapter}:{verse_start}"
                if verse_end:
                    reference += f"-{verse_end}"
                references.append(reference)
        
        return references
    
    @classmethod
    def is_verse_reference(cls, text: str) -> bool:
        """Check if text contains a verse reference."""
        return cls.extract_verse_reference(text) is not None