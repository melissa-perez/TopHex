import urllib
import PIL
import numpy as np
import os
import requests
from typing import List
from flask import Flask, request, redirect, url_for, render_template
from PIL import Image
from requests import Response
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

# PROGRAM CONSTANTS
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static\\uploads\\')
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg')
IMAGE_MICROSERVICE_SERVER = 'http://127.0.0.1:4200'
IMAGE_QUERY_SITE = 'https://unsplash.com/s/photos/sky?orientation=squarish'
RANDOM_IMAGE_COUNTER = 0
TOP_COLORS = 5

# APP GLOBALS
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# PROGRAM FUNCTIONS
def load_img_to_array(np_arr: np.ndarray = None,
                      from_internet: bool = False,
                      file_name: str = None,
                      url: str = None) -> np.ndarray:
    """
    Loads the image into a numpy array.

    :param np_arr: empty object to load data into
    :param from_internet: determines if query is from microservice
    :param file_name: name for local image
    :param url: url for internet image

    :return: np.ndarray
    """
    if from_internet:
        load_image_to_array = Image.open(requests.get(url,
                                                      stream=True).raw)
    else:
        load_image_to_array = Image.open(f'{UPLOAD_FOLDER}/{file_name}')
    if not np_arr:
        np_arr = np.array(load_image_to_array, dtype='int32')
    load_image_to_array.close()
    return np_arr


# From Pithikos SO answer and adapted by me
# https://stackoverflow.com/questions/3241929/
# python-find-dominant-most-common-color-in-an-image
def get_dominant_color(img_arr, palette_size=TOP_COLORS) -> List:
    """
    Get the dominating colors by reducing palette instead of
    using the complete image palette.

    :param img_arr: np.ndarray
    :param palette_size: int
    :return: List
    """
    # Resize image to speed up processing
    data = Image.fromarray((img_arr * 1).astype(np.uint8)).convert('RGB')
    img = data.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=PIL.Image.Palette.ADAPTIVE,
                           colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    dominant_colors = []
    for color in color_counts:
        palette_index = color[1]
        dominant_colors.append(palette[palette_index * \
                                       3:palette_index * 3 + 3])

    for i in range(len(dominant_colors)):
        dominant_colors[i] = bytes(tuple(dominant_colors[i])).hex()

    dominant_colors = ['#' + code for code in dominant_colors]
    return dominant_colors


def create_random_image_url():
    """
    Creates the URL for a random image from some <<IMAGE_QUERY_SITE>>
    and returns the URL as a string.

    :return: str
    """
    url_parts = [
        IMAGE_MICROSERVICE_SERVER,
        '/image_url_query'
    ]
    return ''.join(url_parts)


def get_img_arr_dims(arr: np.ndarray) -> None:
    """
    Prints the image shape and dimensions.

    :param arr: image array
    :return: None
    """
    if arr.any():
        print(arr.ndim)
        print(arr.shape)


def top_hex_colors(img_arr: np.ndarray,
                   hex_colors_list: List = None) -> List:
    """
    Get the dominating colors from the complete image palette.

    :param hex_colors_list: empty object
    :param img_arr: array of pixels
    :return: List
    """
    colors_dict = {}
    pixel_colors = []

    # Resize image to speed up processing
    data = Image.fromarray((img_arr * 1).astype(np.uint8)).convert('RGB')
    img = data.copy()
    img.thumbnail((100, 100))
    img_arr = np.array(img, dtype='int32')

    for row in img_arr:
        for col in row:
            pixel_colors.append(bytes(tuple(col)).hex())

    for color in pixel_colors:
        if color not in colors_dict:
            colors_dict[color] = 1
        else:
            colors_dict[color] += 1

    if hex_colors_list is None:
        hex_colors_list = sorted(colors_dict, key=colors_dict.get, reverse=True)[:TOP_COLORS]
        hex_colors_list = ['#' + code for code in hex_colors_list]

    return hex_colors_list


def valid_image(img_name: str) -> bool:
    """
    Determines if the img ends with a valid extension.

    :param img_name: image name
    :return: bool
    """
    is_valid_name = '.' in img_name
    is_valid_ext = img_name.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS
    return is_valid_name and is_valid_ext


@app.route('/display/<filename>')
def display_image(filename: str) -> Response:
    """
    Displays the image at filename location with a redirect response.

    :param filename: name of file to display
    :return: Response
    """
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/')
def get_home_page():
    """
    Function that returns the main home page of the website.

    :return: str
    """
    return render_template('index.html')


@app.route('/', methods=['POST'])
def image_upload():
    """
    Displays the image to the screen.

    :return: str or Response
    """
    img_arr = None

    if request.form:
        url = create_random_image_url()
        # response is a text url
        response = requests.get(url, params={'url': IMAGE_QUERY_SITE})
        img_arr = load_img_to_array(img_arr, url=response.text,
                                    from_internet=True)
    else:
        file = request.files['file']

    if file and valid_image(file.filename):
        # secure uploaded file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_arr = load_img_to_array(img_arr, file_name=filename)
    else:
        return redirect(request.url)

    top_hex_list = top_hex_colors(img_arr)
    top_primary = get_dominant_color(img_arr)

    if request.form:
        return render_template('index.html', filename=response.text,
                               is_upload=False,
                               colors=zip(top_hex_list, top_primary))
    elif file:
        return render_template('index.html',
                               filename=filename,
                               is_upload=True,
                               colors=zip(top_hex_list, top_primary))
    return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
