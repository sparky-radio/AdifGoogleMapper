# maps_interface.py
"""
Module for interfacing with Google Maps API to display contacts and paths
"""

import os
import webbrowser
from datetime import datetime
from collections import defaultdict
from utils import BAND_COLORS
from grid_converter import grid_to_coordinates

def create_map(contacts, settings):
    """
    Create an HTML file with Google Maps displaying the contacts and paths
    
    Args:
        contacts (list): List of contacts with lat/long coordinates
        settings (Settings): Settings object containing API keys and preferences
    
    Returns:
        str: Path to the generated HTML file
    """
    # Create file path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = settings.OUTPUT_DIRECTORY
    os.makedirs(output_dir, exist_ok=True)
    html_file = os.path.join(output_dir, f"ham_contacts_map_{timestamp}.html")
    
    # Find operator's grid square from contacts
    operator_grid = settings.OPERATOR_GRIDSQUARE
    operator_lat = None
    operator_lon = None
    
    # Look for MY_GRIDSQUARE in contacts if not in settings
    if not operator_grid:
        for contact in contacts:
            if 'MY_GRIDSQUARE' in contact and contact['MY_GRIDSQUARE'].strip():
                operator_grid = contact['MY_GRIDSQUARE'].strip()
                operator_lat, operator_lon = grid_to_coordinates(operator_grid)
                break
    else:
        # Convert operator grid from settings
        operator_lat, operator_lon = grid_to_coordinates(operator_grid)
    
    # Format date range for display if available
    date_range_html = ""
    if hasattr(settings, 'start_date') and settings.start_date is not None:
        start_date_str = settings.start_date.strftime("%Y-%m-%d")
        if hasattr(settings, 'end_date') and settings.end_date is not None:
            end_date_str = settings.end_date.strftime("%Y-%m-%d")
            date_range_html = f'<div id="date-range">Date Range: {start_date_str} to {end_date_str}</div>'
        else:
            date_range_html = f'<div id="date-range">From Date: {start_date_str}</div>'
    elif hasattr(settings, 'end_date') and settings.end_date is not None:
        end_date_str = settings.end_date.strftime("%Y-%m-%d")
        date_range_html = f'<div id="date-range">To Date: {end_date_str}</div>'
    
    # Start building the HTML content
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Ham Radio Contacts Map</title>
    <meta charset="utf-8">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <style>
        #map {{
            height: 100%;
            width: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }}
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
        }}
        .info-window {{
            max-width: 300px;
            max-height: 400px;
            overflow-y: auto;
        }}
        .contact-entry {{
            border-bottom: 1px solid #eee;
            padding: 5px 0;
        }}
        .contact-entry:last-child {{
            border-bottom: none;
        }}
        .legend {{
            background: white;
            padding: 10px;
            margin: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            position: absolute;
            bottom: 30px;
            right: 10px;
            z-index: 1000;
        }}
        .operator-marker {{
            color: blue;
            font-size: 20px;
            display: inline-block;
            margin-right: 5px;
        }}
        .contact-marker {{
            color: red;
            font-size: 20px;
            display: inline-block;
            margin-right: 5px;
        }}
        .path-line {{
            background-color: green;
            height: 3px;
            width: 20px;
            display: inline-block;
            margin-right: 5px;
            vertical-align: middle;
        }}
        #date-range {{
            margin-top: 8px;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="legend">
        <div><span class="operator-marker">●</span> Your location</div>
        <div><span class="contact-marker">●</span> Contact locations</div>
        <div><span class="path-line"></span> Path</div>
        <div id="contact-count">Contacts: {len(contacts)} total</div>
        <div id="marker-count">Locations: 0</div>
        {date_range_html}
    </div>
    <script>
        function initMap() {{
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 2,
                center: {{ lat: 0, lng: 0 }},
                mapTypeId: google.maps.MapTypeId.{settings.DEFAULT_MAP_TYPE}
            }});
            
            const infoWindow = new google.maps.InfoWindow();
            const bounds = new google.maps.LatLngBounds();
            let markersArray = [];
            let pathsArray = [];
            let totalContacts = {len(contacts)};
"""
    
    # Add operator marker if grid square is available
    if operator_lat and operator_lon:
        html_content += f"""
            // Add operator's location marker
            const operatorPosition = {{ lat: {operator_lat}, lng: {operator_lon} }};
            const operatorMarker = new google.maps.Marker({{
                position: operatorPosition,
                map: map,
                title: "Your Location ({operator_grid})",
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 7,
                    fillColor: "#2196F3",
                    fillOpacity: 0.8,
                    strokeWeight: 2,
                    strokeColor: "#0b47a1"
                }}
            }});
            
            bounds.extend(operatorPosition);
            
            operatorMarker.addListener("click", () => {{
                infoWindow.setContent(
                    `<div class="info-window">
                        <h3>Your Location</h3>
                        <p>Grid Square: {operator_grid}</p>
                        <p>Coordinates: {operator_lat}, {operator_lon}</p>
                    </div>`
                );
                infoWindow.open(map, operatorMarker);
            }});
"""
    
    # Group contacts by their coordinates
    grouped_contacts = defaultdict(list)
    for contact in contacts:
        if 'LATITUDE' in contact and 'LONGITUDE' in contact:
            key = f"{contact['LATITUDE']},{contact['LONGITUDE']}"
            grouped_contacts[key].append(contact)
    
    # Add contact markers for each unique location
    html_content += """
            // Create markers for each unique location
