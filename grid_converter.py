# grid_converter.py
"""
Module for converting Maidenhead grid squares to latitude and longitude coordinates
"""

def grid_to_coordinates(grid_square):
    """
    Convert a Maidenhead grid square to latitude and longitude
    
    Args:
        grid_square (str): Maidenhead grid square (e.g., FM18lw)
    
    Returns:
        tuple: (latitude, longitude) in decimal degrees
    """
    try:
        # Ensure the grid square is uppercase
        grid = grid_square.upper().strip()
        
        # Basic validation
        if not grid or len(grid) < 2:
            return None, None
        
        # Convert the first pair (field) A-R -> 0-17
        lon = (ord(grid[0]) - ord('A')) * 20
        lat = (ord(grid[1]) - ord('A')) * 10
        
        # Convert the second pair (square) 0-9 -> 0-9
        if len(grid) >= 4:
            lon += int(grid[2]) * 2
            lat += int(grid[3])
        
        # Convert the third pair (subsquare) a-x -> 0-23
        if len(grid) >= 6:
            lon += (ord(grid[4]) - ord('A')) / 12
            lat += (ord(grid[5]) - ord('A')) / 24
        
        # Convert to the final coordinates
        longitude = lon - 180  # Convert to range -180 to 180
        latitude = lat - 90    # Convert to range -90 to 90
        
        # For subsquare, we need to add half of the subsquare size
        # to get the center point
        if len(grid) >= 6:
            longitude += 1/24  # Half of subsquare width
            latitude += 1/48   # Half of subsquare height
        # For square, we need to add half of the square size
        elif len(grid) >= 4:
            longitude += 1     # Half of square width
            latitude += 0.5    # Half of square height
        # For field, we need to add half of the field size
        else:
            longitude += 10    # Half of field width
            latitude += 5      # Half of field height
        
        return round(latitude, 6), round(longitude, 6)
        
    except Exception as e:
        print(f"Error converting grid square {grid_square}: {e}")
        return None, None