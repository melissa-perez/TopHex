import numpy as np
import os
import typing
import requests
import urllib.request
import matplotlib.pyplot as plt
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from PIL import Image
from numpy import asarray
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

# PROGRAM CONSTANTS
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static\\uploads\\')
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
IMAGE_MICROSERVICE_SERVER = 'http://127.0.0.1:4200'
IMAGE_QUERY_SITE = 'https://unsplash.com/s/photos/sky?orientation=squarish'
RANDOM_IMAGE_COUNTER = 0

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def valid_image(img_name) -> bool:
    """
    Determines if the img ends with a valid extension.

    :param img_name: str
    :return: bool
    """
    is_valid_name = '.' in img_name
    is_valid_ext = img_name.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

    return is_valid_name and is_valid_ext


def convert_to_jpg():
    """
    Convert img types to jpg to use in program. Only three channels.
    """
    return


def create_img_array(np_arr: np.ndarray = None,
                     from_internet: bool = False,
                     file_name: str = None,
                     url: str = None) -> np.ndarray:
    """
    Creates an of numeric values representing the
    image.

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
        np_arr = asarray(load_image_to_array)
    return np_arr


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

    :return:
    """
    # if there is a form, then proceed with rand
    if request.form:
        url = create_random_image_url()
        # print(url)
        response = requests.get(url, params={'url': IMAGE_QUERY_SITE})
        # print(response.text)
        # return response.text
        return render_template('index.html', filename=response.text, is_upload=False)

    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and valid_image(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        arr = None
        arr = create_img_array(arr, file_name=filename)
        print(arr.ndim)
        print(arr.shape)
        return render_template('index.html', filename=filename, is_upload=True)
    else:
        # flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


def create_random_image_url():
    """
    Creates the URL for a random image from some site
    and returns the string to call the image microservice.
    :return: str
    """
    url_parts = [
        IMAGE_MICROSERVICE_SERVER,
        '/image_url_query'
    ]
    return ''.join(url_parts)


if __name__ == '__main__':
    # starts the local host on port 5000
    app.run(debug=True, host='localhost', port='5000')
