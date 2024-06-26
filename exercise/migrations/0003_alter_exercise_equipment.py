# Generated by Django 4.2.4 on 2024-04-02 21:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exercise", "0002_alter_exercise_category_alter_exercise_mechanic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exercise",
            name="equipment",
            field=models.CharField(
                choices=[
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
                    ("foam roll", "Foam Roll"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]
