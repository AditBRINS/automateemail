from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from matplotlib.style import context
from ..models import Log, Shcedule, tbl_produksi_segmentasi, Log, tbl_template, tbl_cabang_report, tbl_captive_non_captive_report, tbl_sourcename, tbl_marketing_officer, captive_non_captive, tbl_brisurfnonbrisurf, tbl_os, tbl_target_seg, tbl_persentase_target, tbl_target_pusat, tbl_persentase_pusat, tbl_sum_segmentasi
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
from django.db.models.functions import TruncMonth, TruncYear, ExtractWeek
import xlwt
from datetime import date, datetime
from ..models import Shcedule
import pandas as pd
import matplotlib.pyplot as plt
from django.db.models import Q
from django.db.models import CharField, Case, Value, When
from django.db.models import When, F, Q
from django.db.models import FloatField, F

def schedule_100_200_1(id_job):
    # ----------------------------------------------------
    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
    # ----------------------------------------------------
    
    try:
        schedule = Shcedule.objects.get(pk = id_job)
    except  Exception as e:
        traceback.format_exc()
    
    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
    
    if schedule.periode == 'harian':
        startdate = today - timedelta(1)
        enddate = today - timedelta(1)
    elif schedule.periode == 'bulanan':
        # temp_month
        if d == today:
            startdate = date.today().replace(day=1) - timedelta(days=1)
        else: 
            startdate = date.today().replace(day=1) - timedelta(days=1)

        enddate = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
    else:
        if ending_day_of_current_year == today:
            startdate = datetime.now().date().replace(month=12, day=30)
        else:
            startdate = today - timedelta(1)

        enddate = datetime.now().date().replace(month=1, day=1) 

    cabang = Shcedule.objects.get(pk = id_job)
    template = get_template('report_100_200_rekap.html')
    
    # segmentasi kinerja 
    segmentasi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    sum_wholesale = list(segmentasi.aggregate(Sum('Premi_WHOLESALE')).values())[0] or 0
    sum_syariah = list(segmentasi.aggregate(Sum('Premi_SYARIAH')).values())[0] or 0
    sum_digital = list(segmentasi.aggregate(Sum('Premi_DIGITAL')).values())[0] or 0
    sum_ritel = list(segmentasi.aggregate(Sum('premi_ritel')).values())[0] or 0
    sum_mikro = list(segmentasi.aggregate(Sum('premi_mikro')).values())[0] or 0
    sum_ritel_mikro = list(segmentasi.aggregate(Sum('Premi_RITEL_MIKRO')).values())[0] or 0
    sum_premi_total = list(segmentasi.aggregate(Sum('Premi_Total')).values())[0] or 0
    
    # premi brisurf non brisurf
    brisurf = tbl_brisurfnonbrisurf.objects.filter(date__range=[enddate, startdate])
    brisurf_report = brisurf.values('kategori').order_by('kategori').annotate(total_premi=Sum('Premi')).values('BRANCH', 'branchName', 'kategori', 'total_premi')
    # sum premi brisurf  
    filter_brisurf = brisurf_report.filter(kategori = 'Brisurf')
    sum_brisurf = list(filter_brisurf.aggregate(Sum('total_premi')).values())[0] or 0
    # sum premi non brisurf
    filter_non_brisurf = brisurf_report.filter(kategori = 'Non Brisurf')
    sum_non_brisurf = list(filter_non_brisurf.aggregate(Sum('total_premi')).values())[0] or 0

    # sum premi captive non captive
    captive_report = captive_non_captive.objects.filter(date__range=[enddate, startdate])
    cnc_report = captive_report.values('captive_non_captive').order_by('captive_non_captive').annotate(total_premi=Sum('premi')).values('branch', 'branchName', 'captive_non_captive', 'total_premi')
    # sum captive pos bri
    filter_cnc_bri = cnc_report.filter(captive_non_captive = 'POS BRI')
    sum_cnc_bri = list(filter_cnc_bri.aggregate(Sum('total_premi')).values())[0] or 0
    # sum captive pos umum
    filter_cnc_umum = cnc_report.filter(captive_non_captive = 'POS UMUM')
    sum_cnc_umum = list(filter_cnc_umum.aggregate(Sum('total_premi')).values())[0] or 0

    # sum os
    os_report = tbl_os.objects.filter(as_at__range=[enddate, startdate])
    sum_os = list(os_report.aggregate(Sum('Nilai')).values())[0] or 0

    target = tbl_target_seg.objects.all()
    target_wholesale = target.filter(SEGMENT = 'WHOLESALE').values('BRANCH', 'BRANCHNAME', 'SEGMENT', 'TARGET')
    target_syariah = target.filter(SEGMENT = 'SYARIAH').values('BRANCH', 'BRANCHNAME', 'SEGMENT', 'TARGET')
    target_digital = target.filter(SEGMENT = 'DIGITAL').values('BRANCH', 'BRANCHNAME', 'SEGMENT', 'TARGET')
    target_ritel = target.filter(SEGMENT = 'RITEL').values('BRANCH', 'BRANCHNAME', 'SEGMENT', 'TARGET')
    target_mikro = target.filter(SEGMENT = 'MIKRO').values('BRANCH', 'BRANCHNAME', 'SEGMENT', 'TARGET')

    persentase = tbl_persentase_target.objects.all()

    target_pusat = tbl_target_pusat.objects.all()

    persentase_pusat = tbl_persentase_pusat.objects.all()

    data = {
        'id' : schedule.id_job,
        'waktu' : schedule.waktu_eksekusi,
        'email_penerima' : schedule.email_penerima,
        'cabang' : schedule.kode_cabang,
        'running_id' :schedule.running_id,
        'today':today,
        'judul_format':schedule.periode,
        'periodic' : schedule.periodic,
        'startdate' : startdate,
        'enddate' : enddate,
        'id_template':schedule.id_template,
        'sum_wholesale' : sum_wholesale,
        'sum_syariah' : sum_syariah, 
        'sum_digital' : sum_digital, 
        'sum_ritel' : sum_ritel, 
        'sum_mikro' : sum_mikro, 
        'sum_ritel_mikro' : sum_ritel_mikro, 
        'sum_premi_total' : sum_premi_total,
        'sum_brisurf' : sum_brisurf, 
        'sum_non_brisurf' : sum_non_brisurf,
        'sum_cnc_bri' : sum_cnc_bri, 
        'sum_cnc_umum' : sum_cnc_umum,
        'sum_os' : sum_os,
        'target_wholesale' : target_wholesale,
        'target_syariah' : target_syariah,
        'target_digital' : target_digital,
        'target_ritel' : target_ritel, 
        'target_mikro' : target_mikro,
        'persentase' : persentase, 
        'target_pusat' : target_pusat,
        'persentase_pusat' : persentase_pusat
    }
    
    html  = template.render(data)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    pdf = result.getvalue()
    filename = 'Report_' + str(data['id']) + '.pdf'

    subject_email = 'Laporan transaksi otomatis'
    message_email = 'Email ini dikirimkan otomatis oleh sistem'
    email_cabang = cabang.email_penerima

    msg = EmailMultiAlternatives(
        subject_email,
        message_email,
        settings.EMAIL_HOST_USER,
        [email_cabang],
    )
    # print(msg)
    msg.attach_alternative(message_email, "text/html"), 
    msg.attach(filename, pdf, 'application/pdf')

    msg.send()

