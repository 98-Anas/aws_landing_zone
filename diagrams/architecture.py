# architecture.py
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, EC2AutoScaling
from diagrams.aws.network import VPC, InternetGateway, RouteTable, ELB, NATGateway
from diagrams.aws.storage import S3
from diagrams.aws.management import Cloudwatch, Cloudtrail
from diagrams.aws.security import IAMRole, IAM
from diagrams.aws.general import User
from diagrams.onprem.client import Client

with Diagram("AWS Landing Zone Architecture", show=False, direction="TB"):
    # Title and Legend
    title = "AWS Free Tier Landing Zone"
    legend = "Green: Free Tier Components | Blue: Core Infrastructure"
    
    # IAM Components
    with Cluster("IAM Management"):
        iam_role = IAMRole("EC2InstanceRole\n(S3ReadOnlyAccess)")
        iam_policy = IAM("SecurityPolicy\n(MinimumPrivileges)")
    
    # Developer Access
    developer = User("Developer")
    ci_cd = Client("GitHub Actions")
    
    with Cluster("VPC (10.0.0.0/16)", graph_attr={"bgcolor": "lightblue"}):
        igw = InternetGateway("IGW")
        
        # Public Subnet Components
        with Cluster("Public Subnet (10.0.1.0/24)"):
            public_rt = RouteTable("PublicRT")
            bastion = EC2("Bastion Host\n(t2.micro)")
            lb = ELB("Application LB\n(Free Tier)")
            nat_instance = EC2("NAT Instance\n(t2.micro)")
            
            public_rt - [bastion, lb, nat_instance]
            igw >> public_rt
        
        # Private Subnet Components
        with Cluster("Private Subnet (10.0.2.0/24)"):
            private_rt = RouteTable("PrivateRT")
            app_servers = EC2AutoScaling("App Servers\n(t2.micro x2)")
            private_rt - app_servers
            private_rt >> nat_instance >> public_rt
    
    # Logging and Monitoring
    with Cluster("Logging & Monitoring", graph_attr={"bgcolor": "lightgreen"}):
        s3_bucket = S3("FlowLogs Bucket\n(Encrypted)")
        cloudwatch = Cloudwatch("CloudWatch\n(Alarms & Metrics)")
        cloudtrail = Cloudtrail("CloudTrail\n(API Logging)")
        
        flow_logs = VPC("VPC Flow Logs")
        flow_logs >> [s3_bucket, cloudwatch]
    
    # Connections
    developer >> Edge(color="darkgreen") >> bastion
    bastion >> Edge(color="red", style="dashed") >> app_servers
    
    lb >> Edge(color="blue") >> app_servers
    app_servers - Edge(color="orange") - iam_role
    iam_role - Edge(color="black") - iam_policy
    
    ci_cd >> Edge(color="purple", label="CI/CD") >> [lb, app_servers]
    
    # Free Tier Annotations
    free_tier = IAM("Free Tier Eligible")
    free_resources = [lb, nat_instance, s3_bucket, cloudwatch, cloudtrail]
    for resource in free_resources:
        resource << Edge(color="green", style="bold") << free_tier

    # Security Boundaries
    with Cluster("Security Boundary"):
        [flow_logs, cloudtrail] >> Edge(color="red", style="dotted") >> s3_bucket