from flask import render_template, jsonify, request
from flask.ext.uploads import DEFAULTS, UploadSet, configure_uploads
from app import app, thumbnail, models, db
from flask.ext.login import login_required, current_user
import random
import uuid
import sys, os

uploads = UploadSet('uploads', DEFAULTS)

configure_uploads(app, uploads)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST' and 'file' in request.files:
        unique_filename = uuid.uuid4().hex
        filename = uploads.save(request.files['file'], name=unique_filename + '.')
        thumbnail.generate_thumbnail(unique_filename, 'app/static/')
        file_path = os.path.join('app/static/uploads/', filename)
        description = 'enter something'
        uploaded_file = models.File(file_path=file_path, description=description)
        current_user.add_files([(uploaded_file, 1)])
        db.session.commit()
        return render_template('user/files.html')
    return render_template('upload.html')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/map')
def map():
    return render_template('map.html', title='Map')


@app.route('/map/refresh', methods=['POST'])
def map_refresh():
    points = [(random.uniform(48.8434100, 48.8634100),
               random.uniform(2.3388000, 2.3588000))
              for _ in range(random.randint(2, 9))]
    return jsonify({'points': points})


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')
