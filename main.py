import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

app = Flask(__name__)
