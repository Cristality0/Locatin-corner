import logging
import os
import shutil
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from get_img import coords_map
from get_location import img2location
import argparse


def process_images(image_folder: str, trip_route: str, distance: float,
                   zoom: int, overlay, overlay_size,
                   output_folder):
    """Process images from the given folder, overlay maps if specified, and
    save them to the output folder.

    Args:
        image_folder (str): _description_
        trip_route (str): _description_
        distance (float): _description_
        zoom (int): _description_
        overlay (bool, optional): _description_. Defaults to True.
        overlay_size (float, optional): _description_. Defaults to 0.4.
        output_folder (str, optional): _description_. Defaults to 'output'.
    """
    # if file extention is a file not not folder then only process that file
    if os.path.isfile(image_folder) and any([image_folder.endswith('.jpg'),
                                            image_folder.endswith('.png')]):
        images = [os.path.basename(image_folder)]
        image_folder = os.path.dirname(image_folder)
    else:
        images = os.listdir(image_folder)[:2]
    images_len = len(images)
    for i, img in enumerate(images, start=1):
        try:
            logging.info(f'Processing image {i}/{images_len}: {img}')
            img_path = os.path.join(image_folder, img)
            data_dict = img2location(img_path)
            if data_dict['latitude'] is None or data_dict['longitude'] is None:
                logging.warning(
                    f'No location data found for {img}. Skipping...')
                continue
            logging.info(f'Location data for {img}: {data_dict}')
            if trip_route is not None:
                ax = coords_map(data_dict['latitude'], data_dict['longitude'],
                                distance, zoom=zoom,
                                route_db=trip_route.copy(),
                                datetime=data_dict['datetime'])
            else:
                ax = coords_map(data_dict['latitude'], data_dict['longitude'],
                                distance, zoom=zoom,
                                datetime=data_dict['datetime'])
            if not overlay:
                # Save figure with _map suffix
                plt.savefig(os.path.join(output_folder, f'{img}_map.png'),
                            bbox_inches='tight', pad_inches=0)
                logging.info(f'Saved map for {img}')
                continue
            plt.savefig(f'temp/map{i}.png', bbox_inches='tight', pad_inches=0)
            plt.close(ax.figure)  # Clear the plot and free up memory
            logging.info(f'Saved map for {img}')
            # Overlay map on image
            img_main = Image.open(img_path)
            map_img = Image.open(f'temp/map{i}.png')
            # Resize map
            size_new = int(img_main.height * overlay_size)
            map_img = map_img.resize((size_new, size_new))
            # Paste to top right corner
            img_main.paste(map_img, (img_main.width - map_img.width, 0))
            logging.info(f'Overlaid map on {img}')
            img_main.save(os.path.join(output_folder, img))
        except Exception as e:
            logging.error(f'Error processing {img}: {str(e)}')


def master(image_folder: str, trip_route: str, distance: float, zoom: int,
           overlay: bool, output_folder: str, overlay_size: float):
    """
    Master function to process images.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s|%(asctime)s||%(message)s',
                        datefmt='%H:%M:%S')
    try:
        # Read trip route data with specified data types
        if trip_route is not None:
            if not os.path.exists(trip_route):
                raise FileNotFoundError(
                    f"Trip route file '{trip_route}' not found.")
            trip_route = pd.read_csv(trip_route)
        # Check if the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            logging.info(f'Output folder "{output_folder}" created.')
        if not os.path.exists('temp'):
            os.makedirs('temp')
        # check image_folder
        if not os.path.exists(image_folder):
            raise FileNotFoundError(
                f"Image folder '{image_folder}' not found.")
        # Process images
        process_images(image_folder, trip_route, distance, zoom, overlay,
                       overlay_size, output_folder)
        # remove temp contents
        shutil.rmtree('temp')
        os.mkdir('temp')
        logging.info('Completed processing images')
    except FileNotFoundError as e:
        logging.error(f"Error: {str(e)}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def retricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{x} not a floating-point literal")

    if 0.0 < x <= 500:
        raise argparse.ArgumentTypeError(f"{x} not in range [0.0, 500]")
    return x


# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description='Process images and overlay maps.')
    parser.add_argument('image_folder', type=str,
                        help='Folder containing input images,'
                        'or path to a single image.')
    parser.add_argument('--trip_route', type=str, default=None,
                        help='CSV file containing trip route data with columns'
                        '["latitude", "longitude"]')
    parser.add_argument('--distance', type=retricted_float, default=4.2,
                        help='Map distance from the center in km.')
    parser.add_argument('--zoom', type=int, default=13, help='Map zoom level.',
                        choices=range(5, 21))
    parser.add_argument('--overlay', type=bool, default=True,
                        help='Overlay map on image, else only save map.')
    parser.add_argument('--output_folder', type=str, default='output',
                        help='Folder to save output images.')
    parser.add_argument('--overlay_size', type=float, default=0.4,
                        help='Size of overlay map as a fraction of original '
                        'image height.')
    return parser.parse_args()


# Entry point of the script
if __name__ == '__main__':
    args = parse_args()
    master(args.image_folder, args.trip_route, args.distance, args.zoom,
           args.overlay, args.output_folder, args.overlay_size)
