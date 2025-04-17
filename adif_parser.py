# adif_parser.py
"""
Module for parsing Amateur Data Interchange Format (ADIF) files
"""

import re
from datetime import datetime
from settings import Settings

def parse_adif_file(filename, settings):
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
        
        rows = content.splitlines()
        contacts = []
        pattern = r"<call:"
        qso_date_format_string = "%Y%m%d"
        for row in rows:
            add_row = True
            if re.search(pattern, row, re.IGNORECASE) :

                # Find all field entries
                field_pattern = r'<([^:]+)(?::(\d+))?>(.*?)(?=<\w+(?::\d+)?>|$)'
                qso_date = None
                current_contact = {}

                for match in re.finditer(field_pattern, row):
                    field_name = match.group(1).upper()
                    field_length = match.group(2)  # This is optional
                    field_value = match.group(3)

                    # Strip whitespace from field value
                    field_value = field_value.strip()
                    if field_name == 'QSO_DATE':
                        qso_date = datetime.strptime(field_value, qso_date_format_string)
                        if settings.start_date and qso_date.date() < settings.start_date :
                            add_row = False
                            break

                        if settings.end_date and qso_date.date() > settings.end_date:
                            add_row = False
                            break

                    # If we hit an EOR (End Of Record), save the contact and start a new one
                    if field_name == 'EOR':
                        if current_contact:  # Only append if we have data
                            contacts.append(current_contact.copy())  # Make a copy to avoid reference issues
                        current_contact = {}
                    else:
                        current_contact[field_name] = field_value

                # Add the last contact if it exists and wasn't terminated with EOR
                if current_contact and add_row:
                    contacts.append(current_contact.copy())
        
        print(f"Successfully parsed {len(contacts)} contacts from ADIF file")
        return contacts
    
    except Exception as e:
        print(f"Error parsing ADIF file: {e}")
        return []