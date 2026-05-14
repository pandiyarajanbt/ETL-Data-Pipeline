import logging
import boto3
from django.conf import settings

logger = logging.getLogger('pipeline')


class EMRExtractor:
    """Submit and monitor EMR steps for large-scale extraction."""

    def __init__(self):
        self.client = boto3.client(
            'emr',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.cluster_id = settings.EMR_CLUSTER_ID

    def submit_spark_step(self, script_s3_path: str, args: list[str]) -> str:
        response = self.client.add_job_flow_steps(
            JobFlowId=self.cluster_id,
            Steps=[{
                'Name': 'ETL-Extract-Step',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': ['spark-submit', '--deploy-mode', 'cluster', script_s3_path] + args,
                },
            }],
        )
        step_id = response['StepIds'][0]
        logger.info(f"Submitted EMR step {step_id} on cluster {self.cluster_id}")
        return step_id

    def get_step_status(self, step_id: str) -> str:
        response = self.client.describe_step(ClusterId=self.cluster_id, StepId=step_id)
        return response['Step']['Status']['State']
