from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_enrollment_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='contract_file',
            field=models.FileField(blank=True, null=True, upload_to='contracts/', verbose_name='Договор (DOCX)'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='decision_status',
            field=models.CharField(
                choices=[('pending', 'Ожидание'), ('accepted', 'Принято'), ('rejected', 'Отказано')],
                default='pending',
                max_length=20,
                verbose_name='Решение по заявке',
            ),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student_first_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Имя заказчика'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student_passport_issued_by',
            field=models.CharField(blank=True, max_length=255, verbose_name='Кем выдан паспорт заказчика'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student_passport_number',
            field=models.CharField(blank=True, max_length=10, verbose_name='Номер паспорта заказчика'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student_passport_series',
            field=models.CharField(blank=True, max_length=10, verbose_name='Серия паспорта заказчика'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student_patronymic',
            field=models.CharField(blank=True, max_length=100, verbose_name='Отчество заказчика'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student_surname',
            field=models.CharField(blank=True, max_length=100, verbose_name='Фамилия заказчика'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='contract_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Телефон для договора'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Имя'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Фамилия'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='passport_issued_by',
            field=models.CharField(blank=True, max_length=255, verbose_name='Кем выдан паспорт'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='passport_number',
            field=models.CharField(blank=True, max_length=10, verbose_name='Номер паспорта'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='passport_series',
            field=models.CharField(blank=True, max_length=10, verbose_name='Серия паспорта'),
        ),
        migrations.AddField(
            model_name='instructor',
            name='patronymic',
            field=models.CharField(blank=True, max_length=100, verbose_name='Отчество'),
        ),
    ]
