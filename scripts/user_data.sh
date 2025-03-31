yum update -y
yum install -y python3

pip3 install --upgrade pip setuptools wheel
pip3 install awsiotsdk

echo "Fetching SSM parameters for device $DEVICE_ID..."

aws ssm get-parameter \
  --name "/iot/$DEVICE_ID/private_key" \
  --query "Parameter.Value" \
  --output text \
  > /home/ec2-user/private.key

aws ssm get-parameter \
  --name "/iot/$DEVICE_ID/device_cert" \
  --query "Parameter.Value" \
  --output text \
  > /home/ec2-user/cert.pem

aws ssm get-parameter \
  --name "/iot/root_ca" \
  --query "Parameter.Value" \
  --output text \
  > /home/ec2-user/AmazonRootCA1.pem

chmod 600 /home/ec2-user/private.key
chmod 644 /home/ec2-user/cert.pem
chmod 644 /home/ec2-user/AmazonRootCA1.pem
