# Generated by Django 3.2.13 on 2023-03-24 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shceduleremail', '0022_tbl_target_seg'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_persentase_target',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('branch', models.CharField(max_length=3)),
                ('branch_name', models.CharField(max_length=50)),
                ('persentase_wholesale', models.FloatField()),
                ('persentase_ritel', models.FloatField()),
                ('persentase_mikro', models.FloatField()),
                ('persentase_syariah', models.FloatField()),
                ('persentase_digital', models.FloatField()),
            ],
            options={
                'db_table': 'persentase_segmen',
                'managed': False,
            },
        ),
    ]
