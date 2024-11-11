import pandas as pd
import folium
from flask import Flask, render_template, request, abort

app = Flask(__name__)

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
    app.run(debug=True)
