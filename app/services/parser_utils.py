import re
from typing import List, Dict, Any, Optional, Tuple
from app.utils.logger import app_logger
from app.services.llm_utils import get_llm

def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract basic contact information from resume text
    """
    contact_info = {
        "name": None,
        "email": None,
        "phone": None,
        "location": None
    }
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info["email"] = email_match.group()
    
    # Phone extraction
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?(?:\d{3})?\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info["phone"] = phone_match.group()
    
    # Name and location often require LLM extraction, which is done in more complex nodes
    
    return contact_info

def extract_sections(text: str) -> Dict[str, str]:
    """
    Attempt to extract common resume sections
    """
    sections = {}
    
    # Common section headers (case-insensitive)
    section_patterns = {
        "summary": r'(?i)(Summary|Professional Summary|Profile|Objective)[\s]*:',
        "experience": r'(?i)(Experience|Work Experience|Employment History|Professional Experience)[\s]*:',
        "education": r'(?i)(Education|Educational Background|Academic History)[\s]*:',
        "skills": r'(?i)(Skills|Technical Skills|Core Competencies|Key Skills)[\s]*:',
        "certifications": r'(?i)(Certifications|Professional Certifications|Certificates)[\s]*:',
        "projects": r'(?i)(Projects|Personal Projects|Professional Projects)[\s]*:'
    }
    
    # Find the positions of all section headers
    section_positions = {}
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, text)
        if match:
            section_positions[section_name] = match.start()
    
    # Sort the sections by position
    sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
    
    # Extract text for each section
    for i, (section_name, pos) in enumerate(sorted_sections):
        start_pos = pos
        
        # End position is the start of the next section or end of text
        if i < len(sorted_sections) - 1:
            end_pos = sorted_sections[i + 1][1]
        else:
            end_pos = len(text)
        
        sections[section_name] = text[start_pos:end_pos].strip()
    
    return sections

def clean_resume_text(text: str) -> str:
    """
    Clean and normalize resume text
    """
    # Replace multiple newlines with a single newline
    cleaned = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with a single space
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    
    # Replace Unicode characters with ASCII equivalents
    cleaned = cleaned.replace('•', '* ')
    cleaned = cleaned.replace('–', '-')
    cleaned = cleaned.replace('—', '-')
    cleaned = cleaned.replace('"', '"')
    cleaned = cleaned.replace('"', '"')
    cleaned = cleaned.replace(''', "'")
    cleaned = cleaned.replace(''', "'")
    
    return cleaned.strip()

async def extract_dates(text: str) -> List[Tuple[str, str]]:
    """
    Extract date ranges from text using regex
    Returns a list of (start_date, end_date) tuples
    """
    # Common date formats in resumes
    date_pattern = r'(?i)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-z.]*\s+\d{4}\s*(?:-|–|to)\s*(Present|Current|Now|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-z.]*\s*\d{0,4}'
    
    date_ranges = []
    matches = re.finditer(date_pattern, text)
    
    for match in matches:
        date_range = match.group(0)
        parts = re.split(r'(?:-|–|to)', date_range)
        if len(parts) == 2:
            start_date = parts[0].strip()
            end_date = parts[1].strip()
            date_ranges.append((start_date, end_date))
    
    return date_ranges
