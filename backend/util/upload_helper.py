from os.path import splitext, normpath
from os.path import exists as path_exists
from multiformats import multicodec, multibase, multihash, multiaddr, CID
from flask import current_app
from models.upload import Upload
from uuid import UUID
from db import db
from werkzeug.utils import secure_filename
import os
import uuid


def allowed_file(filename):
    """
    Checks if the file extension is allowed (based on the ALLOWED_EXTENSIONS parameter)

    Args:
        flask_app (Flask): The Flask app.
        filename (str): The filename to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return get_extension(filename) in current_app.config["ALLOWED_EXTENSIONS"]


def get_extension(filename):
    """
    Gets the file extension.

    Args:
        filename (str): The filename to check.

    Returns:
        str: The file extension.
    """
    ext = splitext(filename)[1].lower()
    if ext.startswith("."):
        ext = ext[1:]
    return ext


def file_parts(filename):
    """
    Gets the file extension.

    Args:
        filename (str): The filename to check.

    Returns:
        (str, str): The file stem and extension (in lowercase for the later).
    """
    (stem, ext) = splitext(filename)
    if ext.startswith("."):
        ext = ext[1:]
    return (stem, ext.lower())


def cid_of_file(filepath):
    """
    Gets the CID of a file.

    CID is defined by Multiformats as a self-describing content-addressed identifier, a format
    that uniquely addresses the same data no matter where it is. In our case, we use the CIDv1
    base32-encoded sha2-256 hash representation of the file.

    Args:
        filepath (str): The file path. It must be a valid path, openable by the backend.

    Returns:
        str: The CID of the file.
    """
    with open(filepath, "rb") as f:
        digest = multihash.digest(f.read(), "sha2-256")
        cid = CID("base16", 1, "raw", digest)
        return cid.encode("base32")
    return None


def get_upload_dir():
    """
    Gets the upload directory.

    Returns:
        str: The upload directory.
    """
    return current_app.config["UPLOAD_FOLDER"]


def get_upload_url(upload, default=None):
    """
    Gets the URL of an upload.

    Args:
        upload (Upload or UUID): The upload data model or its UUID in database.
        default (str): The default URL to return if the upload is None.
    """
    if isinstance(upload, UUID):
        upload = db.session.get(Upload, upload)
    if upload is None:
        return default
    return normpath(
        "/{}/{}.{}".format(get_upload_dir(), upload.content_id, upload.extension)
    )


def upload_formfile(formfile, author_uid, error_on_empty=True):
    """
    Uploads a form file.

    Args:
        formfile: The form file to upload.
        author_uid (UUID): The author UID.
        error_on_empty (bool): Whether to raise an error if the form file is empty.

    Returns:
        (Upload, list[str]): The upload data model and the list of errors.
    """
    upload = None
    errors = []
    if formfile is None or formfile.filename == "":
        if error_on_empty:
            errors.append("No file provided.")
    elif not allowed_file(formfile.filename):
        errors.append("Unsupported file extension.")
    else:
        filename = secure_filename(formfile.filename)
        save_path = os.path.join(get_upload_dir(), str(uuid.uuid4()))
        try:
            if not path_exists(get_upload_dir()):
                os.mkdir(get_upload_dir())
            formfile.save(save_path)
        except:
            errors.append("An error occured while saving the file.")
        content_id = cid_of_file(save_path)
        if content_id is None:
            errors.append("Invalid file.")
        else:
            (stem, extension) = file_parts(filename)
            os.rename(save_path, os.path.join(get_upload_dir(), f"{content_id}.{extension}"))
            try:
                upload = Upload(
                    author_uid=author_uid,
                    original_filename=stem,
                    content_id=content_id,
                    extension=extension,
                )
                db.session.add(upload)
                db.session.commit()
            except:
                db.session.rollback()
                errors.append("An error occured while uploading the file.")
                return (None, errors)
    return (upload, errors)
