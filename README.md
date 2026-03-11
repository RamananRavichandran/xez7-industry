# PluSum – Agentic PMO Automation Platform

PluSum is an agentic AI-driven platform to automate PMO and project manager workflows for service-based companies.

This repository contains:

- A FastAPI backend with multi-agent orchestration
- An LLM layer (OpenAI primary, AWS Bedrock fallback)
- AWS integrations (DynamoDB, S3, SES, Step Functions, Lambda)
- Connectors for Slack, Microsoft Teams, and Jira
- A Streamlit frontend for dashboards and agent control

## Folder structure

- `pluSum/`
  - `api/` – FastAPI app and routes
  - `agents/` – PMO agents and event bus
  - `llm/` – LLM schemas, prompts, router
  - `integrations/` – Slack, Teams, Jira, SES, S3, DynamoDB helpers
  - `services/` – Agent, project, and auth services
  - `utils/` – Logging, retry, AWS session, error types
  - `workflows/` – Lambda handler and Step Functions definition
  - `streamlit_app/` – Streamlit dashboard and agent control UI

## Requirements

Python 3.10+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the backend locally

1. Set environment variables (or create a `.env` file) for at least:

```bash
export OPENAI_API_KEY="sk-..."
export AWS_REGION="us-east-1"
export COGNITO_USER_POOL_ID="your-user-pool-id"
export COGNITO_REGION="us-east-1"
export COGNITO_APP_CLIENT_ID="your-app-client-id"
```

2. Start the FastAPI app:

```bash
uvicorn pluSum.api.main:app --reload --port 8000
```

3. Health check:

```bash
curl http://localhost:8000/health
```

### Example agent run

Request:

```bash
curl -X POST "http://localhost:8000/agents/run" \
  -H "Authorization: Bearer <COGNITO_JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "utilization",
    "project_id": "PROJECT-123",
    "params": {
      "context": "Q2 utilization analysis for consulting projects in EMEA.",
      "timesheets": [
        {"resource_id": "user-1", "hours": 32, "capacity": 40},
        {"resource_id": "user-2", "hours": 44, "capacity": 40}
      ]
    }
  }'
```

Response (shape):

```json
{
  "correlation_id": "b8e25795-92ab-4b8d-9e0e-5f4ca23fd714",
  "status": "COMPLETED",
  "result": {
    "agent_type": "utilization",
    "payload": {
      "project_id": "PROJECT-123",
      "average_utilization": 0.78,
      "underutilized_resources": ["user-1"],
      "overutilized_resources": ["user-2"],
      "recommendations": [
        "Redistribute workload from user-2 to user-1."
      ]
    }
  },
  "evaluation": {
    "score": 0.78,
    "summary": "Average utilization 0.78",
    "severity": "medium"
  },
  "action": {
    "action_type": "notify",
    "payload": {
      "score": 0.78,
      "summary": "Average utilization 0.78",
      "severity": "medium"
    }
  }
}
```

## Running the Streamlit app

1. Ensure the backend is running on `http://localhost:8000`.

2. Set:

```bash
export PLUSUM_BACKEND_URL="http://localhost:8000"
```

3. Launch Streamlit:

```bash
streamlit run pluSum/streamlit_app/app.py
```

4. Open the browser (default `http://localhost:8501`), paste a valid Cognito JWT in the sidebar, and use the `dashboard` and `agent_control` pages.

## Deploying to AWS

### FastAPI on Lambda

1. Package the app (for example, using a Lambda container image or zipped deployment) with `mangum` included.
2. Configure a Lambda function with handler:

```text
pluSum.workflows.lambda_handlers.lambda_handler
```

3. Expose it via API Gateway (HTTP API), optionally with a Cognito authorizer.

### Step Functions

Create the state machine:

```bash
aws stepfunctions create-state-machine \
  --name PluSumMultiAgentWorkflow \
  --definition file://pluSum/workflows/state_machine_definition.json \
  --role-arn arn:aws:iam::<account-id>:role/<step-functions-role>
```

Wire each Lambda ARN in the definition to Lambdas that call `AgentService.run_agent` for the respective agent type.

### Frontend hosting

You can host the Streamlit app on EC2, ECS/Fargate, or another container platform, configured with `PLUSUM_BACKEND_URL` pointing at your API Gateway URL and using Cognito JWTs for auth.
