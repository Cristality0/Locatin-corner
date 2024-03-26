import datetime

import matplotlib.pyplot as plt
import numpy as np
import smopy


def km_to_degrees(lat_km, lon_km, ref_lat: float = 45):
    lat_deg = lat_km / 110.574
    lon_deg = lon_km / (111.320 * np.cos(np.deg2rad(ref_lat)))
    return lat_deg, lon_deg


def coords_map(lat: float, lon: float, dis: float, zoom=10, route_db=None,
               datetime: datetime.datetime = None) -> plt.Axes:
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not (-180 <= lon <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    d_lat, d_lon = km_to_degrees(dis, dis, ref_lat=lat)

    # Create a new map
    output_map = smopy.Map((lat - d_lat, lon - d_lon,
                            lat + d_lat, lon + d_lon), z=zoom)
    ax = output_map.show_mpl()

    # Get coordinates for plotting
    point_x, point_y = output_map.to_pixels(lat, lon)
    lat_min, lon_min = lat - d_lat, lon - d_lon
    lat_max, lon_max = lat + d_lat, lon + d_lon
    x1, y1 = output_map.to_pixels(lat_max, lon_max)
    x3, y3 = output_map.to_pixels(lat_min, lon_min)

    # Set plot limits
    ax.set_xlim(x3, x1)
    ax.set_ylim(y3, y1)

    # Plot datetime if provided
    if datetime is not None:
        color = '#07457c'
        fontsize = 15
        ax.text(0.99, 0.99, s=datetime.strftime("%H:%M"),
                verticalalignment='top', horizontalalignment='right',
                transform=ax.transAxes, color=color, fontsize=fontsize,
                weight='bold')

    # Plot route if provided
    if route_db is not None:
        route_db = route_db.dropna(subset=['latitude', 'longitude'])
        route_db['x'], route_db['y'] = output_map.to_pixels(
            route_db['latitude'], route_db['longitude'])
        ax.plot(route_db['x'], route_db['y'], '--', color='purple', alpha=0.7,
                linewidth=2)
        ax.scatter(point_x, point_y, color='red', marker='o')
        ax.plot(point_x, point_y, "or")

    return ax

# zoom 12, 7km
# zoom 11, 13km
# zoom 10, 28km
# zoom 9, 53km
# zoom 8, 108km
