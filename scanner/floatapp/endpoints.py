from floatapp import app
from floatapp.login import is_authenticated, query_is_photo_user, query_is_admin_user, photo_user, admin_user
from floatapp.jsonp import jsonp
from floatapp.process import thumber_pool, thumber_works
from floatapp.walker import  wait_and_scan
from PhotoAlbum import Photo
from flask import Response, abort, json, request, jsonify, make_response, send_file
from flask_login import login_user, current_user
from random import shuffle
import os
from mimetypes import guess_type

from flask_uploads import UploadSet, configure_uploads, IMAGES
albumuploadset = UploadSet('albums', IMAGES + tuple('mp4'.split()), default_dest=lambda app:app.config['ALBUM_PATH'])
albumuploadset.resolve_conflict = lambda folder, fname: fname
configure_uploads(app, (albumuploadset,))

cwd = os.path.dirname(os.path.abspath(__file__))

def find_scanner():
    return filter(lambda jb: jb.type == 'scanner', thumber_works)

@app.route("/scan", methods=['GET'])
#@admin_required
@jsonp
def check_scanner():
    try:
        walker = find_scanner()[0]
        running = walker.done
    except:
        walker = None
        running = False
    response = jsonify(code='running', running=running)
    response.cache_control.no_cache = True
    return response


@app.route("/scan", methods=['POST'])
#@admin_required
@jsonp
def start_scanner():
    try:
        _ = find_scanner()[0]
        abort(make_response(jsonify(code='running', running=True), 409))
    except:
        pass
    args = (app.config["ALBUM_PATH"], app.config["CACHE_PATH"])
    jb = thumber_pool.apply_async(wait_and_scan, args=args)
    thumber_works.append(dict(type='scanner', _jb=jb))
    response = jsonify(code='started')
    response.cache_control.no_cache = True
    return response

@app.route("/auth")
def login():
    success = False
    if current_user.is_authenticated():
        success = True
    elif query_is_photo_user(request.form) or query_is_photo_user(request.args):
        success = login_user(photo_user, remember=True)
    elif query_is_admin_user(request.form) or query_is_admin_user(request.args):
        success = login_user(admin_user, remember=True)
    if not success:
        abort(403)
    return ""

def cache_base(path):
    #path = path.replace('/', '-').replace(' ', '_').replace('(', '').replace('&', '').replace(',', '').replace(')', '').replace('#', '').replace('[', '').replace(']', '').replace('"', '').replace("'", '').replace('_-_', '-').lower()
    path = path.replace(' ', '_').replace('(', '').replace('&', '').replace(',', '').replace(')', '').replace('#', '').replace('[', '').replace(']', '').replace('"', '').replace("'", '').replace('_-_', '-').lower()
    while path.find("--") != -1:
        path = path.replace("--", "-")
    while path.find("__") != -1:
        path = path.replace("__", "_")
    if len(path) == 0:
        path = "root"
    return path

auth_list = [ ]
def read_auth_list():
    global auth_list, cwd
    f = open(os.path.join(cwd, "auth.txt"), "r")
    paths = [ ]
    for path in f:
        path = path.strip()
        paths.append(path)
        paths.append(cache_base(path))
    f.close()
    auth_list = paths

# TODO: Make this run via inotify
read_auth_list()

def check_permissions(path):
    if not is_authenticated():
        for auth_path in auth_list:
            if path.startswith(auth_path):
                abort(403)


@app.route("/albums/<path:path>")
def albums(path):
    check_permissions(path)
    return accel_redirect(app.config["ALBUM_ACCEL"], app.config["ALBUM_PATH"], path)


@app.route("/cache/<path:path>")
def cache(path):
    check_permissions(path)
    return accel_redirect(app.config["CACHE_ACCEL"], app.config["CACHE_PATH"], path)


def accel_redirect(internal, real, relative_name):
    real_path = os.path.join(real, relative_name)
    return send_file(real_path)
    internal_path = os.path.join(internal, relative_name)
    if not os.path.isfile(real_path):
        abort(405)
    mimetype = None
    types = guess_type(real_path)
    if len(types) != 0:
        mimetype = types[0]
    response = Response(mimetype=mimetype)
    response.headers.add("X-Accel-Redirect", internal_path)
    response.cache_control.public = True
    if mimetype == "application/json":
        response.cache_control.max_age = 3600
    else:
        response.cache_control.max_age = 29030400
    return response

@app.route("/photos")
@jsonp
def photos():
    f = open(os.path.join(app.config["CACHE_PATH"], "all_photos.json"), "r")
    photos = json.load(f)
    f.close()
    if not is_authenticated():
        def allowed(photo):
            for auth_path in auth_list:
                if photo.startswith(auth_path):
                    return False
            return True
        photos = [photo for photo in photos if allowed(photo)]
    count = int(request.args.get("count", len(photos)))
    random = request.args.get("random") == "true"
    if random:
        shuffle(photos)
    else:
        photos.reverse()
    response = jsonify(photos=photos[0:count])
    response.cache_control.no_cache = True
    return response


@app.route("/upload", methods=['POST'])
@jsonp
def upload():
    if request.form.get('album_path', '') == '':
        abort(make_response(jsonify(code='msg', msg='album path is missing'), 400))
    if 'pic' not in request.files:
        abort(make_response(jsonify(code='msg', msg='pic is missing'), 400))
    filename = albumuploadset.save(
                request.files['pic'],
                folder=request.form.get('album_path'))
    filepath = os.path.abspath(os.path.sep.join([app.config["ALBUM_PATH"], filename]))
    cache_path = os.path.abspath(app.config["CACHE_PATH"])
    args = (filepath, cache_path)
    kwds = dict(
            album_base=app.config['ALBUM_PATH'],
            compress=True
            )
    thumber_works.append(dict(
                type='thumber',
                filename=filename,
                album_path=request.form.get('album_path'),
                _jb=thumber_pool.apply_async(Photo, args=args, kwds=kwds)
                ))
    response = jsonify(msg=filename)
    response.cache_control.no_cache = True
    return response


def thumber_status():
    for jb in filter(lambda x: x['type'] == 'thumber', thumber_works):
        yield jb.update(dict(done=jb._jb.ready() and jb._jb.successful()))


@app.route("/upload_status")
@jsonp
def upload_status():
    response = jsonify(working=[i['done'] for i in thumber_status()])
    response.cache_control.no_cache = True
    return response
