from flask import Flask, render_template_string, render_template, redirect, url_for, send_file, request, abort
import asyncio
import sys
import os
import shutil  # Add this import for creating the zip archive
import folium
import pandas as pd

trash_path = '/mnt/d/AustinTrashSchedule'
sys.path.insert(0, trash_path)
samples_folder = trash_path + '/samples'
from async_trash import main  # Import the async function

app = Flask(__name__)

@app.route('/')
def home():
    

    # Check if the samples folder exists
    if not os.path.exists(samples_folder):
        return "Samples folder does not exist.", 404

    # Get list of CSV files in the samples folder
    csv_files = sorted([f for f in os.listdir(samples_folder) if f.endswith('.csv')])

    # HTML for displaying home page with links to each CSV map
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Austin Trash</title>
    </head>
    <body>
        <h1>Austin Bulk Trash Collection Maps</h1>
        <form action="/download_samples" method="get">
            <button type="submit">Download CSV Files</button>
        </form>
        <form action="/run_async_task" method="post">
            <button type="submit">Reload Database (May take awhile)</button>
        </form>
        <h2>Map Links</h2>
        <ul>
            {}
        </ul>
    </body>
    </html>
    """

    # Generate list items for each CSV file link
    links = ''.join(f'<li><a href="/map?csv={os.path.join(samples_folder, file)}" target="_blank">{file}</a></li>'
                    for file in csv_files)

    # Render the HTML with links included
    return render_template_string(html.format(links))

@app.route('/download_samples')
def download_samples():

    zip_path = trash_path + '/samples.zip'

    # Ensure the samples folder exists before trying to archive it
    if os.path.exists(samples_folder):
        # Create a zip archive of the samples folder
        shutil.make_archive(samples_folder, 'zip', samples_folder)

        # Send the zip file as a downloadable response
        response = send_file(zip_path, as_attachment=True, download_name='samples.zip')

        # Clean up by removing the zip file after sending
        os.remove(zip_path)

        return response
    else:
        return "Samples folder does not exist.", 404

@app.route('/run_async_task', methods=['POST'])
def run_async_task():
    os.chdir(trash_path)
    asyncio.run(main())
    return redirect(url_for('home'))

@app.route('/map')
def map_view():
    file_path = request.args.get('csv')

    if not file_path:
        return "Error: No file path provided.", 400

    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)

    try:
        data = pd.read_csv(file_path)

        if 'latitude' not in data.columns or 'longitude' not in data.columns or 'FULL_STREET_NAME' not in data.columns:
            return "Error: CSV file must contain 'latitude', 'longitude', and 'FULL_STREET_NAME' columns.", 400

        initial_location = [user_lat, user_lon] if user_lat and user_lon else [data['latitude'].mean(), data['longitude'].mean()]
        m = folium.Map(location=initial_location, zoom_start=13, height="100vh")
        m.get_root().height = "100%"
        for _, row in data.iterrows():
            google_maps_link = f"https://www.google.com/maps/search/?api=1&query={row['latitude']},{row['longitude']}"
            apple_maps_link = f"https://maps.apple.com/?q={row['latitude']},{row['longitude']}"

            popup_html = f"""
            <div style="font-size: 18px; padding: 5px; width: 200px; background-color: #f9f9f9;">
                <b>{row['FULL_STREET_NAME']}</b><br>
                <a href="{google_maps_link}" target="_blank">Google Maps</a><br>
                <a href="{apple_maps_link}" target="_blank">Apple Maps</a>
            </div>
            """

            folium.Marker(
                [row['latitude'], row['longitude']],
                popup=popup_html
            ).add_to(m)

        if user_lat and user_lon:
            folium.Marker(
                [user_lat, user_lon],
                popup="You are here",
                icon=folium.Icon(color="red")
            ).add_to(m)

        map_html = m._repr_html_()

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Map with Current Location</title>
            <style>
                html, body, #mapid {{
                    height: 100vh;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                .folium-map {{
                    height: 100vh;
                }}



            </style>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
        </head>
        <body>
            <div id="mapid">
                {map_html}
            </div>

            <script>
                function sendLocation() {{
                    if (navigator.geolocation) {{
                        navigator.geolocation.getCurrentPosition(function(position) {{
                            var lat = position.coords.latitude;
                            var lon = position.coords.longitude;
                            window.location.href = window.location.pathname + "?csv={file_path}&lat=" + lat + "&lon=" + lon;
                        }});
                    }} else {{
                        alert("Geolocation is not supported by this browser.");
                    }}
                }}

                document.addEventListener("DOMContentLoaded", function() {{
                    const urlParams = new URLSearchParams(window.location.search);
                    if (!urlParams.has('lat') || !urlParams.has('lon')) {{
                        sendLocation();
                    }}
                }});
            </script>
        </body>
        </html>
        """.format(map_html=map_html, file_path=file_path)

        return render_template_string(html)

    except FileNotFoundError:
        return "Error: File not found.", 404
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run()
