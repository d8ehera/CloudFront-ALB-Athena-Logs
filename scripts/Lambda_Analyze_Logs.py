import time
import boto3
import json
import io
import s3fs
import pandas as pd


# Define all the views in athena.
DATABASE = 'logsaccess'
TIMING_TABLE = 'all_report_timings'
ERRORS_TABLE = 'all_report_errors'

# S3 constant TODO Change all hardcoded values.
S3_BUCKET = 'athena-output'
S3_OUTBUCKET = 'outfiles'
S3_OUTFILE = 'users_loggedin.csv'

class AnalyticsLogs:
    def __init__(self,event):
        
        self.reference_ip = {}
        self.spm_reference_ip = {}
        
        self.s3_athena_query_output = 's3://accesslog-athena-output'
        self.fs = s3fs.S3FileSystem()
        self.client = boto3.client('athena')
            
    def athena_query(self, query):

        response = self.client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': DATABASE
                },
                ResultConfiguration={
                    'OutputLocation': self.s3_athena_query_output,
                }
            )
        
        # get query execution id
        query_execution_id = response['QueryExecutionId']
        print(query_execution_id)
        print (query)
        
        s3_outfile = query_execution_id +'.csv'
        s3_outfile_meta = query_execution_id +'.csv.metadata'
        
        query_status = 'UNKNOWN'
        max_duration = 600 #seconds
        start_time = time.time()
        
        while query_status not in ('SUCCEEDED', 'FAILED') or (time.time() - start_time) > max_duration:
            query_status = self.client.get_query_execution(QueryExecutionId=query_execution_id)
            query_status = query_status['QueryExecution']['Status']['State']
            time.sleep(10)

            if query_status == 'SUCCEEDED' or query_status == 'QUEUED' or query_status == 'RUNNING':
                print(f"STATUS: {query_status }")
            else:
                raise Exception(f"STATUS: {query_status }")
        
        # get query results
        result = self.client.get_query_results(QueryExecutionId=query_execution_id)
        
        return s3_outfile
    
    #Execute all the queries first. This creates a csv file in self.s3_athena_query_output with the execution id.csv
    def execute_query(self):
        query = f"SELECT * FROM {DATABASE}.{USERS_TABLE};"
        self.userlogin_process = self.athena_query(query=query)

    def report_timings(self):
     
        with self.fs.open(f's3://{S3_BUCKET}/{self.timing_process}') as f:
            df = pd.read_csv(f,  escapechar='\\')

        df['time'] = pd.to_datetime(df['time'].str.split('.').str[0], format='%Y-%m-%dT%H:%M:%S', utc=True).dt.tz_convert('America/New_York')
        
        userdetails = []
        for index, row in df.iterrows():
            if row['client_ip'] in self.reference_ip:
                userdetails.append(self.reference_ip[row['client_ip']])
            else:
                userdetails.append('None')
        
        df['user_details'] = userdetails
        df.drop(columns=['client_ip'], inplace=True)
        
        df = df[[c for c in df.columns if c != 'url'] + ['url']]

        df_tocsv = df.to_csv(sep="|", index=False).encode()
        
        with self.fs.open('s3://analytics.iteris-clearguide.com/report_timings.csv', 'wb') as f:
            f.write(df_tocsv)

        s3_resource = boto3.resource("s3")
        s3_resource.Object(S3_BUCKET,self.timing_process).delete()
        s3_resource.Object(S3_BUCKET,self.timing_process + '.metadata').delete()

    def report_errors(self):
        
        with self.fs.open(f's3://{S3_BUCKET}/{self.errors_process}') as f:
            df = pd.read_csv(f,  escapechar='\\')

        df['time'] = pd.to_datetime(df['time'].str.split('.').str[0], format='%Y-%m-%dT%H:%M:%S', utc=True).dt.tz_convert('America/New_York')
        userdetails = []
        for index, row in df.iterrows():
            if row['client_ip'] in self.reference_ip:
                userdetails.append(self.reference_ip[row['client_ip']])
            else:
                userdetails.append('None')
        
        df.drop(columns=['client_ip'], inplace=True)        
        df_tocsv = df.to_csv(sep="|", index=False).encode()
        
        with self.fs.open('s3://analytics.iteris-clearguide.com/error_reports.csv', 'wb') as f:
            f.write(df_tocsv)

        df['user_details'] = userdetails
        df = df[[c for c in df.columns if c != 'url'] + ['url']]

        df_tocsv = df.to_csv(sep="|", index=False).encode()
        
        with self.fs.open('s3://analytics.iteris-clearguide.com/error_reports.csv', 'wb') as f:
            f.write(df_tocsv)
            
        s3_resource = boto3.resource("s3")
        s3_resource.Object(S3_BUCKET,self.errors_process).delete()
        s3_resource.Object(S3_BUCKET,self.errors_process + '.metadata').delete()

    def execute(self):
        print ("in execute")
        self.execute_query()
        self.report_timings()
        self.report_errors()


def lambda_handler(event, context):
      
   AnalyticsLogs(event).execute()
   return True
   
