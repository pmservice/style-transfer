from flask import Flask, send_from_directory, request, make_response, Response, abort
from flask_socketio import SocketIO
import urllib
from werkzeug.utils import secure_filename
import json
from cos_helper import COSHelper
from wml_helper import WMLHelper
from get_vcap import get_wml_vcap, get_cos_vcap

app = Flask(__name__, static_url_path='/static')
#app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

wml_vcap = get_wml_vcap()
cos_vcap = get_cos_vcap()

auth_endpoint = 'https://iam.bluemix.net/oidc/token' # TODO
service_endpoint = 'https://s3-api.us-geo.objectstorage.softlayer.net'

cos_client = COSHelper(wml_vcap, cos_vcap, auth_endpoint, service_endpoint)
wml_client = WMLHelper(wml_vcap, cos_vcap, auth_endpoint, service_endpoint)

filename = "vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5"
cos_client.save_local_file(filename, "data")


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/stylesheets/<path:path>')
def send_styles(path):
    return send_from_directory('static/stylesheets', path)


@app.route('/scripts/<path:path>')
def send_js(path):
    return send_from_directory('static/scripts', path)


@app.route('/staticImages/<path:path>')
def send_img(path):
    return send_from_directory('static/images', path)


def send_experiment_feedback(msg):
    print(msg)
    socketio.emit("experiment_feedback", msg)


@app.route("/images", methods=["POST"])
def send_image():
    try:
        fileob = request.files["image_file"]
        filename = secure_filename(fileob.filename).replace(" ", "_")
        image_type = request.args.get('type', 'data')
        prefix = request.args.get('prefix', '')
        print('Saving image for params: {} {} {}'.format(filename, image_type, prefix))
        cos_client.save_image(fileob, filename, image_type, prefix=prefix)
    except Exception as e:
        print('Exception during saving image: ', e)
        abort(500, e)
    return ''


@app.route("/images/transferStyle", methods=["POST"])
def init_transfer_style():
    try:
        wml_client = WMLHelper(wml_vcap, cos_vcap, auth_endpoint, service_endpoint)
        style_image = urllib.parse.unquote(request.args.get('styleImage')).replace(" ", "_")
        base_image = urllib.parse.unquote(request.args.get('baseImage')).replace(" ", "_")
        iteration = request.args.get('iteration', 1)
        print('Transfering style initialized for params: {}, {}, {}'.format(style_image, base_image, iteration))

        send_experiment_feedback("Storing definition...")
        definition_details = wml_client._store_definition(style_image, base_image, iteration)
        definition_url = wml_client.client.repository.get_definition_url(definition_details)
        definition_uid = wml_client.client.repository.get_definition_uid(definition_details)

        send_experiment_feedback("Storing experiment...")
        experiment_details = wml_client._store_experiment(definition_url)
        experiment_uid = wml_client.client.repository.get_experiment_uid(experiment_details)

        send_experiment_feedback("Running experiment...")
        experiment_run_details = wml_client.client.experiments.run(experiment_uid, asynchronous=True)
        experiment_run_uid = wml_client.client.experiments.get_run_uid(experiment_run_details)

        training_run_uids = wml_client.client.experiments.get_training_uids(experiment_run_details)
        training_run_uid = training_run_uids[0]

        result = {
            "result_image_id": base_image.split(".")[0] + "__at_iteration_" + str(int(iteration) - 1) + ".png",
            "definition_uid": definition_uid,
            "experiment_uid": experiment_uid,
            "experiment_run_uid": experiment_run_uid,
            "training_run_uid": training_run_uid
        }

        return Response(json.dumps(result), mimetype=u'application/json')
    except Exception as e:
        print('Exception during transfering style: ', e)
        abort(500, e)


@app.route("/images/transferStyle/<experiment_run_uid>", methods=["GET"])
def get_transfer_style_status(experiment_run_uid):
    status = wml_client.client.experiments.get_status(experiment_run_uid)
    print(status)
    # status['current_iteration']
    state = status['state']
    send_experiment_feedback("Running experiment: state changed to '{}'".format(state))
    return Response(json.dumps(status), mimetype=u'application/json')


@app.route("/images/<image_name>", methods=["GET"])
def get_image(image_name):
    image_name = urllib.parse.unquote(image_name).replace(" ", "_")
    image_type = request.args.get('type', 'data')
    prefix = request.args.get('prefix', '')
    print('Getting image for params: {} {} {}'.format(image_name, image_type, prefix))
    try:
        file = cos_client.get_image(image_name, image_type, prefix=prefix)
    except Exception as e:
        print('Exception during sending image: ', e)
        abort(404, e)
    response = make_response(file)
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'attachment', filename=image_name)
    return response


@app.route("/cleanEnv", methods=["POST"])
def clean_env():
    style_image = urllib.parse.unquote(request.args.get('style_image')).replace(" ", "_")
    base_image = urllib.parse.unquote(request.args.get('base_image')).replace(" ", "_")
    result_image = urllib.parse.unquote(request.args.get('result_image')).replace(" ", "_")
    definition_uid = request.args.get('definition_uid')
    experiment_uid = request.args.get('experiment_uid')
    experiment_run_uid = request.args.get('experiment_run_uid')

    print('Cleaning image: {}'.format(style_image))
    cos_client.delete_image(style_image, 'data')

    print('Cleaning image: {}'.format(base_image))
    cos_client.delete_image(base_image, 'data')

    print('Cleaning image: {}'.format(result_image))
    cos_client.delete_image(result_image, 'results', prefix=experiment_run_uid + "/transfered_images/")

    print('Cleaning definition: {}'.format(definition_uid))
    wml_client.delete_definition(definition_uid)

    print('Cleaning experiment run: {}'.format(experiment_run_uid))
    wml_client.delete_run(experiment_run_uid)

    print('Cleaning experiment: {}'.format(experiment_uid))
    wml_client.delete_experiment(experiment_uid)

    return ''

print('Running server...')
socketio.run(app, host='0.0.0.0', port=8080)
#app.run('0.0.0.0', 8080)
