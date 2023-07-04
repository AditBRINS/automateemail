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
from tkinter import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def report_segker_1(id_log):
    try:
        log = Log.objects.get(pk = id_log)
    except  Exception as e:
        traceback.format_exc()

    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
    today = log.id_job.waktu_eksekusi
                
    if log.id_job.periode == 'harian':
        startdate = today - timedelta(1)
        enddate = today - timedelta(2)
    elif log.id_job.periode == 'bulanan':
            # temp_month
        if d == today:
            startdate = today + relativedelta(day=30)
        else: 
            startdate = today - timedelta(1)

        enddate = today + relativedelta(day=1)
    else:
        if ending_day_of_current_year == today:
            startdate = datetime.now().date().replace(month=12, day=30)
        else:
            startdate = today - timedelta(1)

        enddate = datetime.now().date().replace(month=1, day=1) 
    
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    trunct_month = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(c=Sum('Premi_Total')).values('month', 'c', 'branch').order_by('branch')
    sumTransaksi = transaksi.values('branch').order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    month_date = transaksi.annotate(month=TruncMonth('date')).values_list('month')
    template_data = tbl_template.objects.all()
    
    # ------------------------------------------------
    # Total produktivitas segmentasi kinerja
    # ------------------------------------------------
    # Segmentasi Kinerja
    segmentasi_kinerja = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('month', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch').order_by('branch')
    data = {
        'id' : log.id_job,
        'waktu' : log.id_job.waktu_eksekusi,
        'email_penerima' : log.id_job.email_penerima,
        'cabang' : log.id_job.kode_cabang,
        'running_id' :log.id_job.running_id,
        'trunct_month' :trunct_month,
        'month_date' : month_date,
        'detail_transaksi':transaksi,
        'today':today,
        'total_harga':sumTransaksi,
        'judul_format':log.id_job.periode,
        'startdate' : startdate,
        'enddate' : enddate,
        'template_data': template_data,
        'id_template':log.id_job.id_template,
        'segmentasi_kinerja' : segmentasi_kinerja,
    }

    pdf = render_to_pdf('report.html', data)
    return HttpResponse(pdf, content_type="application/pdf")

def report_segker_2(id_log):
    try:
        log = Log.objects.get(pk = id_log)
    except  Exception as e:
        traceback.format_exc()

    today = log.id_job.waktu_eksekusi
    startdate = today - timedelta(1)
    enddate = today + relativedelta(day=1)

    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    sumTransaksi = transaksi.values("branch").order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    # startdate = today - timedelta(1)

    # QueryTransaksi = tbl_produksi_segmentasi.objects.raw('SELECT * FROM detail_transaksi')
    # print(QueryTransaksi)
    
    data = {
        'id' : log.id_job,
        'waktu' : log.id_job.waktu_eksekusi,
        'email_penerima' : log.id_job.email_penerima,
        'cabang' : log.id_job.kode_cabang,
        'running_id' :log.id_job.running_id,
        'startdate' : startdate,
        'enddate' : enddate,
        # 'trunct_month' :trunct_month,
        # 'month_date' : month_date,
        'detail_transaksi':transaksi,
        'today':today,
        'total_harga':sumTransaksi,
    }
    pdf = render_to_pdf('report2.html', data)
    return HttpResponse(pdf, content_type="application/pdf")    

def report_b2b_1(id_log):
    try:
        log = Log.objects.get(pk = id_log)
    except  Exception as e:
        traceback.format_exc()

    today = log.id_job.waktu_eksekusi
    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
    today = log.id_job.waktu_eksekusi
            
    if log.id_job.periode == 'harian' or log.id_job.periode == 'Harian':
        startdate = today - timedelta(1)
        enddate = today - timedelta(2)
    elif log.id_job.periode == 'bulanan' or log.id_job.periode == 'Bulanan':
            # temp_month
        if d == today:
            startdate = today + relativedelta(day=30)
        else: 
            startdate = today - timedelta(1)

        enddate = today + relativedelta(day=1)
    else:
        if ending_day_of_current_year == today:
            startdate = datetime.now().date().replace(month=12, day=30)
        else:
            startdate = today - timedelta(1)

        enddate = datetime.now().date().replace(month=1, day=1) 
    print(startdate)
    print(enddate)
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    trunct_month = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(c=Sum('Premi_Total')).values('month', 'c', 'branch').order_by('branch')
    sumTransaksi = transaksi.values('branch').order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    month_date = transaksi.annotate(month=TruncMonth('date')).values_list('month')
    template_data = tbl_template.objects.all()
    
    # ------------------------------------------------
    # Total produktivitas segmentasi kinerja
    # ------------------------------------------------
    # Segmentasi Kinerja
    segmentasi_kinerja = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('month', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch').order_by('branch')

    data = {
        'id' : log.id_job,
        'waktu' : log.id_job.waktu_eksekusi,
        'email_penerima' : log.id_job.email_penerima,
        'cabang' : log.id_job.kode_cabang,
        'running_id' :log.running_id,
        'trunct_month' :trunct_month,
        'month_date' : month_date,
        'detail_transaksi':transaksi,
        'today':today,
        'total_harga':sumTransaksi,
        'judul_format':log.id_job.periode,
        'startdate' : startdate,
        'enddate' : enddate,
        'template_data': template_data,
        'id_template':log.id_job.id_template,
        'segmentasi_kinerja' : segmentasi_kinerja,
    }
    pdf = render_to_pdf('reportB2B.html', data)
    return HttpResponse(pdf, content_type="application/pdf")

def report_b2b_2(id_log):
    try:
        log = Log.objects.get(pk = id_log)
    except  Exception as e:
        traceback.format_exc()

    today = log.id_job.waktu_eksekusi
    startdate = today - timedelta(1)
    enddate = today + relativedelta(day=1)

    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    sumTransaksi = transaksi.values("branch").order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    # startdate = today - timedelta(1)

    # QueryTransaksi = tbl_produksi_segmentasi.objects.raw('SELECT * FROM detail_transaksi')
    # print(QueryTransaksi)
    
    data = {
        'id' : log.id_job,
        'waktu' : log.id_job.waktu_eksekusi,
        'email_penerima' : log.id_job.email_penerima,
        'cabang' : log.id_job.kode_cabang,
        'running_id' :log.running_id,
        'startdate' : startdate,
        'enddate' : enddate,
        # 'trunct_month' :trunct_month,
        # 'month_date' : month_date,
        'detail_transaksi':transaksi,
        'today':today,
        'total_harga':sumTransaksi,
    }
    pdf = render_to_pdf('report2.html', data)
    return HttpResponse(pdf, content_type="application/pdf")   