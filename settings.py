# settings.py
"""
Settings module for Ham Radio Contact Mapper
"""

import os
import json

class Settings:
    """Class to manage application settings"""
    
    def __init__(self):
        """Initialize with default settings and load from file if available"""
        
        # Default values
        self.DEFAULT_ADIF_FILE = "contacts.adi"
        self.OUTPUT_DIRECTORY = "maps"
        self.GOOGLE_MAPS_API_KEY = ""  # This should be provided by the user
        self.DEFAULT_MAP_TYPE = "HYBRID"  # ROADMAP, SATELLITE, HYBRID, or TERRAIN
        self.AUTO_OPEN_MAP = True
        self.OPERATOR_GRIDSQUARE = ""  # Optional: can be set if not found in ADIF
        self.IS_WSPR = False
        
        # Load settings from file if it exists
        self.load_settings()
        self.start_date = None
        self.end_date = None
        self.band = None
    
    def load_settings(self):
        """Load settings from settings.json file if it exists"""
        settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings_data = json.load(f)
                
                # Update settings from file
                for key, value in settings_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                print("Settings loaded successfully")
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to settings.json file"""
        settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        
        try:
            # Create a dictionary of settings
            settings_data = {
                "DEFAULT_ADIF_FILE": self.DEFAULT_ADIF_FILE,
                "OUTPUT_DIRECTORY": self.OUTPUT_DIRECTORY,
                "GOOGLE_MAPS_API_KEY": self.GOOGLE_MAPS_API_KEY,
                "DEFAULT_MAP_TYPE": self.DEFAULT_MAP_TYPE,
                "AUTO_OPEN_MAP": self.AUTO_OPEN_MAP,
                "OPERATOR_GRIDSQUARE": self.OPERATOR_GRIDSQUARE
            }
            
            # Write to file
            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=4)
            
            print("Settings saved successfully")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False