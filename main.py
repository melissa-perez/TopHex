import numpy as np
import os
import urllib.request
import matplotlib.pyplot as plt
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from PIL import Image

# PROGRAM CONSTANTS
IMG_EXTENSION = ('png', 'jpg', 'jpeg', 'gif')
app = Flask(__name__)
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
    return render_template('index.html')


if __name__ == '__main__':
    # starts the local host on port 5000
    app.run(debug=True, host='localhost', port='5000')
