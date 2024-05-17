import boto3

# Create EC2 client
ec2_client = boto3.client('ec2')

# Create instances
instance_response = ec2_client.run_instances(
    ImageId='ami-xxxxxxxx',  # Replace with your AMI ID
    InstanceType='t2.micro',
    MinCount=2,
    MaxCount=2,
    SecurityGroupIds=['your-security-group-id'],  # Replace with your security group ID
    KeyName='your-key-pair-name',  # Replace with your key pair name
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'Instance1'},
                # Add more tags as needed
            ]
        },
    ]
)

# Get instance IDs
instance_ids = [instance['InstanceId'] for instance in instance_response['Instances']]

# Create ELB client
elb_client = boto3.client('elbv2')

# Create target group
target_group_response = elb_client.create_target_group(
    Name='MyTargetGroup',
    Protocol='HTTP',
    Port=80,
    VpcId='your-vpc-id',  # Replace with your VPC ID
    HealthCheckProtocol='HTTP',
    HealthCheckPort='80',
    HealthCheckPath='/',
    TargetType='instance',
)

# Get target group ARN
target_group_arn = target_group_response['TargetGroups'][0]['TargetGroupArn']

# Register instances with target group
elb_client.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[{'Id': instance_id} for instance_id in instance_ids]
)

# Create load balancer security group
elb_sg_response = ec2_client.create_security_group(
    GroupName='ELBSecurityGroup',
    Description='Security group for the ELB',
    VpcId='your-vpc-id'  # Replace with your VPC ID
)

# Get load balancer security group ID
elb_sg_id = elb_sg_response['GroupId']

# Allow HTTP traffic to load balancer security group
ec2_client.authorize_security_group_ingress(
    GroupId=elb_sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

# Authorize inbound rule for instance security group from load balancer security group
ec2_client.authorize_security_group_ingress(
    GroupId='your-instance-security-group-id',  # Replace with your instance security group ID
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'UserIdGroupPairs': [{'GroupId': elb_sg_id}]
        }
    ]
)

# Create load balancer
elb_response = elb_client.create_load_balancer(
    Name='MyLoadBalancer',
    Subnets=['subnet-xxxxxx', 'subnet-xxxxxx'],  # Replace with your subnet IDs
    SecurityGroups=[elb_sg_id],
    Scheme='internet-facing',
    Tags=[
        {'Key': 'Name', 'Value': 'MyLoadBalancer'},
        # Add more tags as needed
    ]
)

# Get load balancer ARN
elb_arn = elb_response['LoadBalancers'][0]['LoadBalancerArn']

# Attach target group to load balancer
elb_client.create_listener(
    LoadBalancerArn=elb_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn}]
)

print("EC2 instances, target group, and load balancer created successfully.")