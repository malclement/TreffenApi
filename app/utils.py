import json

from bson import json_util


# allows to serialize ObjectId
# used in @app.get("/user/info/{user_email}", tags=["user"])
def parse_json(data):
    return json.loads(json_util.dumps(data))
