# Generated by Django 3.2.13 on 2023-03-08 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shceduleremail', '0020_tbl_brisurfnonbrisurf'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_os',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('as_date', models.DateField()),
                ('Branch_Supervisi', models.CharField(max_length=3)),
                ('Branch_Supervisi_name', models.CharField(max_length=50)),
                ('Nilai', models.FloatField()),
            ],
            options={
                'db_table': 'OS_Cabang',
                'managed': False,
            },
        ),
    ]
