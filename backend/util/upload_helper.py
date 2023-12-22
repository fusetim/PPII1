from os.path import splitext, normpath
from multiformats import multicodec, multibase, multihash, multiaddr, CID
from flask import current_app
from models.upload import Upload

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
    """
    if upload is None:
        return default
    return normpath("/{}/{}.{}".format(get_upload_dir(), upload.content_id, upload.extension))