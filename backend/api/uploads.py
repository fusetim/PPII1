from flask import Blueprint, jsonify, request
from sqlalchemy import select
from models.upload import Upload
from db import db
from flask_login import login_required, current_user
from util.upload_helper import allowed_file, file_parts, cid_of_file, get_upload_dir, get_upload_url
import os
from os.path import exists as path_exists
from werkzeug.utils import secure_filename
import uuid


# Creates the "router" (aka blueprint in Flask)
bp = Blueprint("uploads", __name__)

@bp.route("/add", methods=["POST"])
@login_required
def add():
    """
    Uploading route, used to upload a file to the server, for an user.

    The user must be logged in to use this route.

    Example (request built with curl):
        curl -X POST -F "file=@/path/to/file" http://localhost:5000/api/uploads/add
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file provided."}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(get_upload_dir(), str(uuid.uuid4()))
        try:
            if not path_exists(get_upload_dir()):
                os.mkdir(get_upload_dir())
            file.save(save_path)
        except:
            return jsonify({"error": "An error occured while saving the file."}), 500
        content_id = cid_of_file(save_path)
        if content_id is None:
            return jsonify({"error": "Invalid file."}), 400
        (stem, extension) = file_parts(filename)
        upload = None
        try:
            os.rename(save_path, os.path.join(get_upload_dir(), f"{content_id}.{extension}"))
            upload = Upload(
                author_uid=current_user.user_uid,
                original_filename=stem,
                content_id=content_id,
                extension=extension,
            )
            db.session.add(upload)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"error": "An error occured while uploading the file."}), 500
        return jsonify({"cid": content_id, "upload_uid": upload.upload_uid, "url": get_upload_url(upload)}), 200
    return jsonify({"error": "Unsupported file extension."}), 400