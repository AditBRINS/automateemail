# Generated by Django 4.1.7 on 2023-02-22 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shceduleremail', '0018_tbl_captive_non_captive_report_tbl_marketing_officer_tbl_sourcename'),
    ]

    operations = [
        migrations.DeleteModel(
            name='KodeProduk',
        ),
        migrations.AlterModelTable(
            name='captive_non_captive',
            table='premi_capncap',
        ),
        migrations.AlterModelTable(
            name='log',
            table='Log',
        ),
        migrations.AlterModelTable(
            name='tbl_cabang',
            table='email_test',
        ),
        migrations.AlterModelTable(
            name='tbl_captive_non_captive_report',
            table='cnc_report',
        ),
        migrations.AlterModelTable(
            name='tbl_produksi_segmentasi',
            table='produksi_segmentasi',
        ),
    ]
