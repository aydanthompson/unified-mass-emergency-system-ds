from pathlib import Path

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct

PARAMETERS_DIR = Path(__file__).parent.parent.parent / "parameters"
DEVICE_IDS = ["1"]


class ParameterStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Root CA. Not a secret.
        root_ca_file = PARAMETERS_DIR / "AmazonRootCA1.pem"
        with open(root_ca_file, "r") as f:
            root_ca_content = f.read()

        root_ca_param = ssm.StringParameter(
            self,
            "RootCAParam",
            parameter_name="/iot/root_ca",
            string_value=root_ca_content,
            description="Shared Amazon Root CA for all IoT devices.",
        )
        root_ca_param.apply_removal_policy(RemovalPolicy.DESTROY)

        for device_id in DEVICE_IDS:
            # Device certificate.
            cert_file = PARAMETERS_DIR / f"{device_id}.cert.pem"
            with open(cert_file, "r") as cf:
                cert_content = cf.read()

            device_cert_param = ssm.StringParameter(
                self,
                f"DeviceCertParam{device_id}",
                parameter_name=f"/iot/{device_id}/device_cert",
                string_value=cert_content,
            )
            device_cert_param.apply_removal_policy(RemovalPolicy.DESTROY)

            # Private key.
            key_file = PARAMETERS_DIR / f"{device_id}.private.key"
            with open(key_file, "r") as kf:
                key_content = kf.read()

            private_key_param = ssm.StringParameter(
                self,
                f"DeviceKeyParam{device_id}",
                parameter_name=f"/iot/{device_id}/private_key",
                string_value=key_content,
            )
            private_key_param.apply_removal_policy(RemovalPolicy.DESTROY)
