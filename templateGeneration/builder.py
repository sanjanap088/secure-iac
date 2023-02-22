#!/usr/bin/env python
import cdktf_cdktf_provider_aws.s3_access_point
import cdktf_cdktf_provider_aws.s3_bucket_acl
from cdktf import App, TerraformStack, S3Backend
from cdktf_cdktf_provider_aws.instance import Instance
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket
from constructs import Construct
from get_project_root import root_path
import json
from pprint import pprint

RESOURCE_S3 = 'S3'
RESOURCE_EC2 = 'EC2'
BLOCK_BUCKET_PUBLIC_ACCESS = 'Block public access'

class MyAwsStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)
        AwsProvider(self, "AWS", region="us-west-1")

    def configure_instance(self, label="compute", instance_type="t2.micro", ami_id="ami-01456a894f71116f2"):
        Instance(self, id_=label,
                 ami=ami_id,
                 instance_type=instance_type,
                 )
        return self

    # def configure_s3_backend(self):
    #     S3Backend(self,
    #               bucket="cdktf-remote-backend-2",
    #               key="first_project/terraform.tfstate",
    #               encrypt=True,
    #               region="us-east-1",
    #               dynamodb_table="cdktf-remote-backend-lock-2",
    #               profile="CDKTF",
    #               )
    #     return self

    def configure_s3_bucket(self):
        return self


class MyAwsStackBuilder:
    def __init__(self):
        self.app = App(outdir=root_path(ignore_cwd=True))
        self.stack = None

    def _get_out_dir(self):
        return self.app.outdir

    def _new_stack(self, stack_name: str):
        self.stack = MyAwsStack(self.app, stack_name)
        return self

    def _configure_ec2_instance(self):
        self.stack.of(Instance(self.stack, "unique_config_name_ec2",
                               ami="ami_id",
                               instance_type="instance_type",
                               ))
        return self

    def _configure_s3_bucket(self):
        s3_bucket = S3Bucket(self.stack, "unique_config_name_s3",
                             bucket="bucket-name",
                             )

        public_access_block_config = cdktf_cdktf_provider_aws.s3_access_point.S3AccessPointPublicAccessBlockConfiguration(
            block_public_acls=True, block_public_policy=True, ignore_public_acls=True, restrict_public_buckets=True)
        cdktf_cdktf_provider_aws.s3_access_point.S3AccessPoint(self.stack, "unique_config_name_s3_access_point",
                                                               name="access_point_name", bucket=s3_bucket.id,
                                                               public_access_block_configuration=public_access_block_config)
        self.stack.of(s3_bucket)
        return self

    def _synthesize_json_template(self):
        self.app.synth()

    def get_terraform_stack_json(self, stack_name, resource_benchmark_map):
        self._new_stack(stack_name)
        # at the moment, for demo, we will just look for the existence of the resource key and add all the CIS
        # benchmarks implemented in the stack
        if RESOURCE_S3 in resource_benchmark_map:
            self._configure_s3_bucket()

        if RESOURCE_EC2 in resource_benchmark_map:
            self._configure_ec2_instance()

        # TODO: delete previously synthesized output artifacts if stack name already exists
        self._synthesize_json_template()

        with open(str(self._get_out_dir()) + f"/stacks/{stack_name}/cdk.tf.json") as json_data:
            generated_template = json.load(json_data)
            pprint(f'generated template = {generated_template}')
        return generated_template
        pass


# if __name__ == '__main__':
#     MyAwsStackBuilder() \
#         ._new_stack("test-stack-name-sanju-2") \
#         ._configure_ec2_instance() \
#         ._configure_s3_bucket() \
#         ._synthesize_json_template()
# RemoteBackend(stack,
#               hostname='app.terraform.io',
#               organization='<YOUR_ORG>',
#               workspaces=NamedRemoteWorkspace('learn-cdktf')
#               )
