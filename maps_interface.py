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
    operator_grid = settings.OPERATOR_GRIDSQUARE
    operator_lat = None
    operator_lon = None
    
    # Look for MY_GRIDSQUARE in contacts if not in settings
    if not operator_grid:
        for contact in contacts:
            if 'MY_GRIDSQUARE' in contact and contact['MY_GRIDSQUARE'].strip():
                from grid_converter import grid_to_coordinates
                operator_grid = contact['MY_GRIDSQUARE'].strip()
                operator_lat, operator_lon = grid_to_coordinates(operator_grid)
                break
    else:
        # Convert operator grid from settings
        from grid_converter import grid_to_coordinates
        operator_lat, operator_lon = grid_to_coordinates(operator_grid)
    
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
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="legend">
        <div><span class="operator-marker">●</span> Your location</div>
        <div><span class="contact-marker">●</span> Contact locations</div>
        <div><span class="path-line"></span> Path</div>
        <div id="contact-count">Contacts: ${len(contacts)}</div>
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
            markersArray.push(operatorMarker);
            
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
    
    # Add contact markers directly
    html_content += """
            // Create all contact markers
"""
    
    # Now we'll add each contact marker directly in the JavaScript
    for i, contact in enumerate(contacts):
        if 'LATITUDE' not in contact or 'LONGITUDE' not in contact:
            continue
            
        lat = contact.get('LATITUDE')
        lng = contact.get('LONGITUDE')
        call = contact.get('CALL', 'Unknown').replace('"', '\\"')  # Escape any quotes
        
        # Build a description with available information
        info_parts = []
        if 'CALL' in contact:
            info_parts.append(f"Callsign: {contact['CALL']}")
        if 'NAME' in contact:
            info_parts.append(f"Name: {contact['NAME']}")
        if 'QSO_DATE' in contact:
            date = contact['QSO_DATE']
            if len(date) == 8:  # YYYYMMDD format
                formatted_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
                info_parts.append(f"Date: {formatted_date}")
        if 'TIME_ON' in contact:
            time = contact['TIME_ON']
            if len(time) >= 4:  # HHMM format
                formatted_time = f"{time[0:2]}:{time[2:4]}"
                info_parts.append(f"Time: {formatted_time}")
        if 'BAND' in contact:
            info_parts.append(f"Band: {contact['BAND']}")
        if 'MODE' in contact:
            info_parts.append(f"Mode: {contact['MODE']}")
        if 'GRIDSQUARE' in contact:
            info_parts.append(f"Grid: {contact['GRIDSQUARE']}")
        
        description = ", ".join(info_parts).replace('"', '\\"')  # Escape any quotes
        
        # Add marker for this contact
        html_content += f"""
            // Contact {i+1}: {call}
            const contact{i} = new google.maps.Marker({{
                position: {{ lat: {lat}, lng: {lng} }},
                map: map,
                title: "{call}",
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 5,
                    fillColor: "#F44336",
                    fillOpacity: 0.8,
                    strokeWeight: 2,
                    strokeColor: "#B71C1C"
                }}
            }});
            
            bounds.extend({{ lat: {lat}, lng: {lng} }});
            markersArray.push(contact{i});
            
            contact{i}.addListener("click", () => {{
                infoWindow.setContent(
                    `<div class="info-window">
                        <h3>{call}</h3>
                        <p>{description}</p>
                    </div>`
                );
                infoWindow.open(map, contact{i});
            }});
"""
        
        # Add path from operator to this contact if operator location is available
        if operator_lat and operator_lon:
            html_content += f"""
            // Draw path to contact {i+1}
            const path{i} = new google.maps.Polyline({{
                path: [
                    {{ lat: {operator_lat}, lng: {operator_lon} }},
                    {{ lat: {lat}, lng: {lng} }}
                ],
                geodesic: true,
                strokeColor: "#4CAF50",
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
            }
            
            // Add a listener to update marker visibility when the map changes
            map.addListener("bounds_changed", () => {
                const mapBounds = map.getBounds();
                let visibleCount = 0;
                
                if (mapBounds) {
                    markersArray.forEach(marker => {
                        if (mapBounds.contains(marker.getPosition())) {
                            visibleCount++;
                        }
                    });
                    
                    // Update the contact count in the legend
                    document.getElementById("contact-count").textContent = `Contacts: ${visibleCount} visible of ${markersArray.length} total`;
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