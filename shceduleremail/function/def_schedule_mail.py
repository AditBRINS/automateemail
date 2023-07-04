from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from matplotlib.style import context
from ..models import Log, Shcedule, tbl_cabang, tbl_produksi_segmentasi, Log, Running, Login, tbl_template
from ..forms import FormShcedule, FormEmail, FormLogin, FormTemplate
from django.core.paginator import Paginator
from django.views.generic import View
from django.db.models import Sum
from ..utils import render_to_pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMultiAlternatives
from automateemail import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import *
from django.contrib.auth.hashers import check_password
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
import traceback 
from django.db.models.functions import TruncMonth
from django.db.models.functions import TruncMonth
import xlwt
from datetime import date, datetime
from ..models import Shcedule
from .def_send_mail import *
from .def_schedule_mail import *

def insert_scheduler(request):
    form = FormShcedule(request.POST)
    tomorrow = datetime.now()
    today = tomorrow.strftime("%Y-%m-%d")
    today2 = datetime.strptime(today, "%Y-%m-%d")
    template = tbl_template.objects.all()

    if request.method == 'POST':
        periodic = request.POST.get('periodic')
        running_id = Running.objects.values('running_id')
        if form.is_valid():
            if periodic == 'daily':
                # waktu_eksekusi = request.POST.get('waktu_eksekusi')
                jam_eksekusi = request.POST.get('jam_eksekusi')
                status = True if form.data.get('status') == "on" else False
                terakhir_eksekusi = request.POST.get('terakhir_eksekusi')
                template = request.POST.get('template')
                temp = tbl_template.objects.values('template').filter(pk = template) #temp -> merupakan nilai dari template yang akan digunakan diambil dari tb template
                periode = tbl_template.objects.values('periode').filter(pk = template) #periode -> merupakan periode laporan harian, bulanan atau tahunan yang akan diambil dari tb template
                id_template = tbl_template.objects.values('id_template').filter(pk = template) #id_template -> merupakan nilai id_template yang akan digunakan.
                # data_report = Template.objects.values('data_report').filter(pk = template)
                format_laporan = request.POST.get('format_template')
                # jenis_uker = request.POST.get('jenis_uker')
                # template = Template.objects.all()
                cabang = tbl_cabang.objects.all()
                for cabang in cabang : 
                    form = Shcedule(jam_eksekusi = jam_eksekusi, status = status, periodic = periodic, template = temp, terakhir_eksekusi = terakhir_eksekusi, 
                                    running_id = running_id, email_penerima = cabang.Email, kode_cabang = cabang.branch, waktu_eksekusi = today2, periode = periode, 
                                    id_template = id_template, format_laporan = format_laporan, jenis_uker = cabang.Jenis)
                    form.save()
                messages.success(request, 'Data berhasil ditambahkan' )
                obj = Running.objects.first()
                field_object = Running._meta.get_field('running_id')
                field_value = field_object.value_from_object(obj)
                field_value2 = field_value + 1
                print(field_value2)
                Running.objects.filter(idRunning = 1).update(running_id=field_value2) 
                # form2 = Running(running_id = field_value2)
            else : 
                waktu_eksekusi = request.POST.get('waktu_eksekusi')
                jam_eksekusi = request.POST.get('jam_eksekusi')
                status = True if form.data.get('status') == "on" else False
                terakhir_eksekusi = request.POST.get('terakhir_eksekusi')
                template = request.POST.get('template')
                temp = tbl_template.objects.values('template').filter(pk = template)
                periode = tbl_template.objects.values('periode').filter(pk = template)
                format_laporan = request.POST.get('format_template')
                jenis_uker = request.POST.get('jenis_uker')
                id_template = tbl_template.objects.values('id_template').filter(pk = template)
                cabang = tbl_cabang.objects.all()
                # data_report = Template.objects.values('data_report').filter(pk = template)
                for cabang in cabang : 
                    form = Shcedule(waktu_eksekusi = waktu_eksekusi, jam_eksekusi = jam_eksekusi, status = status, periodic = periodic, template=temp, 
                                    terakhir_eksekusi = terakhir_eksekusi, running_id = running_id, email_penerima = cabang.Email, kode_cabang = cabang.branch, 
                                    periode = periode, id_template = id_template, format_laporan = format_laporan, jenis_uker = cabang.Jenis)
                    form.save()
                messages.success(request, 'Data berhasil ditambahkan' )
                obj = Running.objects.first()
                field_object = Running._meta.get_field('running_id')
                field_value = field_object.value_from_object(obj)
                field_value2 = field_value + 1
                print(field_value2)
                Running.objects.filter(idRunning = 1).update(running_id=field_value2) 

    return HttpResponseRedirect('/dashboard')

def update_scheduler(request, running_id):
    schedule = Shcedule.objects.filter(running_id = running_id).first()
    if request.method == 'POST':
        periodic = request.POST.get('periodic')
        print(periodic)
        if periodic == 'daily':
            print('testing3')
            jam_eksekusi = request.POST.get('jam_eksekusi')
            status = True if request.POST.get('status') == 'on' else False
            waktu_eksekusi = request.POST.get('waktu_eksekusi')
            template = request.POST.get('template')
            periode = tbl_template.objects.values('periode').filter(pk = template)
            id_template = tbl_template.objects.values('id_template').filter(pk = template)
            format_laporan = request.POST.get('format_template')
            Shcedule.objects.filter(running_id = running_id).update( running_id=running_id, periodic = periodic, jam_eksekusi = jam_eksekusi, periode = periode, 
                                                                     status=status, waktu_eksekusi = waktu_eksekusi, format_laporan = format_laporan, id_template = id_template)
            messages.success(request, 'Data berhasil diperbarui' )
        else : 
            jam_eksekusi = request.POST.get('jam_eksekusi')
            status = True if request.POST.get('status') == 'on' else False
            waktu_eksekusi = request.POST.get('waktu_eksekusi')
            template = request.POST.get('template')
            periode = tbl_template.objects.values('periode').filter(pk = template)
            id_template = tbl_template.objects.values('id_template').filter(pk = template)
            format_laporan = request.POST.get('format_template')
            Shcedule.objects.filter(running_id = running_id).update( running_id=running_id, periodic = periodic, jam_eksekusi = jam_eksekusi, waktu_eksekusi = waktu_eksekusi, 
                                                                     periode = periode, status=status, format_laporan = format_laporan, id_template = id_template )
            messages.success(request, 'Data berhasil diperbarui' )

    return HttpResponseRedirect('/dashboard')