import pandas as pd
import folium
from flask import Flask, render_template, send_file

# # Load the data from samples.csv
# data = pd.read_csv('/home/schraederbr/AustinTrash/AustinTrashSchedule/samples/trash_date_2024-06-10.csv')

# # Initialize a Folium map centered on a mean location
# m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

# # Add markers for each address
# for _, row in data.iterrows():
#     folium.Marker(
#         [row['latitude'], row['longitude']],
#         popup=row['FULL_STREET_NAME']
#     ).add_to(m)

# # Save the map to an HTML file
# map_path = "/home/schraederbr/mysite/map.html"
# m.save(map_path)



# # Load the data from samples.csv
# data = pd.read_csv('/home/schraederbr/AustinTrash/AustinTrashSchedule/samples/trash_date_2024-06-10.csv')

# print("Data loaded:", data.head())
# print("Latitude mean:", data['latitude'].mean())
# print("Longitude mean:", data['longitude'].mean())


# # Initialize a Folium map centered on a mean location
# m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

# # Add markers for each address
# for _, row in data.iterrows():
#     folium.Marker(
#         [row['latitude'], row['longitude']],
#         popup=row['FULL_STREET_NAME']
#     ).add_to(m)

# # Save the map to an HTML file
# map_path = "/home/schraederbr/mysite/map.html"
# m.save(map_path)


# import pdb; pdb.set_trace()

app = Flask(__name__)

@app.route('/')
def map_view():
    # Load the data from samples.csv
    data = pd.read_csv('/home/schraederbr/AustinTrash/AustinTrashSchedule/samples/trash_date_2024-06-10.csv')

    # Initialize a Folium map centered on a mean location
    m = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

    # Add markers for each address
    for _, row in data.iterrows():
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=row['FULL_STREET_NAME']
        ).add_to(m)

    # Save the map to an HTML file
    map_path = "/home/schraederbr/mysite/templates/map.html"
    m.save(map_path)

    # Render the map.html template
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
