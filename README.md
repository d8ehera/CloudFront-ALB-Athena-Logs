# CloudFront-ALB-Athena-Logs
   Monitor LoadBalancer and CloudFront logs for the following 
      Users logged in.
      Response time of reports
      User Errors from UI
      Different browsers used.
      List all client IP addresses that accessed the ALB
      List the average amount of data (in kilobytes) that is passing through the ALB in request/response pairs
      
   using Athena and Logs stored in S3.


## Application Load Balancer 

   1. Specify the S3 log location in the EC2 Load Balancers Attributes Access logs

   2. Replace the following in ALB sql file.
 
   ALB-Create-Table.sql
      CREATE EXTERNAL TABLE <'database-name'.'alb-table-name'>
      LOCATION - Location of ALB logs in S3
      transient_lastDdlTime - Unix Time when logs was enabled.

## CloudFront Logs 

   1. Specify in the CloudFront distribution S3 log location.

   2. In CloudFront-Create-Table.sql , replace the following  

      CREATE EXTERNAL TABLE <'database-name'.'CF-table-name'>
      LOCATION - Location of CF logs in S3
      transient_lastDdlTime - Unix Time when logs was enabled.

## Analyze Logs Script.
   Python Script that calls Athena and gets response time and errors for all reports in the UI.
   For report timings, create a view of the table with status code as 200.

## Reference
   https://aws.amazon.com/premiumsupport/knowledge-center/athena-analyze-access-logs/