"""

    for i, (coord_key, location_contacts) in enumerate(grouped_contacts.items()):
        lat, lng = coord_key.split(',')
        
        # Get the first contact's call for the marker title
        first_call = location_contacts[0].get('CALL', 'Unknown').replace('"', '\\"')
        contact_count = len(location_contacts)
        
        # Build content for info window with all contacts at this location
        info_window_content = []
        
        for j, contact in enumerate(location_contacts):
            # Build a description with available information
            info_parts = []
            
            if 'CALL' in contact:
                call = contact['CALL'].replace('"', '\\"')
                info_parts.append(f"<strong>Callsign:</strong> {call}")
            if 'NAME' in contact:
                name = contact['NAME'].replace('"', '\\"')
                info_parts.append(f"<strong>Name:</strong> {name}")
            if 'QSO_DATE' in contact:
                date = contact['QSO_DATE']
                if len(date) == 8:  # YYYYMMDD format
                    formatted_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
                    info_parts.append(f"<strong>Date:</strong> {formatted_date}")
            if 'TIME_ON' in contact:
                time = contact['TIME_ON']
                if len(time) >= 4:  # HHMM format
                    formatted_time = f"{time[0:2]}:{time[2:4]}"
                    info_parts.append(f"<strong>Time:</strong> {formatted_time}")
            if 'BAND' in contact:
                info_parts.append(f"<strong>Band:</strong> {contact['BAND']}")
            if 'MODE' in contact:
                info_parts.append(f"<strong>Mode:</strong> {contact['MODE']}")
            if 'GRIDSQUARE' in contact:
                info_parts.append(f"<strong>Grid:</strong> {contact['GRIDSQUARE']}")
            
            contact_html = f"""<div class="contact-entry">
                <h4>Contact {j+1}: {call if 'CALL' in contact else 'Unknown'}</h4>
                <p>{" | ".join(info_parts)}</p>
            </div>"""
            
            info_window_content.append(contact_html)
        
        marker_title = f"{first_call} ({contact_count} contact{'s' if contact_count > 1 else ''})"
        combined_info = "".join(info_window_content).replace('\\', '\\\\').replace('`', '\\`')
        band_color = BAND_COLORS[contact['BAND']]
        # Add marker for this location with info about all contacts
        html_content += f"""
            // Location {i+1} with {contact_count} contact(s)
            const location{i} = new google.maps.Marker({{
                position: {{ lat: {lat}, lng: {lng} }},
                map: map,
                title: "{marker_title}",
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 5,
                    fillColor: "{band_color}",
                    fillOpacity: 0.8,
                    strokeWeight: 2,
                    strokeColor: "{band_color}"
                }},
                contactCount: {contact_count}
            }});
            
            bounds.extend({{ lat: {lat}, lng: {lng} }});
            markersArray.push(location{i});
            
            location{i}.addListener("click", () => {{
                infoWindow.setContent(
                    `<div class="info-window">
                        <h3>Location with {contact_count} contact{'s' if contact_count > 1 else ''}</h3>
                        {combined_info}
                    </div>`
                );
                infoWindow.open(map, location{i});
            }});
"""
        
        # Add path from operator to this location if operator location is available
        if operator_lat and operator_lon:
            html_content += f"""
            // Draw path to location {i+1}
            const path{i} = new google.maps.Polyline({{
                path: [
                    {{ lat: {operator_lat}, lng: {operator_lon} }},
                    {{ lat: {lat}, lng: {lng} }}
                ],
                geodesic: true,
                strokeColor: "{band_color}",
                strokeOpacity: 0.6,
                strokeWeight: 2
            }});
            path{i}.setMap(map);
            pathsArray.push(path{i});
"""
    
    # Add final JavaScript to fit bounds and control marker visibility
    html_content += """
            // Adjust the map to fit all markers
            if (markersArray.length > 0) {
                map.fitBounds(bounds);
                // Update marker count initially
                document.getElementById("marker-count").textContent = `Locations: ${markersArray.length} total`;
            }
            
            // Add a listener to update marker visibility when the map changes
            map.addListener("bounds_changed", () => {
                const mapBounds = map.getBounds();
                let visibleMarkers = 0;
                let visibleContacts = 0;
                
                if (mapBounds) {
                    markersArray.forEach(marker => {
                        if (mapBounds.contains(marker.getPosition())) {
                            visibleMarkers++;
                            visibleContacts += marker.contactCount;
                        }
                    });
                    
                    // Update the counts in the legend
                    document.getElementById("contact-count").textContent = 
                        `Contacts: ${visibleContacts} visible of ${totalContacts} total`;
                    document.getElementById("marker-count").textContent = 
                        `Locations: ${visibleMarkers} visible of ${markersArray.length} total`;
                }
            });
        }
    </script>
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=API_KEY&callback=initMap">
    </script>
</body>
</html>
""".replace("API_KEY", settings.GOOGLE_MAPS_API_KEY)
    
    # Write the HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open the file in the default browser if auto-open is enabled
    if settings.AUTO_OPEN_MAP:
        webbrowser.open('file://' + os.path.abspath(html_file))
    
    return html_file