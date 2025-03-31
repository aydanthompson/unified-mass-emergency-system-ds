from pathlib import Path

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from constructs import Construct


class IoTSimulatorStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        lab_role_arn: str,
        device_id: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        lab_role = iam.Role.from_role_arn(
            self,
            "LabRole",
            role_arn=lab_role_arn,
            mutable=False,
        )

        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        sg = ec2.SecurityGroup(
            self,
            "SimSG",
            vpc=vpc,
            description="Security group for the IoT simulator instance.",
            allow_all_outbound=True,
        )

        # Read EC2 setup script.
        script_dir = Path(__file__).parent.parent.parent / "scripts"
        script_path = script_dir / "user_data.sh"
        with open(script_path, "r") as f:
            base_user_data = f.read()

        # Read IoT simulator Python code.
        sim_py_path = script_dir / "iot_simulator.py"
        with open(sim_py_path) as f:
            simulator_code = f.read()

        # Formatting this is pain.
        # `cat << 'EOF' > ...` is called a "here document".
        # `2>&1` sends both stdout and stderr output to sim.log.
        # `&` runs the command in the background.
        final_user_data = f"""\
#!/bin/bash
DEVICE_ID="{device_id}"

{base_user_data}

cat << 'EOF' > /home/ec2-user/iot_simulator.py
{simulator_code}
EOF

chmod +x /home/ec2-user/iot_simulator.py

nohup python3 /home/ec2-user/iot_simulator.py > /home/ec2-user/sim.log 2>&1 &
"""

        instance = ec2.Instance(
            self,
            "IoTSimulatorInstance",
            instance_type=ec2.InstanceType("t4g.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64,
            ),
            vpc=vpc,
            role=lab_role,
            security_group=sg,
        )
        instance.add_user_data(final_user_data)

        CfnOutput(self, "IoTSimulatorInstanceID", value=instance.instance_id)
        CfnOutput(self, "IoTSimulatorDNS", value=instance.instance_public_dns_name)
