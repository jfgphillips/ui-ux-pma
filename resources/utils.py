import logging
import os

from flask import abort
from flask.views import MethodView
from flask_smorest import Blueprint

from constants import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from schemas import FileUploadSchema

blp = Blueprint("Utils", __name__, description="Utility operations")

logger = logging.getLogger(__name__)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blp.route("/utils/file")
class File(MethodView):
    @blp.arguments(FileUploadSchema, location="form", content_type="form")
    def post(self, file_data):
        upload_folder = None
        import pdb
        pdb.set_trace()
        file = file_data["profile_picture"]
        if file_data["user_type"] == "student":
            upload_folder = f"{UPLOAD_FOLDER}/students"

        elif file_data["user_type"] == "tutor":
            upload_folder = f"{UPLOAD_FOLDER}/tutors"

        if not upload_folder:
            abort(422, message="invalid user type specified")

        if file and allowed_file(file.filename):
            filename = file_data["uid"]
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            return {"filepath": filepath}, 200

        abort(422, message="invalid filepath specified")

