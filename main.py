# main.py
"""
Ham Radio Contact Mapper
Main program file that runs the application
"""

import sys
import os
from adif_parser import parse_adif_file
from grid_converter import grid_to_coordinates
from maps_interface import create_map
from settings import Settings

def main():
    """Main entry point for the application"""
    
    settings = Settings()
    
    # Check if adif file is provided as argument
    if len(sys.argv) > 1:
        adif_file = sys.argv[1]
    else:
        adif_file = settings.DEFAULT_ADIF_FILE
    
    if not os.path.exists(adif_file):
        print(f"Error: ADIF file not found: {adif_file}")
        return
    
    print(f"Processing ADIF file: {adif_file}")
    
    # Parse the ADIF file
    contacts = parse_adif_file(adif_file)
    
    if not contacts:
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
    
    # If we found the operator's grid, add it to all contacts for consistency
    if operator_grid:
        for contact in contacts:
            if 'MY_GRIDSQUARE' not in contact or not contact['MY_GRIDSQUARE'].strip():
                contact['MY_GRIDSQUARE'] = operator_grid
    
    # Convert grid squares to coordinates
    for contact in contacts:
        # Convert contact's grid square
        if 'GRIDSQUARE' in contact and contact['GRIDSQUARE'].strip():
            grid = contact['GRIDSQUARE']
            lat, lon = grid_to_coordinates(grid)
            if lat is not None and lon is not None:
                contact['LATITUDE'] = lat
                contact['LONGITUDE'] = lon
        
        # Convert operator's grid square
        if 'MY_GRIDSQUARE' in contact and contact['MY_GRIDSQUARE'].strip():
            my_grid = contact['MY_GRIDSQUARE']
            my_lat, my_lon = grid_to_coordinates(my_grid)
            if my_lat is not None and my_lon is not None:
                contact['MY_LATITUDE'] = my_lat
                contact['MY_LONGITUDE'] = my_lon
    
    # Filter only contacts with coordinates
    mapped_contacts = [c for c in contacts if 'LATITUDE' in c and 'LONGITUDE' in c]
    
    if not mapped_contacts:
        print("No contacts with valid grid squares found.")
        return
    
    print(f"Mapping {len(mapped_contacts)} contacts with valid coordinates")
    
    # Create and display the map
    html_file = create_map(mapped_contacts, settings)
    
    print(f"Map created: {html_file}")
    print(f"Open {html_file} in your web browser to view your contacts")

if __name__ == "__main__":
    main()