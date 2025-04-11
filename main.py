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
    
    # Convert grid squares to coordinates
    for contact in contacts:
        if 'GRIDSQUARE' in contact:
            grid = contact['GRIDSQUARE']
            lat, lon = grid_to_coordinates(grid)
            contact['LATITUDE'] = lat
            contact['LONGITUDE'] = lon
    
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