from flasgger import swag_from
from flask import Blueprint, request, jsonify, render_template
from flask_cors import cross_origin
import os, time


pages = Blueprint('pages', __name__)

# index page
@pages.route("/", methods=['GET'])
@cross_origin()
def index():
    return render_template('index.html',)


# index page2 
@pages.route("/page2", methods=['GET'])
@cross_origin()
def page2():
    return render_template('pages/page2.html',)
