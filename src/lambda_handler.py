import json
import boto3

GLUE_JOB_NAME = "b3-etl-job"

glue = boto3.client("glue")

def lambda_handler(event, context):
    """AWS Lambda entrypoint to trigger the Glue job."""
    response = glue.start_job_run(JobName=GLUE_JOB_NAME)
    return {
        "statusCode": 200,
        "body": json.dumps({"JobRunId": response["JobRunId"]})
    }