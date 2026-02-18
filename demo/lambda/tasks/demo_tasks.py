import json


def lambda_handler(event, context):
    # log the full event so students can see it in cloudwatch
    print("- received event:", json.dumps(event))

    method = event["httpMethod"]
    path = event["path"]

    # GET /tasks - return a hardcoded task list
    if method == "GET" and path == "/tasks":
        tasks = [
            {"id": 1, "title": "finish cloud computing homework"},
            {"id": 2, "title": "study for midterm"},
            {"id": 3, "title": "eat at the porch"},
        ]
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"tasks": tasks}),
        }

    # POST /tasks - echo back the posted task with an id
    if method == "POST" and path == "/tasks":
        try:
            body = json.loads(event.get("body", "{}"))
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "invalid json in request body"}),
            }

        new_task = {
            "id": 99,
            "title": body.get("title", "untitled task"),
        }
        print("- created task:", json.dumps(new_task))

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"task": new_task}),
        }

    # fallback for unhandled routes
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": f"no route for {method} {path}"}),
    }
