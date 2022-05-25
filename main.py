import urllib

import numpy as np
import os
import requests
from PIL.Image import Palette
from flask import Flask, request, redirect, url_for, render_template
from PIL import Image
from colorthief import ColorThief
from requests import Response
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

# PROGRAM CONSTANTS

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static\\uploads\\')
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
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
        load_image_to_array = Image.open(requests.get(url, stream=True).raw)
    else:
        load_image_to_array = Image.open(f'{UPLOAD_FOLDER}/{file_name}')
    if not np_arr:
        np_arr = np.array(load_image_to_array, dtype="int32")
    load_image_to_array.close()
    return np_arr


# trying Pithikos SO answer and adapted by me for my program
def get_dominant_color(img_arr, palette_size=TOP_COLORS):
    # Resize image to speed up processing
    print(img_arr)
    print(type(img_arr))
    data = Image.fromarray((img_arr * 1).astype(np.uint8)).convert('RGB')
    print(data)
    img = data.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Palette.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    print(color_counts)
    dominant_colors = []
    for color in color_counts:
        print(color)
        palette_index = color[1]
        print(palette_index)
        dominant_colors.append(palette[palette_index * 3:palette_index * 3 + 3])

    print(dominant_colors)
    return dominant_colors


def convert_to_jpg():
    """
    Convert img types to jpg to use in program. Only three channels.
    """
    return


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


def get_img_arr_dims(arr: np.ndarray) -> None:
    """
    Prints the img shape and dimensions.

    :param arr: image array
    :return: None
    """
    if arr.any():
        print(arr.ndim)
        print(arr.shape)


@app.route('/', methods=['POST'])
def image_upload():
    """
    Displays the image to the screen.

    :return: str or Response
    """
    # if there is a form, then the image resulted from the microservice
    if request.form:
        url = create_random_image_url()
        # response is a text url
        response = requests.get(url, params={'url': IMAGE_QUERY_SITE})

        img_arr = None
        img_arr = load_img_to_array(img_arr, url=response.text, from_internet=True)
        top_hex_list = top_hex_colors(img_arr)
        return render_template('index.html', filename=response.text, is_upload=False, hex_colors=top_hex_list)
    else:
        file = request.files['file']

    if file and valid_image(file.filename):
        # image is uploaded -> secure it and store it
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_arr = None
        img_arr = load_img_to_array(img_arr, file_name=filename)
        top_hex_list = top_hex_colors(img_arr)
        top_primary = get_dominant_color(img_arr)

        for i in range(len(top_primary)):
            top_primary[i] = bytes(tuple(top_primary[i])).hex()

        top_primary = ['#' + code for code in top_primary]

        return render_template('index.html',
                               filename=filename,
                               is_upload=True,
                               colors=zip(top_hex_list,top_primary))
    else:
        return redirect(request.url)


def top_hex_colors(img_arr: np.ndarray,
                   hex_colors_list: list = None) -> list:
    """

    :param hex_colors_list:
    :param img_arr:
    :return: list
    """
    colors_dict = {}
    pixel_colors = []

    for row in img_arr:
        for col in row:
            pixel_colors.append(bytes(tuple(col)).hex())

    for color in pixel_colors:
        if color not in colors_dict:
            colors_dict[color] = 1
        else:
            colors_dict[color] += 1

    hex_colors_list = sorted(colors_dict, key=colors_dict.get, reverse=True)[:TOP_COLORS]
    hex_colors_list = ['#' + code for code in hex_colors_list]
    return hex_colors_list


def valid_image(img_name) -> bool:
    """
    Determines if the img ends with a valid extension.

    :param img_name: str
    :return: bool
    """
    is_valid_name = '.' in img_name
    is_valid_ext = img_name.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

    return is_valid_name and is_valid_ext


if __name__ == '__main__':
    # starts the local host on port 5000
    app.run(debug=True, host='localhost', port='5000')
