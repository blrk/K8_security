from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/mutate", methods=["POST"])
def mutate():
    request_info = request.get_json()
    
    print("Received request:", json.dumps(request_info, indent=2))

    uid = request_info["request"]["uid"]
    patches = []

    # Get all containers
    containers = request_info["request"]["object"]["spec"]["containers"]

    for i, container in enumerate(containers):
        patches.append({
            "op": "replace",
            "path": f"/spec/containers/{i}/imagePullPolicy",
            "value": "Always"
        })

    response = {
        "response": {
            "uid": uid,
            "allowed": True,
            "patchType": "JSONPatch",
            "patch": json.dumps(patches).encode("utf-8").decode("latin1")
        }
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443, ssl_context=("server.crt", "server.key"))