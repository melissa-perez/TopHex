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
from werkzeug.utils import secure_filename

# PROGRAM CONSTANTS
UPLOAD_FOLDER = 'static/uploads/'
IMG_EXTENSION = ('png', 'jpg', 'jpeg', 'gif')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
IMG_MS_SERVER = 'http://127.0.0.1:4200'
IMG_QUERY_SITE = 'https://unsplash.com/s/photos/sky?orientation=squarish'

Bootstrap(app)


def valid_image(img_name):
    """
    Determines if the img ends with a valid extension.
    :param img_name: str
    :return: bool
    """
    is_valid_name = '.' in img_name
    is_valid_ext = img_name.rsplit('.', 1)[1].lower() in IMG_EXTENSION
    return is_valid_name and is_valid_ext


@app.route('/')
def get_home_page():
    """
    Function that returns the main home page of the website.
    :return: str
    """
    return render_template('index.html')


@app.route('/', methods=['POST'])
def image_upload():
    if request.form['random_button'] == 'Random':
        url = create_random_image_url()
        print(url)
        response = requests.get(url, params={'url': IMG_QUERY_SITE})
        print(response.text)
        #return response.text
        return render_template('index.html', filename=response.text, is_upload=False)


    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and valid_image(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        # flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename)
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
        IMG_MS_SERVER,
        '/image_url_query'
    ]
    return ''.join(url_parts)

    # http://127.0.0.1:4200/image_url_query?url=https://www.google.com


if __name__ == '__main__':
    # starts the local host on port 5000
    app.run(debug=True, host='localhost', port='5000')
