"""
Utility functions for parsing resume text
"""
import re
from typing import Dict, Any, List, Optional

def clean_resume_text(text: str) -> str:
    """
    Clean and normalize resume text
    
    Args:
        text: Raw resume text
        
    Returns:
        str: Cleaned resume text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Replace multiple newlines with double newlines for better section separation
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extract basic contact information from resume text
    
    Args:
        text: Cleaned resume text
        
    Returns:
        Dict[str, Any]: Dictionary with contact information
    """
    # Initialize results
    contact_info = {
        "name": None,
        "email": None,
        "phone": None,
        "location": None,
    }
    
    # Extract email with regex
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        contact_info["email"] = email_match.group(0)
    
    # Extract phone with regex
    phone_match = re.search(r'\b(?:\+\d{1,2}\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b', text)
    if phone_match:
        contact_info["phone"] = phone_match.group(0)
    
    # Extract name (naive approach - first line often contains the name)
    lines = text.strip().split('\n')
    if lines:
        potential_name = lines[0].strip()
        # Check if the first line is a name (no special chars, not too long)
        if len(potential_name) > 0 and len(potential_name) < 50 and not re.search(r'[@:/]', potential_name):
            contact_info["name"] = potential_name
    
    return contact_info

def extract_sections(text: str) -> Dict[str, str]:
    """
    Extract major sections from the resume text
    
    Args:
        text: Cleaned resume text
        
    Returns:
        Dict[str, str]: Dictionary mapping section names to their content
    """
    # Common section headers
    section_patterns = [
        r'\b(WORK\s+EXPERIENCE|EXPERIENCE|EMPLOYMENT|PROFESSIONAL\s+EXPERIENCE)\b',
        r'\b(EDUCATION|ACADEMIC\s+BACKGROUND|QUALIFICATIONS)\b',
        r'\b(SKILLS|TECHNICAL\s+SKILLS|COMPETENCIES)\b',
        r'\b(PROJECTS)\b',
        r'\b(CERTIFICATIONS|CERTIFICATES)\b',
        r'\b(LANGUAGES)\b',
        r'\b(PUBLICATIONS)\b',
        r'\b(INTERESTS|HOBBIES)\b'
    ]
    
    sections = {}
    current_section = "HEADER"
    section_content = []
    
    # Process line by line
    lines = text.split('\n')
    for line in lines:
        # Check if line is a section header
        is_section_header = False
        for pattern in section_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Save the current section if there is one
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                
                # Start a new section
                current_section = line.strip()
                section_content = []
                is_section_header = True
                break
        
        # If not a header, add to current section
        if not is_section_header:
            section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content).strip()
    
    return sections
