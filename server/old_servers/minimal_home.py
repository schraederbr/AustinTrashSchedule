from flask import Flask, render_template_string, render_template, redirect, url_for, send_file, request, abort
import asyncio
import sys
import os
import shutil  # Add this import for creating the zip archive
import folium
import pandas as pd

sys.path.insert(0, '/home/schraederbr/AustinTrash/AustinTrashSchedule')
from async_trash import main  # Import the async function

app = Flask(__name__)

@app.route('/')
def home():
    # HTML with buttons to download samples and run async_trash.main
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Run Async Task</title>
    </head>
    <body>
        <h1>Hello from Flask!</h1>
        <form action="/download_samples" method="get">
            <button type="submit">Download Samples</button>
        </form>
        <form action="/run_async_task" method="post">
            <button type="submit">Run Async Task</button>
        </form>
        <a href="/map?csv=/home/schraederbr/AustinTrash/AustinTrashSchedule/samples/trash_date_2024-06-10.csv">
            <button type="button">Open Map</button>
        </a>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/download_samples')
def download_samples():
    samples_folder = '/home/schraederbr/AustinTrash/AustinTrashSchedule/samples'
    zip_path = '/home/schraederbr/mysite/samples.zip'

    # Ensure the samples folder exists before trying to archive it
    if os.path.exists(samples_folder):
        # Create a zip archive of the samples folder
        shutil.make_archive('/home/schraederbr/mysite/samples', 'zip', samples_folder)

        # Send the zip file as a downloadable response
        response = send_file(zip_path, as_attachment=True, download_name='samples.zip')

        # Clean up by removing the zip file after sending
        os.remove(zip_path)

        return response
    else:
        return "Samples folder does not exist.", 404

@app.route('/run_async_task', methods=['POST'])
def run_async_task():
    os.chdir('/home/schraederbr/AustinTrash/AustinTrashSchedule')
    asyncio.run(main())
    return redirect(url_for('home'))

@app.route('/map')
def map_view():
    # Get the file path from the URL parameters
    file_path = request.args.get('csv')

    if not file_path:
        return "Error: No file path provided.", 400

    try:
        # Load the data from the specified CSV file
        data = pd.read_csv(file_path)

        # Check if necessary columns are present
        if 'latitude' not in data.columns or 'longitude' not in data.columns or 'FULL_STREET_NAME' not in data.columns:
            return "Error: CSV file must contain 'latitude', 'longitude', and 'FULL_STREET_NAME' columns.", 400

        # Initialize a Folium map centered on a mean location
        m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

        # Add markers for each address
        for _, row in data.iterrows():
            folium.Marker(
                [row['latitude'], row['longitude']],
                popup=row['FULL_STREET_NAME']
            ).add_to(m)

        # Save the map to an HTML file in the templates folder
        map_path = "/home/schraederbr/mysite/templates/map.html"
        m.save(map_path)

        # Render the map.html template
        return render_template('map.html')

    except FileNotFoundError:
        return "Error: File not found.", 404
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run()
