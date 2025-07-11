# main.py
"""
Ham Radio Contact Mapper
Main program file that runs the application
"""
import argparse
import datetime

import sys
import os
from adif_parser import parse_adif_file
from wspr_parser import parse_wspr_file
from grid_converter import grid_to_coordinates
from maps_interface import create_map
from settings import Settings

def main():
    """Main entry point for the application"""

    parser = argparse.ArgumentParser()
    args = parse_args(parser)
    
    settings = Settings()
    
    if args.start:
        settings.start_date = args.start

    if args.end:
        settings.end_date = args.end

    is_wspr = False
    
    # Check if adif file is provided as argument
    if args.adi:
        contacts = do_adi_processing(args, settings)

    if args.wspr:
        is_wspr = True
        contacts = do_wspr_processing(args, settings)
    
    if not contacts:
        if is_wspr :
            print("No contacts found in the WSPR file.")
        else :
            print("No contacts found in the ADIF file.")
        return
    
    print(f"Found {len(contacts)} contacts")
    
    # Find operator's grid square if not already in contacts
    operator_grid = settings.OPERATOR_GRIDSQUARE
    
    # If operator grid is not in settings, look for it in contacts
    if not operator_grid:
        for contact in contacts:
            if 'MY_GRIDSQUARE' in contact and contact['MY_GRIDSQUARE'].strip():
                operator_grid = contact['MY_GRIDSQUARE'].strip()
                break
    
    if operator_grid:
        print(f"Using operator grid square: {operator_grid}")
    else:
        print("Warning: Operator grid square not found. Paths between contacts will not be displayed.")
    
    # Convert grid squares to coordinates for all contacts
    valid_contacts = []
    
    for contact in contacts:
        if args.wspr and contact['GRIDSQUARE'] and contact['LATITUDE'] and contact['LONGITUDE'] :
            valid_contacts.append(contact)
            continue

        # Copy the contact to avoid modifying the original
        processed_contact = contact.copy()
        
        # Convert contact's grid square
        if 'GRIDSQUARE' in processed_contact and processed_contact['GRIDSQUARE'].strip():
            grid = processed_contact['GRIDSQUARE'].strip()
            lat, lon = grid_to_coordinates(grid)
            if lat is not None and lon is not None:
                processed_contact['LATITUDE'] = lat
                processed_contact['LONGITUDE'] = lon
                valid_contacts.append(processed_contact)
            else:
                print(f"Warning: Invalid grid square '{grid}' for contact {processed_contact.get('CALL', 'Unknown')}")
        else:
            print(f"Warning: No grid square found for contact {processed_contact.get('CALL', 'Unknown')}")
    
    if not valid_contacts:
        print("Error: No contacts with valid grid squares found.")
        return
    
    # Make sure operator grid is also included
    if operator_grid:
        for contact in valid_contacts:
            contact['MY_GRIDSQUARE'] = operator_grid
    
    print(f"Successfully processed {len(valid_contacts)} contacts with valid coordinates")
    
    # Create and display the map
    html_file = create_map(valid_contacts, settings)
    
    print(f"Map created: {html_file}")
    print(f"Open {html_file} in your web browser to view your contacts")

def parse_args(parser) :
    try:
        parser.add_argument("--adi", help="the ADI file name and location")
        parser.add_argument("--wspr", help="the WSPR text file name and location")
        parser.add_argument("--start", type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), help="the start date Y-M-D")
        parser.add_argument("--end", type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), help="the end date Y-M-D")
        # parser.add_argument("--band", help="the band: all, 10,12,15,20,30...")
        args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
        return args
        
    except: # calling help will call SystemExit, we can catch this instead
        parser.print_help
        sys.exit(0)

def do_adi_processing(args, settings : Settings) :
    adif_file = args.adi
    
    if not os.path.exists(adif_file):
        print(f"Error: ADIF file not found: {adif_file}")
        return None
    
    print(f"Processing ADIF file: {adif_file}")
    
    # Parse the ADIF file
    contacts = parse_adif_file(adif_file, settings)
    return contacts

def do_wspr_processing(args, settings : Settings) :
    wspr_file = args.wspr
    
    if not os.path.exists(wspr_file):
        print(f"Error: WSPR file not found: {wspr_file}")
        return None
    
    print(f"Processing ADIF file: {wspr_file}")
    
    # Parse the WSPR file
    contacts = parse_wspr_file(wspr_file, settings)
    return contacts

if __name__ == "__main__":
    main()