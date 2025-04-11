# maps_interface.py
"""
Module for interfacing with Google Maps API to display contacts and paths
"""

import os
import webbrowser
from datetime import datetime

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
    operator_grid = None
    operator_lat = None
    operator_lon = None
    
    # Look for MY_GRIDSQUARE in contacts
    for contact in contacts:
        if 'MY_GRIDSQUARE' in contact and contact['MY_GRIDSQUARE'].strip():
            from grid_converter import grid_to_coordinates
            operator_grid = contact['MY_GRIDSQUARE'].strip()
            operator_lat, operator_lon = grid_to_coordinates(operator_grid)
            break
    
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
        }}
        .contact-marker {{
            color: red;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="legend">
        <div><span class="operator-marker">●</span> Your location</div>
        <div><span class="contact-marker">●</span> Contact locations</div>
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
    
    # Add each contact as a marker
    html_content += """
            // Create markers for each contact
            const contacts = [
"""
    
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
    
    # Close the contacts array and add marker creation code
    html_content += """            ];
            
            // Create markers for all contacts
            contacts.forEach(contact => {
                const marker = new google.maps.Marker({
                    position: contact.position,
                    map: map,
                    title: contact.title,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 5,
                        fillColor: "#F44336",
                        fillOpacity: 0.8,
                        strokeWeight: 2,
                        strokeColor: "#B71C1C"
                    }
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
"""
    
    # Add paths from operator to contacts if operator grid is available
    if operator_lat and operator_lon:
        html_content += """
                // Create path from operator to this contact
                if (operatorPosition) {
                    const path = new google.maps.Polyline({
                        path: [operatorPosition, contact.position],
                        geodesic: true,
                        strokeColor: "#4CAF50",
                        strokeOpacity: 0.6,
                        strokeWeight: 2
                    });
                    path.setMap(map);
                }
"""
    
    # Close forEach loop and add final code
    html_content += """            });
            
            // Adjust the map to fit all markers
            if (bounds.isEmpty() === false) {
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