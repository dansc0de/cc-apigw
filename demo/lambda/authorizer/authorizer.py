import json


def lambda_handler(event, context):
    # log the event so students can see what the authorizer receives
    print("- authorizer received event:", json.dumps(event))

    token = event.get("authorizationToken", "")
    method_arn = event["methodArn"]

    # in production this would validate a JWT from an OIDC provider
    # for the demo we just check a hardcoded token
    if token == "Bearer allow-me-in":
        print("- token valid, generating allow policy")
        return generate_policy("student", "Allow", method_arn)

    print("- token invalid, denying access")
    raise Exception("Unauthorized")


def generate_policy(principal_id, effect, resource):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        },
    }
