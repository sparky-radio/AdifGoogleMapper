# maps_interface.py
"""
Module for interfacing with Google Maps API to display contacts
"""

import os
import webbrowser
from datetime import datetime

def create_map(contacts, settings):
    """
    Create an HTML file with Google Maps displaying the contacts
    
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
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        function initMap() {{
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 2,
                center: {{ lat: 0, lng: 0 }},
                mapTypeId: google.maps.MapTypeId.{settings.DEFAULT_MAP_TYPE}
            }});
            
            const infoWindow = new google.maps.InfoWindow();
            const bounds = new google.maps.LatLngBounds();
            
            // Create markers for each contact
            const contacts = [
"""
    
    # Add each contact as a marker
    for contact in contacts:
        lat = contact.get('LATITUDE')
        lng = contact.get('LONGITUDE')
        
        if not lat or not lng:
            continue
        
        # Build a description with available information
        info = []
        if 'CALL' in contact:
            info.append(f"Callsign: {contact['CALL']}")
        if 'NAME' in contact:
            info.append(f"Name: {contact['NAME']}")
        if 'QSO_DATE' in contact:
            date = contact['QSO_DATE']
            if len(date) == 8:  # YYYYMMDD format
                formatted_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
                info.append(f"Date: {formatted_date}")
        if 'TIME_ON' in contact:
            time = contact['TIME_ON']
            if len(time) >= 4:  # HHMM format
                formatted_time = f"{time[0:2]}:{time[2:4]}"
                info.append(f"Time: {formatted_time}")
        if 'BAND' in contact:
            info.append(f"Band: {contact['BAND']}")
        if 'MODE' in contact:
            info.append(f"Mode: {contact['MODE']}")
        if 'GRIDSQUARE' in contact:
            info.append(f"Grid: {contact['GRIDSQUARE']}")
        
        description = ", ".join(info)
        
        # Add the marker to the HTML
        html_content += f"""                {{
                    position: {{ lat: {lat}, lng: {lng} }},
                    title: "{contact.get('CALL', 'Unknown')}",
                    description: "{description}"
                }},
"""
    
    # Close the contacts array and add the rest of the JavaScript
    html_content += """            ];
            
            contacts.forEach(contact => {
                const marker = new google.maps.Marker({
                    position: contact.position,
                    map: map,
                    title: contact.title
                });
                
                bounds.extend(contact.position);
                
                marker.addListener("click", () => {
                    infoWindow.setContent(
                        `<div class="info-window">
                            <h3>${contact.title}</h3>
                            <p>${contact.description}</p>
                        </div>`
                    );
                    infoWindow.open(map, marker);
                });
            });
            
            // Adjust the map to fit all markers
            if (contacts.length > 0) {
                map.fitBounds(bounds);
            }
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