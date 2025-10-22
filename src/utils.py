import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

def setup_logging(level: str = 'INFO') -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('launchpad.log')
        ]
    )

def sanitize_text(text: str) -> str:
    """Sanitize text input for processing"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>\"\'&]', '', text)
    
    return text

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + ',}\b', text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
        'did', 'use', 'way', 'she', 'many', 'oil', 'sit', 'set', 'big', 'end'
    }
    
    keywords = [word for word in words if word not in stop_words]
    
    # Remove duplicates while preserving order
    unique_keywords = []
    seen = set()
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)
    
    return unique_keywords[:20]  # Return top 20 keywords

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = len(keywords1.intersection(keywords2))
    union = len(keywords1.union(keywords2))
    
    return intersection / union if union > 0 else 0.0

def generate_user_id(email: str = None) -> str:
    """Generate a unique user ID"""
    if email:
        return hashlib.md5(email.encode()).hexdigest()
    else:
        return hashlib.md5(datetime.now().isoformat().encode()).hexdigest()

def format_currency(amount: str) -> str:
    """Format currency strings consistently"""
    # Extract numbers from salary string
    numbers = re.findall(r'\d+', amount.replace(',', ''))
    
    if len(numbers) >= 2:
        low = int(numbers[0])
        high = int(numbers[1])
        
        # Assume thousands if numbers are small
        if low < 1000:
            low *= 1000
            high *= 1000
        
        return f"${low:,} - ${high:,}"
    elif len(numbers) == 1:
        num = int(numbers[0])
        if num < 1000:
            num *= 1000
        return f"${num:,}"
    
    return amount

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def parse_experience_level(text: str) -> str:
    """Parse and standardize experience level"""
    text = text.lower()
    
    if any(term in text for term in ['entry', 'junior', 'new', 'graduate', '0-2']):
        return 'Entry Level'
    elif any(term in text for term in ['mid', 'intermediate', '3-5', '2-5']):
        return 'Mid Level'
    elif any(term in text for term in ['senior', 'lead', 'principal', '5+']):
        return 'Senior Level'
    elif any(term in text for term in ['executive', 'director', 'vp', 'chief']):
        return 'Executive'
    
    return 'Mid Level'  # Default

def chunk_text(text: str, max_length: int = 1000) -> List[str]:
    """Split text into chunks for processing"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    sentences = re.split(r'[.!?]+', text)
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(current_chunk + sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def format_date(date_str: str) -> str:
    """Format date string consistently"""
    try:
        if isinstance(date_str, str):
            # Try to parse various date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%B %d, %Y')
                except ValueError:
                    continue
        return date_str
    except Exception:
        return date_str

def calculate_reading_time(text: str) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    # Average reading speed: 200 words per minute
    return max(1, round(word_count / 200))

def create_progress_tracker(total_steps: int) -> Dict[str, Any]:
    """Create a progress tracker for multi-step processes"""
    return {
        'total_steps': total_steps,
        'current_step': 0,
        'completed_steps': [],
        'start_time': datetime.now(),
        'estimated_completion': None
    }

def update_progress(tracker: Dict[str, Any], step_name: str) -> Dict[str, Any]:
    """Update progress tracker"""
    tracker['current_step'] += 1
    tracker['completed_steps'].append({
        'step': step_name,
        'completed_at': datetime.now()
    })
    
    # Estimate completion time
    if tracker['current_step'] > 0:
        elapsed = datetime.now() - tracker['start_time']
        avg_time_per_step = elapsed / tracker['current_step']
        remaining_steps = tracker['total_steps'] - tracker['current_step']
        tracker['estimated_completion'] = datetime.now() + (avg_time_per_step * remaining_steps)
    
    return tracker

class CareerPathValidator:
    """Validate career path suggestions"""
    
    @staticmethod
    def validate_job_title(title: str) -> bool:
        """Validate job title format"""
        if not title or len(title) < 2:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'[<>{}[\]]',  # HTML/markup
            r'\$\d+',      # Money symbols (shouldn't be in title)
            r'http[s]?://' # URLs
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def validate_salary_range(salary: str) -> bool:
        """Validate salary range format"""
        if not salary:
            return True  # Optional field
        
        # Should contain numbers and currency symbols
        if not re.search(r'\$?\d+', salary):
            return False
        
        return True

def get_default_error_message(operation: str) -> str:
    """Get user-friendly error message"""
    messages = {
        'skill_analysis': 'Unable to analyze skills at this time. Please try again later.',
        'career_planning': 'Career planning service is temporarily unavailable.',
        'document_generation': 'Document generation failed. Please check your input and try again.',
        'job_search': 'Job search is temporarily unavailable. Please try again later.',
        'general': 'An unexpected error occurred. Please try again.'
    }
    
    return messages.get(operation, messages['general'])
