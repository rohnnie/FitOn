from django.http import JsonResponse
from django.shortcuts import render, redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
from asgiref.sync import sync_to_async
import asyncio
import datetime
import pandas as pd
from user.models import User
import random
import requests
import ast
import pytz
import boto3
from django.conf import settings
# from aws_conf import get_dynamodb_resource
from collections import defaultdict

def get_dynamodb_resource():
    id = settings.DYNAMO_ID
    key = settings.DYNAMO_KEY
    return boto3.resource(
        'dynamodb',
        region_name='us-east-2',
        aws_access_key_id=id,
        aws_secret_access_key=key
    )

dataTypes = {
    "heart_rate": "com.google.heart_rate.bpm",
    "resting_heart_rate": "com.google.heart_rate.bpm",
    "steps": "com.google.step_count.delta",
    "sleep": "com.google.sleep.segment",
    "oxygen": "com.google.oxygen_saturation",
    "activity": "com.google.activity.segment",
    "glucose": "com.google.blood_glucose",
    "pressure": "com.google.blood_pressure"
}

df = pd.read_csv('google_fit_activity_types.csv')

#function to convert miliseconds to Day
def parse_millis(millis):
    return datetime.datetime.fromtimestamp(int(millis) / 1000).strftime("%b %d, %I %p")

def list_metrics(request):
    return render(request, 'metrics/metric_list.html')

def steps_barplot(data):
    # Your steps data
    print("inside steps function\n")
    steps_data=[]
    for record in data['bucket']:
        if len(record['dataset'][0]['point'])==0:
            continue
        else:
            d={}
            d['start']=parse_millis(record['startTimeMillis'])
            d['end']=parse_millis(record['endTimeMillis'])
            d['count']=record['dataset'][0]['point'][0]['value'][0]['intVal']
            steps_data.append(d)

    # Pass the plot path to the template
    context = {'steps_data_json': steps_data}
    return context

def heartrate_plot(data):
    print("inside heart function\n")
    heart_data=[]
    for record in data['bucket']:
        if len(record['dataset'][0]['point'])==0:
            continue
        else:
            d={}
            d['start']=parse_millis(record['startTimeMillis'])
            d['end']=parse_millis(record['endTimeMillis'])
            d['count']=float(record['dataset'][0]['point'][0]['value'][0]['fpVal'])
            d['min']=int(record['dataset'][0]['point'][0]['value'][1]['fpVal'])
            d['max']=int(record['dataset'][0]['point'][0]['value'][2]['fpVal'])
            heart_data.append(d)

    # Pass the plot path to the template
    context = {'heart_data_json': heart_data}
    return context

def resting_heartrate_plot(data):
    print("inside resting heart function\n")
    resting_heart_data=[]
    for record in data['bucket']:
        if len(record['dataset'][0]['point'])==0:
            continue
        else:
            d={}
            d['start']=parse_millis(record['startTimeMillis'])
            d['end']=parse_millis(record['endTimeMillis'])
            d['count']=int(record['dataset'][0]['point'][0]['value'][0]['fpVal'])
            resting_heart_data.append(d)

    # Pass the plot path to the template
    context = {'resting_heart_data_json': resting_heart_data}
    return context

def sleep_plot(data):
    print("inside sleep function\n")
    sleep_data=[]
    for record in data['session']:
        d={}
        d['start']=parse_millis(record['startTimeMillis'])
        d['end']=parse_millis(record['endTimeMillis'])
        d['count']=(int(record['endTimeMillis']) - int(record['startTimeMillis']))/1000/60/60
        sleep_data.append(d)

    # Pass the plot path to the template
    context = {'sleep_data_json': sleep_data}
    return context   

def activity_plot(data):
    print("inside activity function\n")
    activity_data={}
    for record in data['session']:
        activity_name = df.loc[df['Integer'] == record['activityType']]['Activity Type'].values
        if len(activity_name) == 0:
            continue
        act=activity_name[0]
        duration=(int(record['endTimeMillis']) - int(record['startTimeMillis']))/1000/60        
        if act in activity_data:
            activity_data[act] += int(duration)
        else:
            activity_data[act] = int(duration)
    
    activity_data = sorted(activity_data.items(), key=lambda x: x[1], reverse=True)
    activity_data = activity_data[:10]

    # Pass the plot path to the template
    context = {'activity_data_json': activity_data}
    return context  

