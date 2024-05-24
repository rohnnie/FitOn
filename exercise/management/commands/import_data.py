import json
from django.core.management.base import BaseCommand
from exercise.models import Exercise, MuscleGroup

muscles = [
  "abdominals",
  "hamstrings",
  "calves",
  "shoulders",
  "adductors",
  "glutes",
  "quadriceps",
  "biceps",
  "forearms",
  "abductors",
  "triceps",
  "chest",
  "lower back",
  "traps",
  "middle back",
  "lats",
  "neck",
]

class Command(BaseCommand):
    help = 'Import data from JSON files'

    def handle(self, *args, **options):
        # Paths to your JSON files
        json_file = "D:\\Projects\\Cloud\\FitOn\\exercise-list.json"

        with open(json_file, 'r', encoding="utf8") as f:
            data = json.load(f)
            
            MuscleGroup.objects.all().delete()
            Exercise.objects.all().delete()
            
            for muscle in muscles:
                muscle_obj = MuscleGroup(
                    name=muscle
                )
                muscle_obj.save()

            # Process and save data to the database
            for item in data['exercises']:
                ex_obj = Exercise.objects.create(
                    name=item["name"],
                    force=item["force"],
                    level=item["level"],
                    mechanic=item["mechanic"],
                    equipment=item["equipment"],
                    instructions="\n".join(item["instructions"]),
                    category=item["category"]
                )
                
                for muscle in item["primaryMuscles"]:
                    ex_obj.primaryMuscles.add(MuscleGroup.objects.get(name=muscle))
                
                for muscle in item["secondaryMuscles"]:    
                    ex_obj.secondaryMuscles.add(MuscleGroup.objects.get(name=muscle))
                
                ex_obj.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
