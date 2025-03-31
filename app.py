from aws_cdk import App, CliCredentialsStackSynthesizer, Environment

from aws.stack.alert import IoTWeatherAlertStack
from aws.stack.parameter import ParameterStack
from aws.stack.simulator import IoTSimulatorStack

app = App()

account = app.node.try_get_context("account")
region = app.node.try_get_context("region")
lab_role_arn = app.node.try_get_context("lab_role_arn")
sensor_threshold = app.node.try_get_context("sensor_threshold") or 40.0

# IoTWeatherAlertStack(
#     app,
#     "IoTWeatherAlertStack",
#     lab_role_arn=lab_role_arn,
#     sensor_threshold=sensor_threshold,
#     env=Environment(account=account, region=region),
#     synthesizer=CliCredentialsStackSynthesizer(),
# )

IoTSimulatorStack(
    app,
    "IoTSimulatorStack",
    lab_role_arn=lab_role_arn,
    device_id="1",
    env=Environment(account=account, region=region),
    synthesizer=CliCredentialsStackSynthesizer(),
)

ParameterStack(
    app,
    "ParameterStack",
    env=Environment(account=account, region=region),
    synthesizer=CliCredentialsStackSynthesizer(),
)

app.synth()
