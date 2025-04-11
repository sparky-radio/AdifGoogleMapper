# adif_parser.py
"""
Module for parsing Amateur Data Interchange Format (ADIF) files
"""

import re
from datetime import datetime

def parse_adif_file(filename):
    """
    Parse an ADIF file and return a list of contacts
    
    Args:
        filename (str): Path to the ADIF file
    
    Returns:
        list: List of dictionaries containing contact information
    """
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
        
        # Remove header if present
        if '<EOH>' in content:
            content = content.split('<EOH>')[1]
        
        # Find all field entries
        pattern = r'<([^:]+)(?::(\d+))?>(.*?)(?=<\w+(?::\d+)?>|$)'
        contacts = []
        current_contact = {}
        
        for match in re.finditer(pattern, content):
            field_name = match.group(1).upper()
            field_length = match.group(2)  # This is optional
            field_value = match.group(3)
            
            # Strip whitespace from field value
            field_value = field_value.strip()
            
            # If we hit an EOR (End Of Record), save the contact and start a new one
            if field_name == 'EOR':
                if current_contact:  # Only append if we have data
                    contacts.append(current_contact)
                current_contact = {}
            else:
                current_contact[field_name] = field_value
        
        # Add the last contact if it exists and wasn't terminated with EOR
        if current_contact:
            contacts.append(current_contact)
        
        return contacts
    
    except Exception as e:
        print(f"Error parsing ADIF file: {e}")
        return []