def oxygen_plot(data):
    print("inside oxygen saturation function\n")
    oxygen_data=[]
    for record in data['bucket']:
        if len(record['dataset'][0]['point'])==0:
            continue
        else:
            d={}
            d['start']=parse_millis(record['startTimeMillis'])
            d['end']=parse_millis(record['endTimeMillis'])
            d['count']=int(record['dataset'][0]['point'][0]['value'][0]['fpVal'])
            oxygen_data.append(d)

    # Pass the plot path to the template
    context = {'oxygen_data_json': oxygen_data}
    return context

def glucose_plot(data):
    print("inside blood glucose function\n")
    oxygen_data=[]
    for record in data['bucket']:
        if len(record['dataset'][0]['point'])==0:
            continue
        else:
            d={}
            d['start']=parse_millis(record['startTimeMillis'])
            d['end']=parse_millis(record['endTimeMillis'])
            d['count']=int(record['dataset'][0]['point'][0]['value'][0]['fpVal'])
            oxygen_data.append(d)

    # Pass the plot path to the template
    context = {'glucose_data_json': oxygen_data}
    return context

def pressure_plot(data):
    print("inside blood pressure function\n")
    oxygen_data=[]
    for record in data['bucket']:
        if len(record['dataset'][0]['point'])==0:
            continue
        else:
            d={}
            d['start']=parse_millis(record['startTimeMillis'])
            d['end']=parse_millis(record['endTimeMillis'])
            d['count']=int(record['dataset'][0]['point'][0]['value'][0]['fpVal'])
            oxygen_data.append(d)

    # Pass the plot path to the template
    context = {'pressure_data_json': oxygen_data}
    return context

def get_group_key(time, frequency):
    """Adjusts start and end times based on frequency."""
    if frequency == 'hourly':
        start = time.replace(minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(hours=1)
    elif frequency == 'daily':
        start = time.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=1)
    elif frequency == 'weekly':
        start = time - datetime.timedelta(days=time.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=7)
    elif frequency == 'monthly':
        start = time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=(time.replace(month=time.month % 12 + 1, day=1) - time).days)
    else:
        start = time  # Fallback to the exact time if frequency is unrecognized
        end = time

    return start, end

def process_dynamo_data(items, frequency):
    # Dictionary to hold the data grouped by date
    print("Items in dictionary", items)
    date_groups = defaultdict(list)

    # Process each item
    for item in items:
        time = datetime.datetime.strptime(item['time'], '%Y-%m-%dT%H:%M')
        start, end = get_group_key(time, frequency)
        start_key = start.strftime('%b %d, %I %p')
        end_key = end.strftime('%b %d, %I %p')
        value = float(item['value'])
        date_groups[(start_key, end_key)].append(value)


    # Prepare the final data structure
    result = []

    for (start_key, end_key), values in date_groups.items():
        avg_count = sum(values) / len(values) if values else 0
        result.append({
            'start': start_key,
            'end': end_key,
            'count': avg_count,
        })

    return {'Items': result}


