import csv
import re
from datetime import datetime
from grid_converter import grid_to_coordinates
from settings import Settings
from utils import wspr_frequency_to_band

def parse_wspr_file(file_path, settings : Settings):
    # Define the data structure to hold parsed records
    wspr_data = []
    maidenhead_pattern = r'^[A-R]{2}[0-9]{2}([a-x]{2})?$'
    
    # Define column names for reference
    columns = [
        'date', 'time', 'snr', 'frequency', 'drift', 
        'tx_call', 'tx_grid', 'tx_power', 
        'rx_call', 'rx_grid', 'distance', 'azimuth'
    ]
    
    # Read and parse the file
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line by whitespace
            parts = line.strip().split()
            
            # Only process valid lines (must have correct number of fields)
            if len(parts) >= len(columns):
                tx_lat = ''
                tx_long = ''
                rx_lat = ''
                rx_long = ''
                if parts[6] :
                    tx_grid = parts[6].strip()
                    if bool(re.match(maidenhead_pattern, tx_grid, re.IGNORECASE)):
                        tx_lat, tx_long = grid_to_coordinates(tx_grid)
                    else :
                        tx_grid = ''
                if parts[9] :
                    rx_grid = parts[9].strip()
                    rx_lat, rx_long = grid_to_coordinates(rx_grid)
                record = {
                    'date': parts[0],
                    'time': parts[1],
                    'snr': float(parts[2]),
                    'drift': float(parts[3]),
                    'frequency': float(parts[4]),
                    'tx_call': parts[5],
                    'tx_grid': tx_grid,
                    'tx_lat' : tx_lat,
                    'tx_long' : tx_long,
                    'tx_power': parts[7],
                    'rx_call': parts[8],
                    'rx_grid': rx_grid,
                    'distance': int(parts[10]) if parts[10].isdigit() else 0,
                    'azimuth': int(parts[11]) if len(parts) > 11 and parts[11].isdigit() else 0
                }
                
                # Create a datetime object
                try:
                    date_str = '20' + record['date']
                    # time_str = record['time']
                    # date_obj = datetime.strptime(f"{date_str} {time_str}", "%y%m%d %H%M")
                    date_obj = datetime.strptime(f"{date_str}", "%y%m%d")
                    if settings.start_date and date_obj.date < settings.start_date:
                        break
                    if settings.end_date and date_obj.date > settings.end_date:
                        break
                    record['datetime'] = date_obj
                except ValueError:
                    record['datetime'] = None
                
                record = add_partial_adif_values(record)
                wspr_data.append(record)
    
    return wspr_data


def add_partial_adif_values(data) :
    data['GRIDSQUARE'] = data['tx_grid']
    data['CALL'] = data['tx_call']
    data['QSO_DATE'] = data['date']
    data['TIME_ON'] = data['time']
    data['LATITUDE'] = data['tx_lat']
    data['LONGITUDE'] = data['tx_long']
    data['BAND'] = wspr_frequency_to_band(data['frequency'])

    return data

def display_wspr_data(data, num_records=5):
    """Display a few records nicely formatted"""
    if not data:
        print("No data to display")
        return
    
    # Get field width for each column
    sample = data[0]
    fields = list(sample.keys())
    
    # Print header
    header = " | ".join(fields)
    print(header)
    print("-" * len(header))
    
    # Print data
    for i, record in enumerate(data[:num_records]):
        values = [str(record[field]) for field in fields]
        print(" | ".join(values))
    
    print(f"\nShowing {num_records} of {len(data)} records")

# Usage example
if __name__ == "__main__":
    file_path = "ALL_WSPR.TXT"  # Update with your file path
    
    try:
        settings = Settings()
        wspr_data = parse_wspr_file(file_path, settings)
        print(f"Loaded {len(wspr_data)} WSPR records")
        display_wspr_data(wspr_data, 5000)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing file: {e}")