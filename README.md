# CloudFront-ALB-Athena-Logs
CloudFront Website on S3 and ALB microservices Logs Analysis.

Application Load Balancer 

1. Specify the S3 log location in the EC2 Load Balancers Attributes Access logs

2. Replace the following in ALB sql file.
 
ALB-Create-Table.sql
CREATE EXTERNAL TABLE <'database-name'.'alb-table-name'>
LOCATION - Location of ALB logs in S3
transient_lastDdlTime - Unix Time when logs was enabled.


CloudFront Logs 

1. Specify in the CloudFront distribution S3 log location.

2. In CloudFront-Create-Table.sql , replace the following  

CREATE EXTERNAL TABLE <'database-name'.'CF-table-name'>
LOCATION - Location of CF logs in S3
transient_lastDdlTime - Unix Time when logs was enabled.