def merge_data(existing_data, new_data, frequency):
    """
    Merges new data into existing data based on overlapping time ranges defined by frequency.
    
    Parameters:
    existing_data (list): The existing list of data points for a metric.
    new_data (list): The new data points to be merged.
    frequency (str): The frequency of data collection ('hourly', 'daily', 'weekly', 'monthly').

    Returns:
    list: Updated list of data points after merging.
    """
    # Helper to parse datetime from string
    def parse_time(time_str):
        return datetime.datetime.strptime(time_str, '%b %d, %I %p')

    # Create index of existing data by start time for quick access
    data_index = {}
    for item in existing_data:
        start, end = get_group_key(parse_time(item['start']), frequency)
        data_index[start] = item
        item['end_range'] = end  # Temporarily store the range end to use in comparisons

    # Process each new data point
    for new_item in new_data:
        new_start, new_end = get_group_key(parse_time(new_item['start']), frequency)
        if new_start in data_index:
            # There's an overlap, so update the existing entry
            existing_item = data_index[new_start]
            # Averaging the counts, updating mins and maxs
            existing_item['count'] = (existing_item['count'] + new_item['count']) / 2
            existing_item['min'] = min(existing_item['min'], new_item['min'])
            existing_item['max'] = max(existing_item['max'], new_item['max'])
        else:
            # No overlap, append this new item
            new_item['end'] = new_end.strftime('%b %d, %I %p')  # Format end time for consistency
            existing_data.append(new_item)

    # Remove temporary 'end_range' from existing items
    for item in existing_data:
        item.pop('end_range', None)
    
    existing_data.sort(key=lambda x: parse_time(x['start']))
    
    combined_data = []
    for obj in existing_data:
        if not combined_data or parse_time(combined_data[-1]['start']) != parse_time(obj['start']):
            combined_data.append(obj)
        else:
            combined_data[-1]['count'] += obj['count']

    return combined_data

