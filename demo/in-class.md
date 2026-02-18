# In-Class Notes

[Official AWS REST API Tutorials](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-rest-tutorials.html)

---

## Part 1: Create REST API

- create REST API (not HTTP API), name it `demo-api`, regional endpoint
- REST API gives a visual console for resources/methods (better for teaching)
- HTTP API is cheaper and simpler but less to explore in the console
- must deploy to a stage before you can call any endpoint (HTTP API auto-deploys)

## Part 2: Mock Integration

- create `/health` resource
- add GET method, integration type: **mock**
- integration response > mapping template > `application/json`:
  ```json
  {
    "status": "ok",
    "service": "demo-api"
  }
  ```
- create `dev` stage, deploy
- curl the /health endpoint
- no Lambda, no server -- API Gateway returned this response itself

## Part 3: HTTP Pass-Through

- create `/tasks` resource
- add GET method, integration type: **HTTP**
- endpoint URL points to an external HTTP service
- API Gateway forwards the request and passes the response back
- deploy to `dev` stage, curl GET /tasks

## Part 4: Lambda Proxy Integration

- create Lambda function `mock-tasks`, container image from ECR
- add GET and POST methods on `/tasks`, integration type: **Lambda function**
- **check Lambda Proxy Integration** -- this passes the full HTTP request as the `event` object
- deploy to `dev` stage
- curl GET /tasks
- curl POST /tasks with `{"title": "Buy milk"}`
- show CloudWatch logs, walk through the event object (httpMethod, path, body, headers)

---

## Testing commands

```bash
# health check (mock)
curl https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/health

# get tasks
curl https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks

# create task
curl -X POST https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "build space ship"}'
```

---

## REST API vs HTTP API

| | REST API | HTTP API |
|---|---|---|
| console | detailed resource tree | route list |
| mock integration | yes | no |
| mapping templates | yes | no |
| JWT/OIDC auth | no (custom Lambda) | yes (built-in) |
| API keys / usage plans | yes | no |
| deploy model | manual stage deploy | auto-deploy |
| cost | ~$3.50/million | ~$1.00/million |
| latency | higher | lower |

---

## Key points

- mock: gateway returns responses with no backend at all
- HTTP pass-through: gateway forwards to an external service
- Lambda proxy: full HTTP request becomes the `event` object
- response format: `statusCode`, `headers`, `body` (body must be string via `json.dumps()`)
- CloudWatch: every Lambda invocation logged automatically
- API keys are for usage tracking/throttling, **not** authentication
- must redeploy REST API stage after any changes (HTTP API auto-deploys)

---

## Part 5: API Keys and Usage Plans

- create a **usage plan** -- set throttle (e.g. 5 req/sec) and quota (e.g. 100 req/day)
- create an **API key**
- associate the key with the usage plan, and the usage plan with your `dev` stage
- on POST /tasks, set **API Key Required = True** (method request settings)
- leave GET /tasks open (API Key Required = False)
- redeploy to `dev` stage
- demo:
  ```bash
  # denied -- no key
  curl -X POST https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks \
    -H "Content-Type: application/json" \
    -d '{"title": "build space ship"}'

  # allowed -- with key
  curl -X POST https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks \
    -H "Content-Type: application/json" \
    -H "x-api-key: YOUR_API_KEY_HERE" \
    -d '{"title": "build space ship"}'

  # still works -- GET does not require a key
  curl https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks
  ```
- show the **usage dashboard** in the console -- tracks calls per key

### when would you use API keys?

- **third-party developer access** -- give each partner/customer a key, track usage per client, set different rate limits per tier
- **internal service metering** -- multiple teams share an API, each gets a key so you can see who's driving traffic
- **abuse prevention** -- throttling prevents a single client from hammering your API
- **monetization** -- tie usage plans to billing tiers (free/basic/pro with different quotas)
- API keys answer "how much is this client using?" -- **not** "who is this?" or "are they allowed?"

---

## Part 6: Lambda Authorizer

- create Lambda function `mock-authorizer`, container image from ECR (`apigw/authorizer`)
- in API Gateway, go to **Authorizers** > create new
  - name: `demo-authorizer`
  - type: **Lambda**
  - Lambda function: `mock-authorizer`
  - Lambda event payload: **Token**
  - token source: `Authorization`
  - disable authorization caching for the demo (so every request hits the Lambda)
- on GET /tasks, change **Authorization** from NONE to `demo-authorizer`
- redeploy to `dev` stage
- demo:
  ```bash
  # denied -- no token
  curl https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks

  # denied -- wrong token
  curl -H "Authorization: Bearer wrong-token" \
    https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks

  # allowed
  curl -H "Authorization: Bearer allow-me-in" \
    https://XXXXXX.execute-api.us-east-1.amazonaws.com/dev/tasks
  ```
- show CloudWatch logs for the authorizer -- students can see the event with `authorizationToken` and `methodArn`
- the authorizer returns an IAM policy (allow/deny) -- Gateway enforces it

### how this maps to production

- in production, the token would be a JWT from an OIDC provider (Google, Okta, Cognito)
- the authorizer would validate the JWT signature, check expiration, verify claims
- OAuth2 = authorization ("can this app access this resource?")
- OIDC = authentication on top of OAuth2 ("who is this user?")
- HTTP API has a built-in JWT authorizer so you wouldn't need the Lambda at all
