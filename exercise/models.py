from django.db import models

class Choices:
    force = [
        ("push", "Push"),
        ("pull", "Pull"),
        ("static", "Static")
    ]
    
    level = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert")
    ]
    
    mechanic = [
        ("compound", "Compound"),
        ("isolation", "Isolation"),
    ]
    
    equipment = [
        ("body only", "Body Only"),
        ("machine", "Machine"),
        ("kettlebells", "Kettlebells"),
        ("dumbbell", "Dumbbell"),
        ("cable", "Cable"),
        ("barbell", "Barbell"),
        ("bands", "Bands"),
        ("medicine ball", "Medicine Ball"),
        ("exercise ball", "Exercise Ball"),
        ("e-z curl bar", "E-Z Curl Bar"),
        ("foam roll", "Foam Roll")
    ]
    
    category = [
        ("strength", "Strength"),
        ("stretching", "Stretching"),
        ("plyometrics", "Plyometrics"),
        ("strongman", "Strongman"),
        ("powerlifting", "Powerlifting"),
        ("cardio", "Cardio"),
        ("olympic weightlifting", "Olympic Weightlifting"),
        ("crossfit", "Crossfit"),
        ("weighted bodyweight", "Weighted Bodyweight"),
        ("assisted bodyweight", "Assisted Bodyweight")
    ]

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    force = models.CharField(max_length=100, choices=Choices.force, null=True)
    level = models.CharField(max_length=100, choices=Choices.level)
    mechanic = models.CharField(max_length=100, choices=Choices.mechanic, null=True)
    equipment = models.CharField(max_length=100, choices=Choices.equipment, null=True)
    primaryMuscles = models.ManyToManyField(MuscleGroup, blank=True, related_name="primary_muscles")
    secondaryMuscles = models.ManyToManyField(MuscleGroup, blank=True, related_name="secondary_muscles")
    instructions = models.CharField(max_length=10000, blank=True, null=True)
    category = models.CharField(max_length=100, choices=Choices.category)   
    