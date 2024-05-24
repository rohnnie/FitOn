import json
import boto3
import os
from io import StringIO
import csv

ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
sagemaker_runtime = boto3.client('runtime.sagemaker')
ALLOW_SAGEMAKER = True

def is_csv(string):
    try:
        csv.reader(StringIO(string)).__next__()
        return True
    except Exception:
        return False

status_code = {
    'okay': 200,
    'forbidden': 403,
    'bad_request': 400
}

path_list = [ '/status', '/inference', '/help' ]
path_list = set(path_list)

request_attributes = {}

def get_payload(body = 'hello from sagemaker !', status_code = status_code['okay']):
    payload = {
        'statusCode': status_code,
        'body' : json.dumps(body)
    }
    return payload

def status_check(request_attributes):
    return get_payload(status_code = status_code['okay'])
    
def help():
    message = "The POST /inference can take upto 13 columns as follows : \n"
    columns = "Age, Sleep Duration, Physical Activity Level, Heart Rate, Daily Steps, Gender_Female, Gender_Male, BMI Category_Normal, BMI Category_Normal Weight, BMI Category_Obese, BMI Category_Overweight, Sleep Disorder_Insomnia, Sleep Disorder_Sleep Apnea \n"
    example = "example : '37,7.2,60,68,7000,True,False,True,False,False,False,False,False\n24,7.8,64,68,732,True,False,True,False,False,False,False,False)' "
    return get_payload(message + columns + example, status_code['okay'])

def bad_request(request_attributes):
    return get_payload(f'bad request : {request_attributes['method']} {request_attributes['path']}', status_code['bad_request'])

def lambda_handler(event, context):
    print("event : ")
    print(event)
    print("context : ")
    print(context)
    
    request_attributes['path'] = event['path']
    request_attributes['method'] = event['httpMethod']
    request_attributes['params'] = event['queryStringParameters']
    if event['body'] != None:
        print("TESTING ...... ")
        csv_data = list(csv.reader(StringIO(event['body'])))
        print(csv_data)
        request_attributes['body'] = json.loads(event['body'])
    else:
        request_attributes['body'] = None
    
    print("API ATTRIBUTES : ")
    print(request_attributes)
    
    if request_attributes['path'] in path_list:
        if request_attributes['path'] == '/status':
            if request_attributes['method'] == 'GET':
                return status_check(request_attributes)
            else:
                return get_payload(f'bad request : {request_attributes['method']} /status; should be GET /status', status_code['bad_request'])
        
        elif request_attributes['path'] == '/inference' and request_attributes['method'] == 'POST':
            
            payload = request_attributes['body']
            
            if is_csv(str(payload)) == True:
                
                print("CSV VERIFIED : ")
                
                payload_split = payload.split("\n")
                payload_len = len(payload_split)
                
                verify_payload = True
                error_bag = []
                error_bag_idxs = []
                for i, row in enumerate(payload_split):
                    if len(row.split(',')) != 13:
                        verify_payload = False
                        error_bag.append(row)
                        error_bag_idxs.append(i)
                
                print(f"verify_payload : {verify_payload}")
                if verify_payload == True:
                    if ALLOW_SAGEMAKER == True:
                        payload_data = str(payload)
                        print("SAGEMAKER INPUT : ")
                        print(payload_data)
                        response = sagemaker_runtime.invoke_endpoint(EndpointName = ENDPOINT_NAME,
                                                                     ContentType = 'text/csv',
                                                                     Body = payload_data)
                        result = json.loads(response['Body'].read().decode())
                        print("SAGEMAKER RESULT : ")
                        print(result)
                        return get_payload(f"inference : {result}", status_code['okay'])
                    else:
                        return get_payload(f"inference : {[0] * payload_len}", status_code['okay'])
                else:
                    err_messg = f"number of columns in payload must be equal to 13 : \n these rows {error_bag_idxs} have column lens not equal to 13 : {error_bag}"
                    return get_payload(
                        err_messg,
                        status_code['bad_request']
                    )
                    
            else:
                err_messg = f"payload body is not a csv : {payload}; \n payload body should be like : '37,7.2,60,68,7000,True,False,True,False,False,False,False,False\n24,7.8,64,68,732,True,False,True,False,False,False,False,False)' "
                return get_payload(
                    err_messg, 
                    status_code['bad_request']
                )
                
        elif request_attributes['path'] == '/help':
                return help()
                
    return bad_request(request_attributes)
