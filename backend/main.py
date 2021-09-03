import os
from os import path
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import pathlib
import random
from flask_cors import CORS
from PIL import Image, ImageOps

UPLOAD_FOLDER = "files"
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CORS(app)


def get_clients():
    if not path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    return {
        pathlib.Path(file_name).stem: file_name
        for file_name in os.listdir(UPLOAD_FOLDER)
    }


@app.route("/upload", methods=["POST"])
def fileUpload():
    clients = get_clients()
    client_id = str(random.randint(0, 1000000))
    while client_id in clients:
        client_id = str(random.randint(0, 1000000))
    file = request.files["file"]
    extension = pathlib.Path(secure_filename(file.filename)).suffix
    filename = f"{client_id}{extension}"
    destination = "/".join([UPLOAD_FOLDER, filename])
    file.save(destination)
    response = {"id": client_id}
    return response


@app.route("/get_image", methods=["GET"])
def getFile():
    clients = get_clients()
    height = request.args.get("height")
    width = request.args.get("width")
    if height and width:
        image = ImageOps.exif_transpose(Image.open(f"{UPLOAD_FOLDER}/{clients[request.args.get('client_id')]}"))
        original_size = image.size
        new_filename = f"{UPLOAD_FOLDER}/{request.args.get('client_id')}_new.png"
        image.resize((int(width), int(height))).resize(original_size).save(new_filename)
        # TODO round colors
        return send_file(new_filename)
    else:
        return send_file(f"{UPLOAD_FOLDER}/{clients[request.args.get('client_id')]}")




@app.route("/delete_client", methods=["GET"])
def deleteClient():
    clients = get_clients()
    if request.args.get("client_id") in clients:
        os.remove(f"{UPLOAD_FOLDER}/{clients[request.args.get('client_id')]}")
        return {"status": "success"}
    else:
        return {"status": "no file"}


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
