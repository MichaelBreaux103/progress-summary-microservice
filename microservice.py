# Progress Summary Microservice
# Receives a list of records and sends back how many are completed, how many
# are remaining, the percent complete, and (optionally) counts by group.
#
# Communication pipe: REST API (HTTP) on localhost, port 5002, using JSON.
# Run it with:  python microservice.py

from flask import Flask, request, jsonify

app = Flask(__name__)
PORT = 5002


def make_error(message):
    """Send back an error message with HTTP status 400."""
    print("Sent error: " + message)
    return jsonify({"error": message}), 400


def check_request(data):
    """Check the request. Returns an error message, or an empty string if everything is OK."""
    if data is None:
        return 'The request body must be JSON, like {"records": [...], "status_field": "done"}.'
    if "records" not in data or not isinstance(data["records"], list):
        return 'records is required and must be a list, like [{"title": "Essay", "done": true}].'
    for record in data["records"]:
        if not isinstance(record, dict):
            return 'Every record must be a JSON object, like {"title": "Essay", "done": true}.'
    if "status_field" not in data and "group_field" not in data:
        return 'Send at least one of status_field (like "done") or group_field (like "course").'
    if "status_field" in data and not isinstance(data["status_field"], str):
        return 'status_field must be a field name, like "done".'
    if "group_field" in data and not isinstance(data["group_field"], str):
        return 'group_field must be a field name, like "course".'
    return ""


def count_completed(records, status_field):
    """Count records whose status field is true. A missing field counts as not completed."""
    completed = 0
    for record in records:
        if status_field in record and record[status_field] is True:
            completed = completed + 1
    return completed


def count_groups(records, group_field):
    """Count how many records have each value of the group field."""
    groups = {}
    for record in records:
        if group_field in record:
            key = str(record[group_field])
        else:
            key = "(missing)"
        if key in groups:
            groups[key] = groups[key] + 1
        else:
            groups[key] = 1
    return groups


def build_summary(records, status_field, group_field):
    """Put together the totals, percent complete, and group counts."""
    total = len(records)
    completed = 0
    if status_field != "":
        completed = count_completed(records, status_field)
    remaining = total - completed

    percent = 0.0
    if total > 0:
        percent = round(completed * 100.0 / total, 1)

    summary = {
        "total": total,
        "completed": completed,
        "remaining": remaining,
        "percent_complete": percent,
    }
    if group_field != "":
        summary["groups"] = count_groups(records, group_field)
    return summary


@app.route("/summary", methods=["POST"])
def get_summary():
    """Handle a request: read the JSON, check it, and send back the summary."""
    data = request.get_json(silent=True)
    print("Received request at /summary")

    error = check_request(data)
    if error != "":
        return make_error(error)

    status_field = ""
    if "status_field" in data:
        status_field = data["status_field"]
    group_field = ""
    if "group_field" in data:
        group_field = data["group_field"]

    summary = build_summary(data["records"], status_field, group_field)
    print("Sent summary: " + str(summary["completed"]) + " of " + str(summary["total"]) + " completed")
    return jsonify(summary), 200


if __name__ == "__main__":
    print("Progress Summary microservice running on http://localhost:" + str(PORT))
    app.run(host="localhost", port=PORT)
