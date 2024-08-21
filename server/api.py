from flask import Blueprint, request, current_app, Response, jsonify
from flask import make_response
import http.client
from jf import JobEntry

api = Blueprint("api", __name__, template_folder="templates")

KEY_DOES_NOT_EXIST = "Key %s does not exist!"
NO_ACCESS_TO_ENTRY = "Cannot access the content associated with key %s. Owned by other user!"
NO_CONTENT_IN_REQUEST_BODY = "No 'content' in request body. The request must provide the content!"
PUT_SUCCESS = "Successfully added the content."

# Response status
OK = http.client.OK                   # 200
BAD_REQUEST = http.client.BAD_REQUEST  # 400
NOT_FOUND = http.client.NOT_FOUND     # 404

@api.route("/<key>", methods=["GET"])
def get(key):
    # request_body = request.json
    jf = current_app.jf

    job_content = jf.get(key)

    if job_content is None:
        return Response(KEY_DOES_NOT_EXIST % (key), NOT_FOUND)

    # Return the file content with a status of OK
    return make_response(job_content.title, 200)