async def fetch_metric_data(service, metric, total_data, duration, frequency, email):
    
    end_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
    
    if duration == "day":
        start_time = end_time - datetime.timedelta(hours=23, minutes=59)
    elif duration == "week":
        start_time = end_time - datetime.timedelta(days=6, hours=23, minutes=59)
    elif duration == "month":
        start_time = end_time - datetime.timedelta(days=29, hours=23, minutes=59)
    elif duration == "quarter":
        start_time = end_time - datetime.timedelta(days=89, hours=23, minutes=59)
    
    if frequency == "hourly":
        bucket = 3600000
    elif frequency == "daily":
        bucket = 86400000
    elif frequency == "weekly":
        bucket = 604800000
    elif frequency == "monthly":
        bucket = 2592000000
    
    print(start_time.timestamp())
    print(end_time.timestamp())
    
    start_date = start_time.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end_date = end_time.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print(start_date)
    print(end_date)
    
    if metric == "sleep":
        data = service.users().sessions().list(userId='me', activityType=72, startTime=f'{start_date}', endTime=f'{end_date}').execute()
    elif metric == "activity":
        data = service.users().sessions().list(userId='me', startTime=f'{start_date}', endTime=f'{end_date}').execute()
    else:        
        data = service.users().dataset().aggregate(userId='me', body={
            "aggregateBy": [{
                "dataTypeName": dataTypes[metric]
            }],
            "bucketByTime": {"durationMillis": bucket},
            "startTimeMillis": int(start_time.timestamp()) * 1000,
            "endTimeMillis": int(end_time.timestamp()) * 1000,
        }).execute()
    
    if metric=="heart_rate":
        context=heartrate_plot(data)
        total_data['heartRate']=context
    elif metric=="steps":
        context=steps_barplot(data)
        total_data['steps']=context
    elif metric=="resting_heart_rate":
        context=resting_heartrate_plot(data)
        total_data['restingHeartRate']=context
    elif metric=="sleep":
        context=sleep_plot(data)
        total_data['sleep']=context
    elif metric=="activity":
        context=activity_plot(data)
        total_data['activity']=context
    elif metric=="oxygen":
        context=oxygen_plot(data)
        total_data['oxygen']=context
    elif metric=="glucose":
        context=glucose_plot(data)
        total_data['glucose']=context
    elif metric=="pressure":
        context=pressure_plot(data)
        total_data['pressure']=context
    table = get_dynamodb_resource().Table('Django')
    response = table.scan(
        FilterExpression="metric = :m AND #t BETWEEN :start AND :end AND email = :email",
        ExpressionAttributeNames={"#t": "time"},
        ExpressionAttributeValues={
            ":m": metric,
            ":email": email,
            ":start": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            ":end": end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    )
    
    print("printing processed data from DynamoDB--------------------------------")

    processed_data = process_dynamo_data(response['Items'], frequency)
    # print("processed data", processed_data)

    # Assuming 'processed_data' is structured similarly for each metric
# and 'frequency' is defined appropriately for the context in which this is run

    if metric == "heart_rate":
        print("heart rate")
        total_data['heartRate']['heart_data_json'] = merge_data(total_data['heartRate']['heart_data_json'], processed_data['Items'], frequency)
    elif metric == "steps":
        print("steps")
        total_data['steps']['steps_data_json'] = merge_data(total_data['steps']['steps_data_json'], processed_data['Items'], frequency)
    elif metric == "resting_heart_rate":
        print("resting heart rate")
        total_data['restingHeartRate']['resting_heart_data_json'] = merge_data(total_data['restingHeartRate']['resting_heart_data_json'], processed_data['Items'], frequency)
    elif metric == "sleep":
        print("sleep")
        total_data['sleep']['sleep_data_json'] = merge_data(total_data['sleep']['sleep_data_json'], processed_data['Items'], frequency)
    elif metric == "activity":
        print("activity")
        # final = merge_data(total_data['activity']['activity_data_json'], processed_data['Items'], frequency)
        # print(final) #
        
    elif metric == "oxygen":
        print("oxygen")
        total_data['oxygen']['oxygen_data_json'] = merge_data(total_data['oxygen']['oxygen_data_json'], processed_data['Items'], frequency)
    else:
        print("Unknown metric")

@sync_to_async
def get_credentials(request):
    if "credentials" in request.session:
        credentials = Credentials(**request.session["credentials"])
        return credentials, request.user.username
    
    return None

@sync_to_async
def get_sleep_scores(total_data, email):
    sleep_body = ""
    for sleep_data in total_data["sleep"]["sleep_data_json"]:
        duration = sleep_data['count']
        user = User.objects.get(email=email)
        age=26
        activity_level=70
        given_date = datetime.datetime.strptime(sleep_data['start'], '%b %d, %I %p')
        nearest_hr = min(total_data['restingHeartRate']['resting_heart_data_json'], key=lambda x: abs(datetime.datetime.strptime(x['start'], '%b %d, %I %p') - given_date))
        heart_rate=nearest_hr['count']
        
        nearest_steps = min(total_data['steps']['steps_data_json'], key=lambda x: abs(datetime.datetime.strptime(x['start'], '%b %d, %I %p') - given_date))
        daily_steps=nearest_steps['count']
        
        gender_female=(user.sex == "female")
        gender_male=(user.sex == "male")
        
        sleep_body += f"{age},{duration},{activity_level},{heart_rate},{daily_steps},{gender_female},{gender_male},{True},{True},{False},{False},{False},{False}\n"
    
    if sleep_body and sleep_body[-1] == '\n':
        sleep_body = sleep_body[:-1]
        
    url = "https://2pfeath3sg.execute-api.us-east-1.amazonaws.com/dev/inference"
    
    response = requests.post(url, json=sleep_body)
    sleep_score = response.text.split(":")[1][:-1].strip()
    sleep_score = ast.literal_eval(sleep_score)
    
    for i, sleep_data in enumerate(total_data["sleep"]["sleep_data_json"]):
        sleep_data["count"] = sleep_score[i]
    
    return total_data

async def format_bod_fitness_data(total_data):
    list1 = total_data["glucose"]["glucose_data_json"]
    list2 = total_data["pressure"]["pressure_data_json"]
    
    def parse_date(date_str):
        return datetime.datetime.strptime(date_str, '%b %d, %I %p')

    # Extract all unique start dates from both lists
    all_dates = set()
    for item in list1 + list2:
        all_dates.add(item['start'])

    # Update list1
    for date in all_dates:
        found = False
        for item in list1:
            if item['start'] == date:
                found = True
                break
        if not found:
            list1.append({'start': date, 'end': date, 'count': 0})

    # Update list2
    for date in all_dates:
        found = False
        for item in list2:
            if item['start'] == date:
                found = True
                break
        if not found:
            list2.append({'start': date, 'end': date, 'count': 0})

    # Sort lists by start date
    list1.sort(key=lambda x: parse_date(x['start']))
    list2.sort(key=lambda x: parse_date(x['start']))
    
    total_data["glucose"]["glucose_data_json"] = list1
    total_data["pressure"]["pressure_data_json"] = list2
    
    return total_data

async def fetch_all_metric_data(request, duration, frequency):
    total_data = {}
    credentials, email = await get_credentials(request)
    if credentials:
        # try:
        service = build('fitness', 'v1', credentials=credentials)
        tasks = []
        for metric in dataTypes.keys():
            tasks.append(fetch_metric_data(service, metric, total_data, duration, frequency, email))
        
        await asyncio.gather(*tasks)
        total_data = await get_sleep_scores(total_data, email)
        total_data = await format_bod_fitness_data(total_data)
                 
        # except Exception as e:
        #     print(e)
        #     total_data = {}
    
    else:
        print("Not signed in Google")
    
    print("total data: ", total_data)
    return total_data
        

async def get_metric_data(request):
    
    duration = 'week'
    frequency = 'daily'
    
    if request.GET.get('data_drn'):
        duration = request.GET.get('data_drn')
    
    if request.GET.get('data_freq'):
        frequency = request.GET.get('data_freq')    
    
    total_data = await fetch_all_metric_data(request, duration, frequency)
    
    context = {'data': total_data}
    return render(request, 'metrics/display_metric_data.html', context)

def health_data_view(request):
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table('Django')
    default_email = request.user.username

    if request.method == 'POST':
        data = request.POST
        print(data)
        table.put_item(
            Item={
                'email': default_email,  # Use the default email
                'metric': data.get('metric'),
                'time': data.get('time'),
                'value': data.get('value')
            }
        )
        return redirect("metrics:get_metric_data")

    # Fetch all the metrics data from DynamoDB
    response = table.scan()
    metrics_data = {}
    for item in response['Items']:
        metric = item['metric']
        if metric not in metrics_data:
            metrics_data[metric] = []
        metrics_data[metric].append(item)

    for metric in metrics_data:
        metrics_data[metric].sort(key=lambda x: x['time'], reverse=True)

    return render(request, 'metrics/display_metric_data.html', {'metrics_data': metrics_data})

async def send_report(request):
    duration = 'week'
    frequency = 'hourly'    
    
    total_data = await fetch_all_metric_data(request, duration, frequency)
    _, email = await get_credentials(request)
    
    data = {
        "email": email
    }
    
    for metric in total_data:
        if metric == "steps":
            values = []
            for val in total_data["steps"]["steps_data_json"]:
                values.append({"Time": val["start"], "Average Steps": val["count"]})
            data["steps"] = values
        elif metric == "heartRate":
            values = []
            for val in total_data["heartRate"]["heart_data_json"]:
                values.append({"Time": val["start"], "Average Heartrate": val["count"]})
            data["heartrate"] = values
        elif metric == "restingHeartRate":
            values = []
            for val in total_data["restingHeartRate"]["resting_heart_data_json"]:
                values.append({"Time": val["start"], "Average Resting Heartrate": val["count"]})
            data["restingHeartRate"] = values
        elif metric == "sleep":
            values = []
            for val in total_data["sleep"]["sleep_data_json"]:
                values.append({"Time": val["start"], "Sleep Score": val["count"]})
            data["sleep"] = values
        elif metric == "oxygen":
            values = []
            for val in total_data["oxygen"]["oxygen_data_json"]:
                values.append({"Time": val["start"], "Average Oxygen Saturation": val["count"]})
            data["oxygen_saturation"] = values
        elif metric == "glucose":
            values = []
            for val in total_data["glucose"]["glucose_data_json"]:
                values.append({"Time": val["start"], "Average Blood Glucose": val["count"]})
            data["blood_glucose"] = values
        elif metric == "pressure":
            values = []
            for val in total_data["pressure"]["pressure_data_json"]:
                values.append({"Time": val["start"], "Average Blood Pressure": val["count"]})
            data["blood_pressure"] = values
        elif metric == "activity":
            values = []
            for val in total_data["activity"]["activity_data_json"]:
                values.append({"Activity": val[0], "Duration(Min)": val[1]})
            data["activities"] = values
    
    print(data)
    
    url = "https://2pfeath3sg.execute-api.us-east-1.amazonaws.com/dev/notification"
    response = requests.post(url, json=data)
    return JsonResponse({'message': 'Data received successfully'})