def schedule_100_200_2(id_job):
    # ----------------------------------------------------
    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
    # ----------------------------------------------------
    
    try:
        schedule = Shcedule.objects.get(pk = id_job)
    except  Exception as e:
        traceback.format_exc()
    
    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)

    yearly = schedule.waktu_eksekusi

    if schedule.periode == 'harian':
        startdate = today - timedelta(1)
        enddate = today - timedelta(1)
    elif schedule.periode == 'mingguan':
        day = str(schedule.waktu_eksekusi)
        dt = datetime.strptime(day, '%Y-%m-%d')

        enddate = dt - timedelta(days=dt.weekday())
        startdate = enddate + timedelta(days=4)
    elif schedule.periode == 'bulanan':
        # temp_month
        if d == today:
            startdate = date.today().replace(day=1) - timedelta(days=1)
        else: 
            startdate = date.today().replace(day=1) - timedelta(days=1)

        enddate = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
    elif schedule.periode == 'tahunan_detail':
        # temp_month
        if ending_day_of_current_year == today:
            startdate = datetime.now().date().replace(month=12, day=30)
        else:
            startdate = today - timedelta(1)

        enddate = datetime.now().date().replace(month=1, day=1) 
    else:
        # if ending_day_of_current_year == today:
        #     startdate = datetime.now().date().replace(month=12, day=30)
        # else:
        #     startdate = today - timedelta(1)

        # enddate = datetime.now().date().replace(month=1, day=1) 
        if ending_day_of_current_year == today:
            startdate = yearly.replace(day=1) - timedelta(days=365)
            startdate = startdate.replace(month=12, day=31) 
        else:
            startdate = yearly.replace(day=1) - timedelta(days=365)
            startdate = startdate.replace(month=12, day=31) 

        enddate = yearly.replace(day=1) - timedelta(days=365)
        enddate = enddate.replace(month=1, day=1)  

    cabang = Shcedule.objects.get(pk = id_job)
    template = get_template('report_100_200.html')
    
    import pandas as pd

    # buat fungsi perhitunga total masing - masing nilai setiap cabang
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    
    segmentasi_kinerja = transaksi.values('branch').filter(branch__lt=200).annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
            mikro_captive=Sum(Case(When(captive_non_captive = 'POS BRI', then=F('premi_mikro')), output_field = FloatField(), default = 0))).annotate(
            mikro_non_captive=Sum(Case(When(captive_non_captive = 'POS UMUM', then=F('premi_mikro')), output_field = FloatField(), default = 0))).annotate(ritel_captive=Sum(Case(When(captive_non_captive='POS BRI', then=F('premi_ritel')), output_field=FloatField(), default=0))).annotate(
            ritel_non_captive=Sum(Case(When(captive_non_captive='POS UMUM', then=F('premi_ritel')), output_field=FloatField(), default=0))).annotate(
            digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('wholesale', 'mikro_captive', 
            'ritel_non_captive','ritel_captive', 'mikro_non_captive','digital', 'syariah', 'premi_total','branch', 'nama_cabang').order_by('-premi_total')
    
    segmentasi_kinerja_2 = transaksi.values('branch').filter(branch__gt=200).annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
            mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
            ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
            digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('wholesale', 'mikro', 
            'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'nama_cabang').order_by('-premi_total')
   
    # filter segmentasi selain syariah.
    # segmentasi_kinerja_str = transaksi.filter(branch__icontains=string)
    # print(segmentasi_kinerja_str)

    # total premi konvesional 
    sum_syariah_konv = list(segmentasi_kinerja.aggregate(Sum('syariah')).values())[0] or 0
    # total premi syariah
    sum_syariah_sya = list(segmentasi_kinerja_2.aggregate(Sum('syariah')).values())[0] or 0

    # perhitungan brisurf non brisurf
    brisurf = tbl_brisurfnonbrisurf.objects.filter(date__range=[enddate, startdate])
    brisurf_report = brisurf.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi')).values('BRANCH', 'branchName', 'total_premi')
   
    # total premi brisurf konvesioanl
    brisurf_konv = brisurf_report.values('BRANCH').filter(BRANCH__lt=200).annotate(total_premi=Sum('Premi')).values('BRANCH', 'branchName', 'total_premi')
    filter_brisurf_konv = brisurf_konv.filter(kategori = 'Brisurf')
    filter_non_brisurf_konv = brisurf_konv.filter(kategori = 'Non Brisurf')

    branch_brisurf = filter_brisurf_konv.values('BRANCH').annotate(premi_brisurf = Sum('Premi')).values('BRANCH', 'branchName', 'premi_brisurf')
    sum_brisurf = list(filter_brisurf_konv.aggregate(Sum('total_premi')).values())[0] or 0
    
    branch_non_brisurf = filter_non_brisurf_konv.values('BRANCH').annotate(premi_non_brisurf = Sum('Premi')).values('BRANCH', 'branchName', 'premi_non_brisurf')
    sum_non_brisurf = list(filter_non_brisurf_konv.aggregate(Sum('total_premi')).values())[0] or 0

    # total premi brisurf syariah
    brisurf_sya = brisurf_report.values('BRANCH').filter(BRANCH__gt=200).annotate(total_premi=Sum('Premi')).values('BRANCH', 'branchName', 'total_premi')
    filter_brisurf_sya = brisurf_sya.filter(kategori = 'Brisurf')
    filter_non_brisurf_sya = brisurf_sya.filter(kategori = 'Non Brisurf')

    branch_brisurf_sya = filter_brisurf_sya.values('BRANCH').annotate(premi_brisurf = Sum('Premi')).values('BRANCH', 'branchName', 'premi_brisurf')
    sum_brisurf_sya = list(filter_brisurf_sya.aggregate(Sum('total_premi')).values())[0] or 0
    
    branch_non_brisurf_sya = filter_non_brisurf_sya.values('BRANCH').annotate(premi_non_brisurf = Sum('Premi')).values('BRANCH', 'branchName', 'premi_non_brisurf')
    sum_non_brisurf_sya = list(filter_non_brisurf_sya.aggregate(Sum('total_premi')).values())[0] or 0

    # sum segmentasi 
    sum_segmentasi = tbl_sum_segmentasi.objects.all().filter(~Q(branch= 115))

    # total setiap premi. 
    sum_wholesale = list(sum_segmentasi.aggregate(Sum('wholesale')).values())[0] or 0
    sum_syariah = list(sum_segmentasi.aggregate(Sum('syariah')).values())[0] or 0
    sum_digital = list(sum_segmentasi.aggregate(Sum('digital')).values())[0] or 0
    sum_Retail_Pos_BRI = list(sum_segmentasi.aggregate(Sum('Retail_Pos_BRI')).values())[0] or 0
    sum_Retail_Pos_umum = list(sum_segmentasi.aggregate(Sum('Retail_Pos_umum')).values())[0] or 0
    sum_Mikro_Pos_BRI = list(sum_segmentasi.aggregate(Sum('Mikro_Pos_BRI')).values())[0] or 0
    sum_Mikro_Pos_umum = list(sum_segmentasi.aggregate(Sum('Mikro_Pos_umum')).values())[0] or 0

    # data target
    target = tbl_target_seg.objects.filter(Branch__lt=200).all()
    sum_target_wholesale = list(target.aggregate(Sum('Wholesale')).values())[0] or 0
    sum_target_syariah = list(target.aggregate(Sum('Syariah')).values())[0] or 0
    sum_target_digital = list(target.aggregate(Sum('Digital')).values())[0] or 0
    sum_target_Retail_Pos_BRI = list(target.aggregate(Sum('Retail_Pos_BRI')).values())[0] or 0
    sum_target_Retail_Pos_umum = list(target.aggregate(Sum('Retail_Pos_umum')).values())[0] or 0
    sum_target_Mikro_Pos_BRI = list(target.aggregate(Sum('Mikro_Pos_BRI')).values())[0] or 0
    sum_target_Mikro_Pos_umum = list(target.aggregate(Sum('Mikro_Pos_umum')).values())[0] or 0

    target_2 = tbl_target_seg.objects.filter(Branch__gt=200).all()
    sum_target_syariah_2 = list(target_2.aggregate(Sum('Syariah')).values())[0] or 0

    persentase = tbl_persentase_target.objects.all()

    # persentase total 
    persetase_wholesale = ((sum_wholesale / sum_target_wholesale) * (100))
    persentase_syariah = ((sum_syariah / sum_target_syariah) * (100))
    persentase_digital = ((sum_digital / sum_target_digital) * (100))
    persentase_ritel_pos_bri = ((sum_Retail_Pos_BRI / sum_target_Retail_Pos_BRI) * 100)
    persentase_ritel_pos_umum = ((sum_Retail_Pos_umum / sum_target_Retail_Pos_umum) * 100)
    persentase_mikro_pos_bri = ((sum_Mikro_Pos_BRI / sum_target_Mikro_Pos_BRI) * 100)
    persentase_mikro_pos_umum = ((sum_Mikro_Pos_umum / sum_target_Mikro_Pos_umum) * 100)

    persentase_syariah_2 = ((sum_syariah_sya / sum_target_syariah_2) * 100)

    sum_segmentasi_kinerja = transaksi.annotate(year = TruncYear('date')).filter(branch__lt=200).values('year').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
            mikro_captive=Sum(Case(When(captive_non_captive = 'POS BRI', then=F('premi_mikro')), output_field = FloatField(), default = 0))).annotate(
            mikro_non_captive=Sum(Case(When(captive_non_captive = 'POS UMUM', then=F('premi_mikro')), output_field = FloatField(), default = 0))).annotate(ritel_captive=Sum(Case(When(captive_non_captive='POS BRI', then=F('premi_ritel')), output_field=FloatField(), default=0))).annotate(
            ritel_non_captive=Sum(Case(When(captive_non_captive='POS UMUM', then=F('premi_ritel')), output_field=FloatField(), default=0))).annotate(
            digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('year','wholesale', 'mikro_captive', 
            'ritel_non_captive','ritel_captive', 'mikro_non_captive','digital', 'syariah', 'premi_total').order_by('-premi_total')
    print(sum_segmentasi_kinerja)
    sum_segmentasi_kinerja_2 = transaksi.annotate(year = TruncYear('date')).filter(branch__gt=200).values('year').annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('year', 'syariah', 'premi_total').order_by('-premi_total')

    sum_segmentasi_kinerja_3 = transaksi.annotate(year = TruncYear('date')).values('year').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
            mikro_captive=Sum(Case(When(captive_non_captive = 'POS BRI', then=F('premi_mikro')), output_field = FloatField(), default = 0))).annotate(
            mikro_non_captive=Sum(Case(When(captive_non_captive = 'POS UMUM', then=F('premi_mikro')), output_field = FloatField(), default = 0))).annotate(ritel_captive=Sum(Case(When(captive_non_captive='POS BRI', then=F('premi_ritel')), output_field=FloatField(), default=0))).annotate(
            ritel_non_captive=Sum(Case(When(captive_non_captive='POS UMUM', then=F('premi_ritel')), output_field=FloatField(), default=0))).annotate(
            digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('year','wholesale', 'mikro_captive', 
            'ritel_non_captive','ritel_captive', 'mikro_non_captive','digital', 'syariah', 'premi_total').order_by('-premi_total')

    data = {
        'id' : schedule.id_job,
        'waktu' : schedule.waktu_eksekusi,
        'email_penerima' : schedule.email_penerima,
        'cabang' : schedule.kode_cabang,
        'running_id' :schedule.running_id,
        'periodic' : schedule.periodic,
        'periode' : schedule.periode,
        'startdate' : startdate,
        'enddate' : enddate,
        'detail_transaksi':transaksi,
        'today':today,
        'segmentasi_kinerja' : segmentasi_kinerja,
        'segmentasi_kinerja_2' : segmentasi_kinerja_2,
        'sum_wholesale' : sum_wholesale,
        'sum_syariah' : sum_syariah, 
        'sum_digital' : sum_digital, 
        'sum_Retail_Pos_BRI' : sum_Retail_Pos_BRI,
        'sum_Retail_Pos_umum' : sum_Retail_Pos_umum, 
        'sum_Mikro_Pos_BRI' : sum_Mikro_Pos_BRI,
        'sum_Mikro_Pos_umum' : sum_Mikro_Pos_umum,
        'sum_syariah_konv' : sum_syariah_konv, 
        'sum_syariah_sya' : sum_syariah_sya, 
        'brisurf_report' : brisurf_report,
        'branch_brisurf' : branch_brisurf,
        'branch_non_brisurf' : branch_non_brisurf,  
        'sum_brisurf' : sum_brisurf, 
        'sum_non_brisurf' : sum_non_brisurf, 
        'brisurf_sya' : brisurf_sya,
        'branch_brisurf_sya' : branch_brisurf_sya,
        'branch_non_brisurf_sya' : branch_non_brisurf_sya,  
        'sum_brisurf_sya' : sum_brisurf_sya, 
        'sum_non_brisurf_sya' : sum_non_brisurf_sya, 
        'target' : target,
        'target_2' : target_2,
        'persentase' : persentase, 
        'sum_segmentasi' : sum_segmentasi, 
        'sum_target_wholesale' : sum_target_wholesale,
        'sum_target_syariah' : sum_target_syariah, 
        'sum_target_syariah_2' : sum_target_syariah_2,
        'sum_target_digital' : sum_target_digital, 
        'sum_target_Retail_Pos_BRI' : sum_target_Retail_Pos_BRI,
        'sum_target_Retail_Pos_umum' : sum_target_Retail_Pos_umum,
        'sum_target_Mikro_Pos_BRI' : sum_target_Mikro_Pos_BRI,
        'sum_target_Mikro_Pos_umum' : sum_target_Mikro_Pos_umum, 
        'persentase_wholesale' : persetase_wholesale,
        'persentase_digital' : persentase_digital, 
        'persentase_syariah' : persentase_syariah,
        'persentase_retail_pos_bri' : persentase_ritel_pos_bri,
        'persentase_ritel_pos_umum' : persentase_ritel_pos_umum, 
        'persentase_mikro_pos_umum' : persentase_mikro_pos_umum,
        'persentase_mikro_pos_bri' : persentase_mikro_pos_bri, 
        'persentase_syariah_2' : persentase_syariah_2, 
        'sum_segmentasi_kinerja' : sum_segmentasi_kinerja, 
        'sum_segmentasi_kinerja_2' : sum_segmentasi_kinerja_2,
        'sum_segmentasi_kinerja_3' : sum_segmentasi_kinerja_3
    }
    
    html  = template.render(data)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    pdf = result.getvalue()
    filename = 'Report_' + str(data['id']) + '.pdf'

    subject_email = 'Laporan transaksi otomatis'
    message_email = 'Email ini dikirimkan otomatis oleh sistem'
    email_cabang = cabang.email_penerima

    msg = EmailMultiAlternatives(
        subject_email,
        message_email,
        settings.EMAIL_HOST_USER,
        [email_cabang],
    )
    # print(msg)
    msg.attach_alternative(message_email, "text/html"), 
    msg.attach(filename, pdf, 'application/pdf')

    msg.send()
