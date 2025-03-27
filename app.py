from aws_cdk import App, CliCredentialsStackSynthesizer

from aws.aws_stack import IoTWeatherAlertStack

app = App()

account_id = app.node.try_get_context("account_id")
lab_role_arn = app.node.try_get_context("lab_role_arn")
sensor_threshold = app.node.try_get_context("sensor_threshold") or 40.0

IoTWeatherAlertStack(
    app,
    "IoTWeatherAlertStack",
    lab_role_arn=lab_role_arn,
    sensor_threshold=sensor_threshold,
    synthesizer=CliCredentialsStackSynthesizer(),
)

app.synth()
