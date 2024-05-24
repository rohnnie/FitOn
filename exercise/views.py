from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from exercise.models import Exercise, MuscleGroup
import re
from django.core.serializers import serialize
import pymysql
import datetime
from user.models import User
from django.http import JsonResponse
import json
import requests

def store_exercises(request):
    post_data = json.loads(request.body)
    exercise_list = post_data['data_list']
    print("Exercises: ", exercise_list)
    connection = pymysql.connect(host="database-1.chu04k6u0syf.us-east-1.rds.amazonaws.com", user='admin', password='admin1234', database='exercises')
    user = User.objects.get(email=request.user.username)
    success = False
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO fitness_data (timestamp, user_id, Age, gender, height, weight, heartrate, steps, exercise_id) VALUES ("
            
            ts = datetime.datetime.now()
            # Iterate over the list of values and execute the query for each row
            for value in exercise_list:
                ts = ts - datetime.timedelta(seconds=1)
                time = ts.strftime('%Y-%m-%d %H:%M:%S.%f')
                temp_sql = str(sql)
                temp_sql += f'"{time}", '
                temp_sql += str(user.id)
                temp_sql += f", 26, "
                gender = 1 if user.sex == "male" else 0
                temp_sql += f"{gender}, "
                temp_sql += f"{user.height}, "
                temp_sql += f"{user.weight}, "
                temp_sql += f"75, "
                temp_sql += f"5000, "
                temp_sql += f"{value})"
                
                ret = cursor.execute(temp_sql)
            
            # Commit the transaction
            connection.commit()
            print("Insertion of exercises successful")
            success = True

    finally:
        # Close the connection
        connection.close()
    
    if success:
        return JsonResponse({'message': 'Data received successfully'})
    else:
        return JsonResponse({'error': 'Insertion failed'}, status=500)

def list_exercises(request):
    name = request.GET.get('exercise_name')
    level = request.GET.get('exercise_level')
    equipment = request.GET.get('exercise_equipment')
    muscle = request.GET.get('exercise_muscle')
    category = request.GET.get('exercise_category')
    
    user = User.objects.get(email=request.user.username)
    
    gender = 1 if (user.sex == "male") else 0
    body = f"26, {gender}, {user.height}, {user.weight}, 70, 5000"
    url = "https://2pfeath3sg.execute-api.us-east-1.amazonaws.com/dev/recommend"
    response = requests.post(url, json=body).text
    print(response)
    start_index = response.index('[')
    end_index = response.rindex(']')
    list_string = response[start_index:end_index + 1]
    inference_list = eval(list_string)[0]
    if(type(inference_list) == int):
        inference_list = [inference_list]
    inference_list = [max(50+i, i) for i in inference_list]
    
    selected_exercises = request.GET.getlist('exercise')
    exercises = Exercise.objects.all()

    if name:
        exercises = exercises.filter(name__icontains=name)
    if level and level != 'none':
        exercises = exercises.filter(level__icontains=level)
    if equipment and equipment != 'none':
        exercises = exercises.filter(equipment__icontains=equipment)
    if category and category != 'none':
        exercises = exercises.filter(category__icontains=category)
    if muscle and muscle != 'none':
        if MuscleGroup.objects.filter(name=muscle).exists():
            exercises = exercises.filter(primaryMuscles__name__icontains=muscle) | \
                    exercises.filter(secondaryMuscles__name__icontains=muscle)
    
    filter_dict = {
        "name": name if name else "",
        "level": level if level else "none",
        "equipment": equipment if equipment else "none",
        "category": category if category else "none",
        "muscle": muscle if muscle else "none"
    }
    
    page_number = request.GET.get('page', 1)  # Default to page 1 if not provided
    paginator = Paginator(exercises, 10)
    
    try:
        exercises = paginator.page(page_number)
    except PageNotAnInteger:
        exercises = paginator.page(1)
    except EmptyPage:
        exercises = paginator.page(paginator.num_pages)

    current_page_number = exercises.number
    page_range = paginator.page_range
    num_pages = paginator.num_pages
    
    image_urls = []
    for ex in exercises:
        name = re.sub(r"[^a-zA-Z0-9-(),']", '_', ex.name)
        url = {
            "url_0": f"https://fiton-exercise-images.s3.amazonaws.com/exercise_images/{name}_0.jpg",
            "url_1": f"https://fiton-exercise-images.s3.amazonaws.com/exercise_images/{name}_1.jpg"
        }
        image_urls.append(url)
    
    if selected_exercises and len(selected_exercises):
        selected_exercises = Exercise.objects.filter(id__in=selected_exercises)
    else:
        selected_exercises = []
    
    if inference_list and len(inference_list) == 4:
        recommended_exercises = Exercise.objects.filter(id__in=inference_list)
    else:
        recommended_exercises = []
    
    recommended_image_urls = []
    for ex in recommended_exercises:
        name = re.sub(r"[^a-zA-Z0-9-(),']", '_', ex.name)
        url = {
            "url_0": f"https://fiton-exercise-images.s3.amazonaws.com/exercise_images/{name}_0.jpg",
            "url_1": f"https://fiton-exercise-images.s3.amazonaws.com/exercise_images/{name}_1.jpg"
        }
        recommended_image_urls.append(url)
    
    print(recommended_exercises)

    return render(request, 'exercise/exercise_list.html', {'exercises': zip(exercises, image_urls), 'filter_dict': filter_dict, 'current_page_number': current_page_number, 'page_range': page_range, 'num_pages': num_pages, 'selected_exercises': selected_exercises, 'recommended_exercises': zip(recommended_exercises, recommended_image_urls)})