#
# observatory-dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# observatory-dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with observatory-dashboard.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=invalid-name

import datetime
import json
import os.path

from astropy.time import Time
import astropy.units as u

from flask import abort
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import send_from_directory

# pylint: disable=missing-docstring


GENERATED_DATA_DIR = '/var/www/dashboard/generated'
GENERATED_DATA = {

}

app = Flask(__name__, static_folder='../static')

# Stop Flask from telling the browser to cache dynamic files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1


@app.route('/data/<path:path>')
def generated_data(path):
    if path in GENERATED_DATA:
        return send_from_directory(GENERATED_DATA_DIR, GENERATED_DATA[path])
    abort(404)


class SiteCamera:
    def __init__(self, id, label, authorised=False, video=False, source=None):
        self.id = id
        self.label = label
        self.source_url = source or ''
        self.camera_url = '/camera/' + id
        self.video_url = '/video/' + id if video and authorised else ''


@app.route('/')
def dashboard():
    cameras = [
        SiteCamera('eumetsat', 'EUMETSAT 10.8 um', source='https://eumetview.eumetsat.int/static-images/MSG/IMAGERY/IR108/BW/index.htm'),
        SiteCamera('dome', 'Dome'),
        SiteCamera('allsky', 'All-Sky'),
        SiteCamera('telescope', 'Telescope'),
    ]

    return render_template('dashboard.html', cameras=cameras)


@app.route('/environment')
def environment():
    return render_template('environment.html')


@app.route('/camera/<path:camera>')
def camera_image(camera):
    if camera in ['eumetsat', 'allsky', 'dome', 'telescope']:
        return send_from_directory(GENERATED_DATA_DIR, camera + '.jpg')
    abort(404)


@app.route('/camera/<path:camera>/thumb')
def camera_thumb(camera):
    if camera in ['eumetsat', 'allsky', 'dome', 'telescope']:
        return send_from_directory(GENERATED_DATA_DIR, camera + '_thumb.jpg')
    abort(404)


@app.route('/data/dashboard')
def dashboard_data():
    data = json.load(open(GENERATED_DATA_DIR + '/dashboard.json'))
    return jsonify(**data)


@app.route('/data/environment')
def environment_data():
    path = 'latest.json'
    if 'date' in request.args:
        # Map today's date to today.json
        today = Time.strptime(Time.now().strftime('%Y-%m-%d'), '%Y-%m-%d') + 12 * u.hour
        if today > Time.now():
            today -= 1 * u.day

        if today.strftime('%Y-%m-%d') == request.args['date']:
            path = 'today.json'
        else:
            # Validate that it is a well-formed date
            date = Time.strptime(request.args['date'], '%Y-%m-%d')
            path = date.strftime('%Y/%Y-%m-%d.json')

    return send_from_directory(GENERATED_DATA_DIR, os.path.join('weather', path))
