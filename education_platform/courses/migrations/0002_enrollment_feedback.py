from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='feedback',
            field=models.TextField(blank=True, verbose_name='Фидбек преподавателя'),
        ),
    ]
