from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from matplotlib.style import context
from ..models import Log, Shcedule, tbl_produksi_segmentasi, Log, tbl_template, tbl_cabang_report, tbl_captive_non_captive_report, tbl_sourcename, tbl_marketing_officer, captive_non_captive, tbl_brisurfnonbrisurf, tbl_os, tbl_target_seg, tbl_persentase_target,tbl_target_pusat, tbl_persentase_pusat, persentase_mro, target_mro, tbl_klaim_cabang
from django.db.models import Sum
from ..utils import render_to_pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMultiAlternatives
from automateemail import settings
from django.contrib.auth.hashers import *
from django.contrib.auth.hashers import check_password
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
import traceback 
from django.db.models.functions import TruncMonth, TruncYear, ExtractWeek
import xlwt
from datetime import date, datetime
from ..models import Shcedule
from django.template.loader import render_to_string

def pdf_report_performance_branch_1(id_job):
    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

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
    
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    cabang = Shcedule.objects.get(pk = id_job)
    sumTransaksi = transaksi.values("branch").order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    trunct_month = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(c=Sum('Premi_Total')).values('month', 'c', 'branch').order_by('branch')
    month_date = transaksi.annotate(month=TruncMonth('date')).values_list('month')
    template_data = tbl_template.objects.all()
    
    template = get_template('report.html')

    # -------------------
    # Produksi Segmentasi 
    # -------------------  
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    trunct_month = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(c=Sum('Premi_Total')).values('month', 'c', 'branch').order_by('branch')
    sumTransaksi = transaksi.values('branch').order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    month_date = transaksi.annotate(month=TruncMonth('date')).values_list('month')
    template_data = tbl_template.objects.all()
    transaksi_test = transaksi.all()
    
    # grouping dan mentotalkan jumlah setiap minggu 
    # trunct_week = transaksi.annotate(week = ExtractWeek('date')).values('week').annotate(c=Sum('Premi_Total')).values('week', 'c', 'branch').order_by('branch')
    # print(trunct_week)

    # print(transaksi.date)
    transaksi_branch = transaksi.filter(branch=schedule.kode_cabang)
    # print(transaksi_branch)

    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    filter_seg_PBRI = transaksi.filter(captive_non_captive = 'POS BRI')
    filter_seg_PU = transaksi.filter(captive_non_captive = 'POS UMUM')

    sum_segker_mingguan_pbri = filter_seg_PBRI.annotate(year = TruncYear('date')).filter(kode_mro__lt=200).values('year').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('year', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    sum_segker_mingguan_pu = filter_seg_PU.annotate(year = TruncYear('date')).filter(kode_mro__lt=200).values('year').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('year', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    
    segmentasi_kinerja_mingguan = transaksi.annotate(week = ExtractWeek('date')).values('week').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('week', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch').order_by('branch')
    # print(segmentasi_kinerja_mingguan)
    # ------------------------------------------------
    # Total produktivitas segmentasi kinerja
    # ------------------------------------------------
    # Segmentasi Kinerja
    segmentasi_kinerja = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('month', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch').order_by('branch')

    segmentasi_tahunan = transaksi.annotate(year = TruncYear('date')).values('year').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('year', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'kode_mro').order_by('branch')
    
    # --------------------------
    # captive_non_captive
    # -------------------------
    # tbl_cabang
    cabang_report = tbl_cabang_report.objects.filter(Tanggal__range=[enddate, startdate]).order_by('Tanggal')
    sum_cabang_transaksi = cabang_report.values('kode_cabang').order_by('kode_cabang').annotate(total_premi = Sum('premi')).values('kode_cabang', 'total_premi', 'cabang_report')
    # tbl_captive_non_captive
    captive_report = captive_non_captive.objects.filter(date__range=[enddate, startdate])
    cnc_report = captive_report.values('captive_non_captive').order_by('captive_non_captive').annotate(total_premi=Sum('premi')).values('branch', 'branchName', 'captive_non_captive', 'total_premi')
    sum_segmentasi_cnc = captive_report.values('branch').order_by('branch').annotate(total_premi=Sum('premi'))
    
    # tabel brisurfnonbrisurf
    brisurf = tbl_brisurfnonbrisurf.objects.filter(date__range=[enddate, startdate])
    brisurf_report = brisurf.values('kategori').order_by('kategori').annotate(total_premi=Sum('Premi')).values('BRANCH', 'branchName', 'kategori', 'total_premi')
    sum_segmentasi_brisurf = brisurf_report.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi'))    
    # tbl_sourcename 
    sourcename = tbl_sourcename.objects.filter(tgl_produksi__range = [enddate, startdate])
    sourcename_report = sourcename.values('sumber_bisnis').order_by('sumber_bisnis').annotate(total_premi = Sum('premi')).values('kode_cabang', 'cabang', 'kode_sumber', 'sumber_bisnis', 'total_premi')
    sum_sourcename = sourcename.values('kode_cabang').order_by('kode_cabang').annotate(total_premi = Sum('premi'))
    template_data = tbl_template.objects.all()
    # tbl_marketing_officer
    marketing_officer = tbl_marketing_officer.objects.filter(Tanggal__range = [enddate, startdate]).order_by('Tanggal')
    mo_report = marketing_officer.values('nama_mo').order_by('nama_mo').annotate(total_premi = Sum('premi')).values('kode_cabang', 'cabang', 'nama_akun_mo', 'nama_mo', 'total_premi')
    sum_mo_report = marketing_officer.values('kode_cabang').order_by('kode_cabang').annotate(total_premi = Sum('premi'))
    # filter branch captive non captive
    cnc_branch = cnc_report.filter(branch = schedule.kode_cabang)
    df_report = pd.DataFrame(list(cnc_branch.all().values('branchName', 'captive_non_captive', 'total_premi')))
    # filter branch sumber sumber_bisnis
    sourcename_branch = sourcename_report.filter(kode_cabang = schedule.kode_cabang)
    
    # tbl OS - overdue
    os_report = tbl_os.objects.all().order_by('year')
    posisi_outstanding = os_report.values('as_at').order_by('-as_at').first()

    sum_os_premi = os_report.values('Branch').annotate(os_overdue = Sum('Outstanding_due')).annotate(os_overdue = Sum('Outstanding_due')).annotate(os_wpc = Sum('Outstanding_Undue')).annotate(os_overdue_brisurf_cp = Sum('OS_overdue_Brisurf_Captive')
    ).annotate(os_overdue_nonbrisur_cap = Sum('OS_overdue_Non_Brisurf_Captive')).annotate(os_overdue_noncap = Sum('OS_Overdue_NonCaptive')).annotate(os_wpc_brisurf_cap = Sum('OS_wpc_Brisurf_Captive')
    ).annotate(os_wpc_non_brisurf_cap = Sum('OS_wpc_Non_Brisurf_Captive')).annotate(os_wpc_noncap = Sum('OS_wpc_NonCaptive')).values('Branch_Supervisi_name', 'Branch_Name','os_overdue', 'Branch', 'os_wpc', 'os_overdue_brisurf_cp', 'os_overdue_nonbrisur_cap', 'os_overdue_noncap', 'os_wpc_brisurf_cap', 'os_wpc_non_brisurf_cap', 'os_wpc_noncap').order_by('Branch')

    # persentase target segmentasi
    target = tbl_target_seg.objects.all()
    persentase = tbl_persentase_target.objects.all()

    data = {
        'id' : schedule.id_job,
        'waktu' : schedule.waktu_eksekusi,
        'email_penerima' : schedule.email_penerima,
        'cabang' : schedule.kode_cabang,
        'running_id' :schedule.running_id,
        'jenis_uker' : schedule.jenis_uker,
        'periodic' : schedule.periodic,
        'trunct_month' :trunct_month,
        'month_date' : month_date,
        'detail_transaksi':transaksi,
        'today':today,
        'total_harga':sumTransaksi,
        'judul_format':schedule.periode,
        'startdate' : startdate,
        'enddate' : enddate,
        'template_data': template_data,
        'id_template':schedule.id_template,
        'segmentasi_kinerja' : segmentasi_kinerja,
        'segmentasi_kinerja_mingguan' : segmentasi_kinerja_mingguan,
        'segmentasi_tahuanan' : segmentasi_tahunan,             
        'cabang_report' : cabang_report,
        'sum_cabang_transaksi' : sum_cabang_transaksi,
        'cnc_report' : cnc_report,
        'sum_segmentasi_cnc' : sum_segmentasi_cnc,
        'sourcename_report' : sourcename_report, 
        'sum_sourcename' : sum_sourcename, 
        'mo_report' : mo_report, 
        'sum_mo_report' : sum_mo_report,
        'brisurf_report' : brisurf_report,
        'sum_segmentasi_brisurf' : sum_segmentasi_brisurf,
        'persentase' : persentase,
        'sum_segker_mingguan_pbri' : sum_segker_mingguan_pbri,
        'sum_segker_mingguan_pu' : sum_segker_mingguan_pu, 
        'os_report' : os_report, 
        'posisi_outstanding' : posisi_outstanding, 
        'sum_os_premi' : sum_os_premi, 
        'target' : target
    }


    # template msg email

    html  = template.render(data)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    pdf = result.getvalue()
    filename = 'Report_' + str(data['id']) + '.pdf'

    subject_email = 'Simulasi Otomasi Laporan'
    msg_email = render_to_string('template_msg_email.html')
    # message_email = msg_email,
    email_cabang = cabang.email_penerima

    msg = EmailMultiAlternatives(
        subject_email,
        msg_email,
        settings.EMAIL_HOST_USER,
        [email_cabang],
    )
    # print(msg)
    msg.attach_alternative(msg_email, "text/html"), 
    msg.attach(filename, pdf, 'application/pdf')

    msg.send()

def pdf_report_performance_branch_2(id_job):
    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

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
    
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    cabang = Shcedule.objects.get(pk = id_job)
    sumTransaksi = transaksi.values("branch").order_by("branch").annotate(total_harga = Sum('Premi_Total'))

    template = get_template('report_detail.html')

    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    transaksi_cabang = transaksi.values("branch").order_by("branch").annotate(total_premi = Sum('Premi_Total')).order_by('-total_premi')[0:9]

    # -------------------
    # Produksi Segmentasi 
    # -------------------  
    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    trunct_month = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(c=Sum('Premi_Total')).values('month', 'c', 'branch').order_by('branch')
    sumTransaksi = transaksi.values('branch').order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    month_date = transaksi.annotate(month=TruncMonth('date')).values_list('month')
    template_data = tbl_template.objects.all()
    transaksi_test = transaksi.all()
    
    # grouping dan mentotalkan jumlah setiap minggu 
    # trunct_week = transaksi.annotate(week = ExtractWeek('date')).values('week').annotate(c=Sum('Premi_Total')).values('week', 'c', 'branch').order_by('branch')
    # print(trunct_week)

    # print(transaksi.date)
    transaksi_branch = transaksi.filter(branch=schedule.kode_cabang)
    # print(transaksi_branch)

    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    filter_seg_PBRI = transaksi.filter(captive_non_captive = 'POS BRI')
    filter_seg_PU = transaksi.filter(captive_non_captive = 'POS UMUM')
    
    segker_mingguan = transaksi.values('date').filter(kode_mro__lt=200).annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('date', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    mro_detail_mingguan = segker_mingguan.values('branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro').distinct()
    
    segker_mingguan_2 = transaksi.values('date').filter(kode_mro__gt=200).annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('date', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    mro_detail_mingguan_2 = segker_mingguan_2.values('branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro').distinct()

    segker_harian_pbri = filter_seg_PBRI.values('date').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('date', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    segker_harian_pu = filter_seg_PU.values('date').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('date', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    segmentasi_kinerja_mingguan = transaksi.annotate(week = ExtractWeek('date')).filter(kode_mro__lt=200).values('week').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('week', 'wholesale',
                'digital', 'syariah','premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    total_segmentasi_kinerja_harian = transaksi.values('date').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('date', 'wholesale',
                'digital', 'syariah','premi_total','branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_harian_pbri = filter_seg_PBRI.values('date').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('date', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_harian_pu = filter_seg_PU.values('date').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('date', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')

    total_segmentasi_kinerja_mingguan =  transaksi.annotate(week = ExtractWeek('date')).values('week').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('week', 'wholesale',
                'digital', 'syariah','premi_total','branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_mingguan_pbri = filter_seg_PBRI.annotate(week = ExtractWeek('date')).values('week').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('week', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_mingguan_pu = filter_seg_PU.annotate(week = ExtractWeek('date')).values('week').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('week', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')

    total_segmentasi_kinerja_bulanan = transaksi.annotate(month = TruncMonth('date')).values('month').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('month', 'wholesale',
                'digital', 'syariah','premi_total','branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_bulanan_pbri = filter_seg_PBRI.annotate(month = TruncMonth('date')).values('month').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('month', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_bulanan_pu = filter_seg_PU.annotate(month = TruncMonth('date')).values('month').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('month', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')

    total_segker = transaksi.annotate(year = TruncYear('date')).values('year').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('year', 'wholesale',
                'digital', 'syariah','premi_total','branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_pbri = filter_seg_PBRI.annotate(year = TruncYear('date')).values('year').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('year', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')
    total_segker_pu = filter_seg_PU.annotate(year = TruncYear('date')).values('year').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('year', 'ritel', 'mikro', 'branch', 'nama_cabang').order_by('branch', 'nama_cabang')

    if schedule.periodic == 'monthly' :
        date_segker_mingguan = transaksi.filter(kode_mro__lt=200)
        startdate_mro = date_segker_mingguan.order_by('date')
        enddate_mro = date_segker_mingguan.order_by('-date')

        field_name_ros = 'date'    

        obj_weekly_mro_1 = startdate_mro.first()
        obj_weekly_mro_2 = enddate_mro.first()
        startdate_weekly_mro_1 = getattr(obj_weekly_mro_1, field_name_ros)
        enddate_weekly_mro_1 = getattr(obj_weekly_mro_2, field_name_ros)

        day_weekly_mro = str(startdate_weekly_mro_1)
        date_weekly_mro = datetime.strptime(day_weekly_mro, '%Y-%m-%d')
        
        startdate_weekly_mro = date_weekly_mro - timedelta(days=date_weekly_mro.weekday())
        enddate_weekly_mro = startdate_weekly_mro + timedelta(days=4)
        sum_week_mro = startdate_weekly_mro.isocalendar()[1]

        startdate_weekly_mro_2 = (enddate_weekly_mro + timedelta(days=7)) - timedelta(days=enddate_weekly_mro.weekday())
        enddate_weekly_mro_2 = startdate_weekly_mro_2 + timedelta(days=4)
        sum_week_mro_2 = startdate_weekly_mro_2.isocalendar()[1]

        startdate_weekly_mro_3 = (enddate_weekly_mro_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_mro_2.weekday())
        enddate_weekly_mro_3 = startdate_weekly_mro_3 + timedelta(days=4)
        sum_week_mro_3 = startdate_weekly_mro_3.isocalendar()[1]

        startdate_weekly_mro_4 = (enddate_weekly_mro_3 + timedelta(days=7)) - timedelta(enddate_weekly_mro_3.weekday())
        enddate_weekly_mro_4 = (startdate_weekly_mro_4 + timedelta(days=4))
        sum_week_mro_4 = startdate_weekly_mro_4.isocalendar()[1]

        startdate_weekly_mro_5 = (enddate_weekly_mro_4 + timedelta(days=7)) - timedelta(enddate_weekly_mro_4.weekday())
        enddate_weekly_mro_5 = enddate_weekly_mro_1
        sum_week_mro_5 = startdate_weekly_mro_5.isocalendar()[1]
    else:
        date_segker_mingguan =0
        startdate_mro = 0
        enddate_mro = 0

        field_name_ros = 0    

        obj_weekly_mro_1 = 0
        obj_weekly_mro_2 = 0
        startdate_weekly_mro_1 = 0
        enddate_weekly_mro_1 = 0

        day_weekly_mro = 0
        date_weekly_mro = 0
        
        startdate_weekly_mro = 0
        enddate_weekly_mro = 0
        sum_week_mro = 0

        startdate_weekly_mro_2 = 0
        enddate_weekly_mro_2 = 0
        sum_week_mro_2 = 0

        startdate_weekly_mro_3 = 0
        enddate_weekly_mro_3 = 0
        sum_week_mro_3 = 0

        startdate_weekly_mro_4 = 0
        enddate_weekly_mro_4 = 0
        sum_week_mro_4 = 0

        startdate_weekly_mro_5 = 0
        enddate_weekly_mro_5 = 0
        sum_week_mro_5 = 0

    segker_mingguan_pbri = filter_seg_PBRI.annotate(week = ExtractWeek('date')).filter(kode_mro__lt=200).values('week').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('week', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    segker_mingguan_pu = filter_seg_PU.annotate(week = ExtractWeek('date')).filter(kode_mro__lt=200).values('week').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('week', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    
    sum_segker_mingguan_pbri = filter_seg_PBRI.annotate(year = TruncYear('date')).filter(kode_mro__lt=200).values('year').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('year', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    sum_segker_mingguan_pu = filter_seg_PU.annotate(year = TruncYear('date')).filter(kode_mro__lt=200).values('year').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('year', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    
    mro_detail_bulanan = segmentasi_kinerja_mingguan.values('branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro').distinct()
    # print(mro_detail_bulanan)

    segmentasi_kinerja_mingguan_2 = transaksi.annotate(week = ExtractWeek('date')).filter(kode_mro__gt=200).values('week').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('week', 'wholesale',
                'digital', 'syariah', 'premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    
    mro_detail_bulanan_2 = segmentasi_kinerja_mingguan_2.values('branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro').distinct()

    if schedule.periodic == 'monthly' :
        date_segker_mingguan_2 = transaksi.filter(kode_mro__gt=200)
        startdate_ros = date_segker_mingguan_2.order_by('date')
        enddate_ros = date_segker_mingguan_2.order_by('-date')

        field_name_ros = 'date'    

        obj_weekly_ros_1 = startdate_ros.first()
        obj_weekly_ros_2 = enddate_ros.first()
        startdate_weekly_ros_1 = getattr(obj_weekly_ros_1, field_name_ros)
        enddate_weekly_ros_1 = getattr(obj_weekly_ros_2, field_name_ros)

        day_weekly_ros = str(startdate_weekly_ros_1)
        date_weekly_ros = datetime.strptime(day_weekly_ros, '%Y-%m-%d')
        
        startdate_weekly_ros = date_weekly_ros - timedelta(days=date_weekly_ros.weekday())
        enddate_weekly_ros = startdate_weekly_ros + timedelta(days=4)
        sum_week_ros = startdate_weekly_ros.isocalendar()[1]

        startdate_weekly_ros_2 = (enddate_weekly_ros + timedelta(days=7)) - timedelta(days=enddate_weekly_ros.weekday())
        enddate_weekly_ros_2 = startdate_weekly_ros_2 + timedelta(days=4)
        sum_week_ros_2 = startdate_weekly_ros_2.isocalendar()[1]

        startdate_weekly_ros_3 = (enddate_weekly_ros_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_ros_2.weekday())
        enddate_weekly_ros_3 = startdate_weekly_ros_3 + timedelta(days=4)
        sum_week_ros_3 = startdate_weekly_ros_3.isocalendar()[1]

        startdate_weekly_ros_4 = (enddate_weekly_ros_3 + timedelta(days=7)) - timedelta(enddate_weekly_ros_3.weekday())
        enddate_weekly_ros_4 = (startdate_weekly_ros_4 + timedelta(days=4))
        sum_week_ros_4 = startdate_weekly_ros_4.isocalendar()[1]

        startdate_weekly_ros_5 = (enddate_weekly_ros_4 + timedelta(days=7)) - timedelta(enddate_weekly_ros_4.weekday())
        enddate_weekly_ros_5 = enddate_weekly_ros_1
        sum_week_ros_5 = startdate_weekly_ros_5.isocalendar()[1]
    else:
        date_segker_mingguan_2 = 0
        startdate_ros = 0
        enddate_ros = 0

        field_name_ros = 0    

        obj_weekly_ros_1 = 0
        obj_weekly_ros_2 = 0
        startdate_weekly_ros_1 = 0
        enddate_weekly_ros_1 = 0

        day_weekly_ros = 0
        date_weekly_ros = 0
        
        startdate_weekly_ros = 0
        enddate_weekly_ros = 0
        sum_week_ros = 0

        startdate_weekly_ros_2 = 0
        enddate_weekly_ros_2 = 0
        sum_week_ros_2 = 0

        startdate_weekly_ros_3 = 0
        enddate_weekly_ros_3 = 0
        sum_week_ros_3 = 0

        startdate_weekly_ros_4 = 0
        enddate_weekly_ros_4 = 0
        sum_week_ros_4 = 0

        startdate_weekly_ros_5 = 0
        enddate_weekly_ros_5 = 0
        sum_week_ros_5 = 0

    # print(segmentasi_kinerja_mingguan)
    # ------------------------------------------------
    # Total produktivitas segmentasi kinerja
    # ------------------------------------------------
    # Segmentasi Kinerja
    segmentasi_kinerja = transaksi.annotate(month = TruncMonth('date')).values('month').filter(kode_mro__lt=200).annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('month', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    mro_detail = segmentasi_kinerja.values('branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro').distinct()
    
    segker_bulanan_pbri = filter_seg_PBRI.annotate(month = TruncMonth('date')).filter(kode_mro__lt=200).values('month').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('month', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro' ).order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')
    segker_bulanan_pu = filter_seg_PU.annotate(month = TruncMonth('date')).filter(kode_mro__lt=200).values('month').annotate(ritel =Sum('premi_ritel')).annotate(mikro = Sum('premi_mikro')).values('month', 'ritel', 'mikro', 'branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    segmentasi_kinerja_2 = transaksi.annotate(month = TruncMonth('date')).values('month').filter(kode_mro__gt=200).annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('month', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    mro_detail_2 = segmentasi_kinerja_2.values('branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro').distinct()


    segmentasi_tahunan = transaksi.annotate(year = TruncYear('date')).values('year').annotate(wholesale=Sum('Premi_WHOLESALE')).annotate(
                mikro=Sum('premi_mikro')).annotate(ritel=Sum('premi_ritel')).annotate(
                ritel_mikro=Sum('Premi_RITEL_MIKRO')).annotate(
                digital=Sum('Premi_DIGITAL')).annotate(syariah=Sum('Premi_SYARIAH')).annotate(premi_total=Sum('Premi_Total')).values('year', 'wholesale', 'mikro', 
                'ritel_mikro','ritel', 'digital', 'syariah', 'premi_total','branch', 'nama_cabang', 'kode_mro', 'nama_mro').order_by('branch', 'nama_cabang', 'kode_mro', 'nama_mro')

    # --------------------------
    # captive_non_captive
    # -------------------------
    # tbl_cabang
    cabang_report = tbl_cabang_report.objects.filter(Tanggal__range=[enddate, startdate]).order_by('Tanggal')
    sum_cabang_transaksi = cabang_report.values('kode_cabang').order_by('kode_cabang').annotate(total_premi = Sum('premi')).values('kode_cabang', 'total_premi', 'cabang_report')
    # tbl_captive_non_captive
    captive_report = captive_non_captive.objects.filter(date__range=[enddate, startdate])
    cnc_report = captive_report.values('captive_non_captive').order_by('captive_non_captive').annotate(total_premi=Sum('premi')).values('branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO')
    sum_segmentasi_cnc = captive_report.values('branch').order_by('branch').annotate(total_premi=Sum('premi'))
    # Melakukan filtering data.
    filter_cnc_PBRI = captive_report.filter(captive_non_captive = 'POS BRI')
    filter_cnc_PU = captive_report.filter(captive_non_captive = 'POS UMUM')
    # perhitungan captive non captive dapat dibagi menjadi tahunan, bulanan dan harian, 
    # perhitunagn cnc mingguan. 
    cnc_perhari_pbri = filter_cnc_PBRI.values('date').annotate(total_premi=Sum('premi')).values('date', 'branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO').order_by('date')
    cnc_perhari_pu = filter_cnc_PU.values('date').annotate(total_premi=Sum('premi')).values('date', 'branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO').order_by('date')
    
    # perhitungan cnc bulanan.
    cnc_mingguan_pbri = filter_cnc_PBRI.annotate(week = ExtractWeek('date')).values('week').annotate(total_premi=Sum('premi')).values('week', 'branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO').order_by('week')
    sum_cnc_mingguan_pbri = filter_cnc_PBRI.values('Kode_MRO').order_by('Kode_MRO').annotate(total_premi=Sum('premi'))
    cnc_mingguan_pu = filter_cnc_PU.annotate(week = ExtractWeek('date')).values('week').annotate(total_premi=Sum('premi')).values('week', 'branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO').order_by('week')
    sum_cnc_mingguan_pu = filter_cnc_PU.values('Kode_MRO').order_by('Kode_MRO').annotate(total_premi=Sum('premi'))
    
    if schedule.periodic == 'monthly' :
        startdate_captive = filter_cnc_PBRI.order_by('date')
        enddate_captive = filter_cnc_PBRI.order_by('-date')
        
        field_name = 'date'

        obj_weekly_captive_1 = startdate_captive.first()
        obj_weekly_captive_2 = enddate_captive.first()
        startdate_weekly_captive_1 = getattr(obj_weekly_captive_1, field_name)
        enddate_weekly_captive_1 = getattr(obj_weekly_captive_2, field_name)

        day_weekly_captive = str(startdate_weekly_captive_1)
        date_weekly_captive = datetime.strptime(day_weekly_captive, '%Y-%m-%d')
        
        startdate_weekly_captive = date_weekly_captive - timedelta(days=date_weekly_captive.weekday())
        enddate_weekly_captive = startdate_weekly_captive + timedelta(days=4)
        sum_week_captive = startdate_weekly_captive.isocalendar()[1]

        startdate_weekly_captive_2 = (enddate_weekly_captive + timedelta(days=7)) - timedelta(days=enddate_weekly_captive.weekday())
        enddate_weekly_captive_2 = startdate_weekly_captive_2 + timedelta(days=4)
        sum_week_captive_2 = startdate_weekly_captive_2.isocalendar()[1]

        startdate_weekly_captive_3 = (enddate_weekly_captive_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_captive_2.weekday())
        enddate_weekly_captive_3 = startdate_weekly_captive_3 + timedelta(days=4)
        sum_week_captive_3 = startdate_weekly_captive_3.isocalendar()[1]

        startdate_weekly_captive_4 = (enddate_weekly_captive_3 + timedelta(days=7)) - timedelta(enddate_weekly_captive_3.weekday())
        enddate_weekly_captive_4 = (startdate_weekly_captive_4 + timedelta(days=4))
        sum_week_captive_4 = startdate_weekly_captive_4.isocalendar()[1]

        startdate_weekly_captive_5 = (enddate_weekly_captive_4 + timedelta(days=7)) - timedelta(enddate_weekly_captive_4.weekday())
        enddate_weekly_captive_5 = enddate_weekly_captive_1
        sum_week_captive_5 = startdate_weekly_captive_5.isocalendar()[1]
        
        startdate_non_captive = filter_cnc_PU.order_by('date')
        enddate_non_captive = filter_cnc_PU.order_by('-date')

        obj_weekly_non_captive_1 = startdate_non_captive.first()
        obj_weekly_non_captive_2 = enddate_non_captive.first()
        startdate_weekly_non_captive_1 = getattr(obj_weekly_non_captive_1, field_name)
        enddate_weekly_non_captive_1 = getattr(obj_weekly_non_captive_2, field_name)


        day_weekly_non_captive = str(startdate_weekly_non_captive_1)
        date_weekly_non_captive = datetime.strptime(day_weekly_non_captive, '%Y-%m-%d')
        
        startdate_weekly_non_captive = date_weekly_non_captive - timedelta(days=date_weekly_non_captive.weekday())
        enddate_weekly_non_captive = startdate_weekly_non_captive + timedelta(days=4)
        sum_week_non_captive = startdate_weekly_non_captive.isocalendar()[1]

        startdate_weekly_non_captive_2 = (enddate_weekly_non_captive + timedelta(days=7)) - timedelta(days=enddate_weekly_non_captive.weekday())
        enddate_weekly_non_captive_2 = startdate_weekly_non_captive_2 + timedelta(days=4)
        sum_week_non_captive_2 = startdate_weekly_non_captive_2.isocalendar()[1]

        startdate_weekly_non_captive_3 = (enddate_weekly_non_captive_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_non_captive_2.weekday())
        enddate_weekly_non_captive_3 = startdate_weekly_non_captive_3 + timedelta(days=4)
        sum_week_non_captive_3 = startdate_weekly_non_captive_3.isocalendar()[1]

        startdate_weekly_non_captive_4 = (enddate_weekly_non_captive_3 + timedelta(days=7)) - timedelta(enddate_weekly_non_captive_3.weekday())
        enddate_weekly_non_captive_4 = (startdate_weekly_non_captive_4 + timedelta(days=4))
        sum_week_non_captive_4 = startdate_weekly_non_captive_4.isocalendar()[1]

        startdate_weekly_non_captive_5 = (enddate_weekly_non_captive_4 + timedelta(days=7)) - timedelta(enddate_weekly_non_captive_4.weekday())
        enddate_weekly_non_captive_5 = enddate_weekly_non_captive_1
        sum_week_non_captive_5 = startdate_weekly_non_captive_5.isocalendar()[1]
    else :
        startdate_captive = 0
        enddate_captive = 0
        
        field_name = 0

        obj_weekly_captive_1 = 0
        obj_weekly_captive_2 = 0
        startdate_weekly_captive_1 = 0
        enddate_weekly_captive_1 = 0

        day_weekly_captive = 0
        date_weekly_captive = 0
        
        startdate_weekly_captive = 0
        enddate_weekly_captive = 0
        sum_week_captive = 0

        startdate_weekly_captive_2 = 0
        enddate_weekly_captive_2 = 0
        sum_week_captive_2 = 0

        startdate_weekly_captive_3 = 0
        enddate_weekly_captive_3 = 0
        sum_week_captive_3 = 0

        startdate_weekly_captive_4 = 0
        enddate_weekly_captive_4 = 0
        sum_week_captive_4 = 0

        startdate_weekly_captive_5 = 0
        enddate_weekly_captive_5 = 0
        sum_week_captive_5 = 0
        
        startdate_non_captive = 0
        enddate_non_captive = 0

        obj_weekly_non_captive_1 = 0
        obj_weekly_non_captive_2 = 0
        startdate_weekly_non_captive_1 = 0
        enddate_weekly_non_captive_1 = 0


        day_weekly_non_captive = 0
        date_weekly_non_captive = 0
        
        startdate_weekly_non_captive = 0
        enddate_weekly_non_captive = 0
        sum_week_non_captive = 0

        startdate_weekly_non_captive_2 = 0
        enddate_weekly_non_captive_2 = 0
        sum_week_non_captive_2 = 0

        startdate_weekly_non_captive_3 = 0
        enddate_weekly_non_captive_3 = 0
        sum_week_non_captive_3 = 0

        startdate_weekly_non_captive_4 = 0
        enddate_weekly_non_captive_4 = 0
        sum_week_non_captive_4 = 0

        startdate_weekly_non_captive_5 = 0
        enddate_weekly_non_captive_5 = 0
        sum_week_non_captive_5 = 0

    # perhitungan cnc tahunan.
    cnc_tahunan_pbri = filter_cnc_PBRI.annotate(month = TruncMonth('date')).values('month').annotate(total_premi=Sum('premi')).values('month', 'branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO').order_by('month')
    sum_cnc_tahunan_pbri = filter_cnc_PBRI.values('Kode_MRO').order_by('Kode_MRO').annotate(total_premi=Sum('premi'))
    
    cnc_tahunan_pu = filter_cnc_PU.annotate(month = TruncMonth('date')).values('month').annotate(total_premi=Sum('premi')).values('month', 'branch', 'branchName', 'captive_non_captive', 'total_premi', 'Kode_MRO', 'Nama_MRO').order_by('month')
    sum_cnc_tahunan_pu = filter_cnc_PU.values('Kode_MRO').order_by('Kode_MRO').annotate(total_premi=Sum('premi'))
    # print(cnc_tahunan_pbri)

    # tabel brisurfnonbrisurf - unit kerja cabang
    brisurf = tbl_brisurfnonbrisurf.objects.filter(date__range=[enddate, startdate])
    brisurf_report = brisurf.values('kategori').order_by('kategori').annotate(total_premi=Sum('Premi')).values('BRANCH', 'branchName', 'kategori', 'total_premi', 'date')
    sum_segmentasi_brisurf = brisurf_report.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi'))
    # filtering table brisurf data mingguan.
    
    # Melakukan filtering data.
    filter_brisurf = brisurf.filter(kategori = 'Brisurf')
    filter_non_brisurf = brisurf.filter(kategori = 'Non Brisurf')
    # perhitungan brisurf non brisurf dapat dibagi menjadi tahunan, bulanan dan harian, 
    # perhitungan brisurf harian.
    brisurf_harian = filter_brisurf.values('date').annotate(total_premi=Sum('Premi')).values('date', 'BRANCH', 'branchName', 'kategori', 'total_premi').order_by('date')
    non_brisurf_harian = filter_non_brisurf.values('date').annotate(total_premi=Sum('Premi')).values('date', 'BRANCH', 'branchName', 'kategori', 'total_premi').order_by('date')
    # perhitungan brisurf mingguan.

    brisurf_mingguan = filter_brisurf.annotate(week = ExtractWeek('date')).values('week').annotate(total_premi=Sum('Premi')).values('week', 'BRANCH', 'branchName', 'kategori', 'total_premi').order_by('week')
    sum_brisurf_mingguan = filter_brisurf.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi'))

    if schedule.periodic == 'monthly' :
        startdate_brisurf = filter_brisurf.order_by('date')
        enddate_brisurf = filter_brisurf.order_by('-date')

        startdate_non_brisurf = filter_non_brisurf.order_by('date')
        enddate_non_brisurf = filter_non_brisurf.order_by('-date')
        
        field_name = 'date'

        obj_weekly_1 = startdate_brisurf.first()
        obj_weekly_2 = enddate_brisurf.first()
        startdate_weekly_1 = getattr(obj_weekly_1, field_name)
        enddate_weekly_1 = getattr(obj_weekly_2, field_name)

        day_weekly_bri = str(startdate_weekly_1)
        date_weekly_bri = datetime.strptime(day_weekly_bri, '%Y-%m-%d')
        
        startdate_weekly_brisurf = date_weekly_bri - timedelta(days=date_weekly_bri.weekday())
        enddate_weekly_brisurf = startdate_weekly_brisurf + timedelta(days=4)
        sum_week_brisurf = startdate_weekly_brisurf.isocalendar()[1]

        startdate_weekly_brisurf_2 = (enddate_weekly_brisurf + timedelta(days=7)) - timedelta(days=enddate_weekly_brisurf.weekday())
        enddate_weekly_brisrf_2 = startdate_weekly_brisurf_2 + timedelta(days=4)
        sum_week_brisurf_2 = startdate_weekly_brisurf_2.isocalendar()[1]

        startdate_weekly_brisurf_3 = (enddate_weekly_brisrf_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_brisrf_2.weekday())
        enddate_weekly_brisrf_3 = startdate_weekly_brisurf_3 + timedelta(days=4)
        sum_week_brisurf_3 = startdate_weekly_brisurf_3.isocalendar()[1]

        startdate_weekly_brisurf_4 = (enddate_weekly_brisrf_3 + timedelta(days=7)) - timedelta(enddate_weekly_brisrf_3.weekday())
        enddate_weekly_brisurf_4 = (startdate_weekly_brisurf_4 + timedelta(days=4))
        sum_week_brisurf_4 = startdate_weekly_brisurf_4.isocalendar()[1]

        startdate_weekly_brisurf_5 = (enddate_weekly_brisurf_4 + timedelta(days=7)) - timedelta(enddate_weekly_brisurf_4.weekday())
        enddate_weekly_brisurf_5 = (startdate_weekly_brisurf_5 + timedelta(days=4))
        sum_week_brisurf_5 = startdate_weekly_brisurf_5.isocalendar()[1]
            
        obj_weekly_non_brisurf_1 = startdate_non_brisurf.first()
        print(obj_weekly_non_brisurf_1)
        obj_weekly_non_brisurf_2 = enddate_non_brisurf.first()
        startdate_weekly_non_brisurf_1 = getattr(obj_weekly_non_brisurf_1, field_name)
        enddate_weekly_non_brisurf_1 = getattr(obj_weekly_non_brisurf_2, field_name)

        day_weekly_non_bri = str(startdate_weekly_non_brisurf_1)
        date_weekly_non_bri = datetime.strptime(day_weekly_non_bri, '%Y-%m-%d')
        
        startdate_weekly_non_brisurf = date_weekly_non_bri - timedelta(days=date_weekly_non_bri.weekday())
        enddate_weekly_non_brisurf = startdate_weekly_non_brisurf + timedelta(days=4)
        sum_week_non_brisurf = startdate_weekly_non_brisurf.isocalendar()[1]

        startdate_weekly_non_brisurf_2 = (enddate_weekly_non_brisurf + timedelta(days=7)) - timedelta(days=enddate_weekly_non_brisurf.weekday())
        enddate_weekly_non_brisrf_2 = startdate_weekly_non_brisurf_2 + timedelta(days=4)
        sum_week_non_brisurf_2 = startdate_weekly_non_brisurf_2.isocalendar()[1]

        startdate_weekly_non_brisurf_3 = (enddate_weekly_non_brisrf_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_non_brisrf_2.weekday())
        enddate_weekly_non_brisrf_3 = startdate_weekly_non_brisurf_3 + timedelta(days=4)
        sum_week_non_brisurf_3 = startdate_weekly_non_brisurf_3.isocalendar()[1]

        startdate_weekly_non_brisurf_4 = (enddate_weekly_non_brisrf_3 + timedelta(days=7)) - timedelta(enddate_weekly_non_brisrf_3.weekday())
        enddate_weekly_non_brisurf_4 = (startdate_weekly_non_brisurf_4 + timedelta(days=4))
        sum_week_non_brisurf_4 = startdate_weekly_non_brisurf_4.isocalendar()[1]

        startdate_weekly_non_brisurf_5 = (enddate_weekly_non_brisurf_4 + timedelta(days=7)) - timedelta(enddate_weekly_non_brisurf_4.weekday())
        enddate_weekly_non_brisurf_5 = (startdate_weekly_non_brisurf_5 + timedelta(days=4))
        sum_week_non_brisurf_5 = startdate_weekly_non_brisurf_5.isocalendar()[1]
    else:
        startdate_klaim = 0
        enddate_klaim = 0
        
        field_name = 0

        obj_weekly_1 = 0
        obj_weekly_2 = 0
        startdate_weekly_1 = 0
        enddate_weekly_1 = 0

        day_weekly_klaim = 0
        date_weekly_klaim = 0
        
        startdate_weekly_brisurf = 0
        enddate_weekly_brisurf = 0
        sum_week_brisurf = 0

        startdate_weekly_brisurf_2 = 0
        enddate_weekly_brisrf_2 = 0
        sum_week_brisurf_2 = 0

        startdate_weekly_brisurf_3 = 0
        enddate_weekly_brisrf_3 = 0
        sum_week_brisurf_3 = 0

        startdate_weekly_brisurf_4 = 0
        enddate_weekly_brisurf_4 = 0
        sum_week_brisurf_4 = 0

        startdate_weekly_brisurf_5 = 0
        enddate_weekly_brisurf_5 = 0
        sum_week_brisurf_5 = 0
            
        obj_weekly_non_brisurf_1 = 0
        obj_weekly_non_brisurf_2 = 0
        startdate_weekly_non_brisurf_1 = 0
        enddate_weekly_non_brisurf_1 = 0

        day_weekly_non_bri = 0
        date_weekly_non_bri = 0
        
        startdate_weekly_non_brisurf = 0
        enddate_weekly_non_brisurf = 0
        sum_week_non_brisurf = 0

        startdate_weekly_non_brisurf_2 = 0
        enddate_weekly_non_brisrf_2 = 0
        sum_week_non_brisurf_2 = 0

        startdate_weekly_non_brisurf_3 = 0
        enddate_weekly_non_brisrf_3 = 0
        sum_week_non_brisurf_3 = 0

        startdate_weekly_non_brisurf_4 = 0
        enddate_weekly_non_brisurf_4 = 0
        sum_week_non_brisurf_4 = 0

        startdate_weekly_non_brisurf_5 = 0
        enddate_weekly_non_brisurf_5 = 0
        sum_week_non_brisurf_5 = 0

    non_brisurf_mingguan = filter_non_brisurf.annotate(week = ExtractWeek('date')).values('week').annotate(total_premi=Sum('Premi')).values('week', 'BRANCH', 'branchName', 'kategori', 'total_premi').order_by('week')
    sum_non_brisurf_mingguan = filter_non_brisurf.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi'))

    # perhitungan brisurf bulanan
    brisurf_tahunan = filter_brisurf.annotate(month = TruncMonth('date')).values('month').annotate(total_premi=Sum('Premi')).values('month', 'BRANCH', 'branchName', 'kategori', 'total_premi').order_by('month')
    sum_brisurf_tahunan = filter_brisurf.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi'))

    non_brisurf_tahunan = filter_non_brisurf.annotate(month = TruncMonth('date')).values('month').annotate(total_premi=Sum('Premi')).values('month', 'BRANCH', 'branchName', 'kategori', 'total_premi').order_by('month')
    sum_non_brisurf_tahunan = filter_non_brisurf.values('BRANCH').order_by('BRANCH').annotate(total_premi=Sum('Premi'))

    # tbl_sourcename 
    sourcename = tbl_sourcename.objects.filter(tgl_produksi__range = [enddate, startdate])
    sourcename_report = sourcename.values('sumber_bisnis').order_by('sumber_bisnis').annotate(total_premi = Sum('premi')).values('kode_cabang', 'cabang', 'kode_sumber', 'sumber_bisnis', 'total_premi')
    sum_sourcename = sourcename.values('kode_cabang').order_by('kode_cabang').annotate(total_premi = Sum('premi'))
    template_data = tbl_template.objects.all()
    # tbl_marketing_officer
    marketing_officer = tbl_marketing_officer.objects.filter(Tanggal__range = [enddate, startdate]).order_by('Tanggal')
    mo_report = marketing_officer.values('nama_mo').order_by('nama_mo').annotate(total_premi = Sum('premi')).values('kode_cabang', 'cabang', 'nama_akun_mo', 'nama_mo', 'total_premi')
    sum_mo_report = marketing_officer.values('kode_cabang').order_by('kode_cabang').annotate(total_premi = Sum('premi'))
    
    # filter branch captive non captivef
    cnc_branch = cnc_report.filter(branch = schedule.kode_cabang)
    df_report = pd.DataFrame(list(cnc_branch.all().values('branchName', 'captive_non_captive', 'total_premi')))
    
    # filter branch sumber sumber_bisnis
    sourcename_branch = sourcename_report.filter(kode_cabang = schedule.kode_cabang)
    df_report = pd.DataFrame(list(sourcename_branch.all().values('kode_cabang', 'cabang', 'kode_sumber', 'sumber_bisnis', 'total_premi')))

    # tbl OS
    os = tbl_os.objects.all()
    os_report = os.values('year').annotate(os_overdue = Sum('Outstanding_due')).annotate(os_overdue = Sum('Outstanding_due')).annotate(os_wpc = Sum('Outstanding_Undue')).annotate(os_overdue_brisurf_cp = Sum('OS_overdue_Brisurf_Captive')
    ).annotate(os_overdue_nonbrisur_cap = Sum('OS_overdue_Non_Brisurf_Captive')).annotate(os_overdue_noncap = Sum('OS_Overdue_NonCaptive')).annotate(os_wpc_brisurf_cap = Sum('OS_wpc_Brisurf_Captive')
    ).annotate(os_wpc_non_brisurf_cap = Sum('OS_wpc_Non_Brisurf_Captive')).annotate(os_wpc_noncap = Sum('OS_wpc_NonCaptive')).values('year', 'Branch_Supervisi_name', 'Branch_Name','os_overdue', 'Branch', 'os_wpc', 'os_overdue_brisurf_cp', 'os_overdue_nonbrisur_cap', 'os_overdue_noncap', 'os_wpc_brisurf_cap', 'os_wpc_non_brisurf_cap', 'os_wpc_noncap').order_by('year')

    posisi_outstanding = os.values('as_at').order_by('-as_at').first()
    
    # total O/S Premi
    # os_perhari = os_report.values('ProductionDate').annotate(os_overdue = Sum('Outstanding_due')).annotate(os = Sum('Outstanding')).values('ProductionDate', 'Branch_Supervisi', 'Branch_Supervisi_name', 'os_overdue', 'os', 'Branch').order_by('ProductionDate')
    # os_premi_mingguan= os_report.annotate(week = ExtractWeek('ProductionDate')).values('week').annotate(os_overdue = Sum('Outstanding_due')).annotate(os = Sum('Outstanding')).values('week', 'Branch_Supervisi', 'Branch_Supervisi_name', 'os_overdue', 'os', 'Branch').order_by('week')
    # os_premi_bulanan =os_report.annotate(month = TruncMonth('ProductionDate')).values('month').annotate(os = Sum('Outstanding')).values('month', 'Branch_Supervisi', 'Branch_Supervisi_name', 'os', 'Branch').order_by('month')

    sum_os_premi = os_report.values('Branch').annotate(os_overdue = Sum('Outstanding_due')).annotate(os_overdue = Sum('Outstanding_due')).annotate(os_wpc = Sum('Outstanding_Undue')).annotate(os_overdue_brisurf_cp = Sum('OS_overdue_Brisurf_Captive')
    ).annotate(os_overdue_nonbrisur_cap = Sum('OS_overdue_Non_Brisurf_Captive')).annotate(os_overdue_noncap = Sum('OS_Overdue_NonCaptive')).annotate(os_wpc_brisurf_cap = Sum('OS_wpc_Brisurf_Captive')
    ).annotate(os_wpc_non_brisurf_cap = Sum('OS_wpc_Non_Brisurf_Captive')).annotate(os_wpc_noncap = Sum('OS_wpc_NonCaptive')).values('Branch_Supervisi_name', 'Branch_Name','os_overdue', 'Branch', 'os_wpc', 'os_overdue_brisurf_cp', 'os_overdue_nonbrisur_cap', 'os_overdue_noncap', 'os_wpc_brisurf_cap', 'os_wpc_non_brisurf_cap', 'os_wpc_noncap').order_by('Branch')

    # total nilai klaim
    klaim_cabang = tbl_klaim_cabang.objects.filter(Tanggal__range = [enddate, startdate])
    # klaim per-segmentasi harian, mingguan, bulanan dan tahunan. 
    klaim_cabang_perminggu = klaim_cabang.annotate(week = ExtractWeek('Tanggal')).values('week').annotate(Nilai_Klaim=Sum('Nilai')).values('week', 'Nilai_Klaim', 'Branch', 'NamaBranch').order_by('week')
    print(klaim_cabang_perminggu)
    klaim_cabang_perbulan = klaim_cabang.annotate(month = TruncMonth('Tanggal')).values('month').annotate(Nilai_Klaim=Sum('Nilai')).values('month', 'Nilai_Klaim', 'Branch', 'NamaBranch').order_by('month')
    klaim_cabang_total = klaim_cabang.annotate(month_as_at = TruncYear('Tanggal')).values('month_as_at').annotate(Nilai_Klaim=Sum('Nilai')).values('month_as_at', 'Nilai_Klaim', 'Branch', 'NamaBranch').order_by('month_as_at')
    
    if schedule.periodic == 'monthly' :
        startdate_klaim_cabang = klaim_cabang.order_by('Tanggal')
        enddate_klaim_cabang = klaim_cabang.order_by('-Tanggal')
        
        field_name = 'Tanggal'

        obj_weekly_klaim_1 = startdate_klaim_cabang.first()
        obj_weekly_klaim_2 = enddate_klaim_cabang.first()
        startdate_weekly_klaim_1 = getattr(obj_weekly_klaim_1, field_name)
        enddate_weekly_klaim_1 = getattr(obj_weekly_klaim_2, field_name)

        day_weekly_klaim = str(startdate_weekly_klaim_1)
        date_weekly_klaim = datetime.strptime(day_weekly_klaim, '%Y-%m-%d')
        
        startdate_weekly_klaim = date_weekly_klaim - timedelta(days=date_weekly_klaim.weekday())
        enddate_weekly_klaim = startdate_weekly_klaim + timedelta(days=4)
        sum_week_klaim = startdate_weekly_klaim.isocalendar()[1]

        startdate_weekly_klaim_2 = (enddate_weekly_klaim + timedelta(days=7)) - timedelta(days=enddate_weekly_klaim.weekday())
        enddate_weekly_klaim_2 = startdate_weekly_klaim_2 + timedelta(days=4)
        sum_week_klaim_2 = startdate_weekly_klaim_2.isocalendar()[1]

        startdate_weekly_klaim_3 = (enddate_weekly_klaim_2 + timedelta(days=7)) - timedelta(days=enddate_weekly_klaim_2.weekday())
        enddate_weekly_klaim_3 = startdate_weekly_klaim_3 + timedelta(days=4)
        sum_week_klaim_3 = startdate_weekly_klaim_3.isocalendar()[1]

        startdate_weekly_klaim_4 = (enddate_weekly_klaim_3 + timedelta(days=7)) - timedelta(enddate_weekly_klaim_3.weekday())
        enddate_weekly_klaim_4 = (startdate_weekly_klaim_4 + timedelta(days=4))
        sum_week_klaim_4 = startdate_weekly_klaim_4.isocalendar()[1]

        startdate_weekly_klaim_5 = (enddate_weekly_klaim_4 + timedelta(days=7)) - timedelta(enddate_weekly_klaim_4.weekday())
        enddate_weekly_klaim_5 = enddate_weekly_klaim_1
        sum_week_klaim_5 = startdate_weekly_klaim_5.isocalendar()[1]
    else :
        startdate_captive = 0
        enddate_captive = 0
        
        field_name = 0

        obj_weekly_captive_1 = 0
        obj_weekly_captive_2 = 0
        startdate_weekly_captive_1 = 0
        enddate_weekly_captive_1 = 0

        day_weekly_captive = 0
        date_weekly_captive = 0
        
        startdate_weekly_klaim = 0
        enddate_weekly_klaim = 0
        sum_week_klaim = 0

        startdate_weekly_klaim_2 = 0
        enddate_weekly_klaim_2 = 0
        sum_week_klaim_2 = 0

        startdate_weekly_klaim_3 = 0
        enddate_weekly_klaim_3 = 0
        sum_week_klaim_3 = 0

        startdate_weekly_klaim_4 = 0
        enddate_weekly_klaim_4 = 0
        sum_week_klaim_4 = 0

        startdate_weekly_klaim_5 = 0
        enddate_weekly_klaim_5 = 0
        sum_week_klaim_5 = 0
        
    target = tbl_target_seg.objects.all()
    persentase = tbl_persentase_target.objects.all()

    target_per_mro = target_mro.objects.all()
    persentase_target_mro = persentase_mro.objects.all()

    nama_cabang_mro = transaksi.order_by().values('kode_mro', 'nama_cabang').distinct()

    data = {
        'id' : schedule.id_job,
        'waktu' : schedule.waktu_eksekusi,
        'email_penerima' : schedule.email_penerima,
        'segker_mingguan' : segker_mingguan,
        'cabang' : schedule.kode_cabang,
        'segker_mingguan_2' : segker_mingguan_2,
        'mro_detail_mingguan': mro_detail_mingguan,
        'mro_detail_mingguan_2': mro_detail_mingguan_2,
        'running_id' :schedule.running_id,
        'jenis_uker' : schedule.jenis_uker,
        'periodic' : schedule.periodic,
        'trunct_month' :trunct_month,
        'month_date' : month_date,
        'detail_transaksi':transaksi,
        'today':today,
        'total_harga':sumTransaksi,
        'judul_format':schedule.periode,
        'startdate' : startdate,
        'enddate' : enddate,
        'template_data': template_data,
        'id_template':schedule.id_template,
        'segmentasi_kinerja' : segmentasi_kinerja,
        'segmentasi_kinerja_mingguan' : segmentasi_kinerja_mingguan,
        'segmentasi_kinerja_mingguan_2' : segmentasi_kinerja_mingguan_2,
        'segmentasi_tahuanan' : segmentasi_tahunan,   
        'total_segmentasi_kinerja_harian' : total_segmentasi_kinerja_harian,
        'total_segker_harian_pbri' : total_segker_harian_pbri, 
        'total_segker_harian_pu' : total_segker_harian_pu,          
        'total_segmentasi_kinerja_mingguan' : total_segmentasi_kinerja_mingguan,
        'total_segker_mingguan_pbri' : total_segker_mingguan_pbri, 
        'total_segker_mingguan_pu' : total_segker_mingguan_pu,
        'total_segmentasi_kinerja_bulanan' : total_segmentasi_kinerja_bulanan,
        'total_segker_bulanan_pbri' : total_segker_bulanan_pbri, 
        'total_segker_bulanan_pu' : total_segker_bulanan_pu,
        'total_segker' : total_segker,
        'total_segker_pbri' : total_segker_pbri, 
        'total_segker_pu' : total_segker_pu,
        'cabang_report' : cabang_report,
        'sum_cabang_transaksi' : sum_cabang_transaksi,
        'cnc_report' : cnc_report,
        'sum_segmentasi_cnc' : sum_segmentasi_cnc,
        'sourcename_report' : sourcename_report, 
        'sum_sourcename' : sum_sourcename, 
        'mo_report' : mo_report, 
        'sum_mo_report' : sum_mo_report,
        'sum_os_premi' : sum_os_premi,
        'brisurf_report' : brisurf_report,
        'sum_segmentasi_brisurf' : sum_segmentasi_brisurf,
        'os' : os,
        'os_report' : os_report,
        # 'os_report_mingguan_brisurf' : os_report_mingguan_brisurf,
        # 'os_report_bulanan' : os_report_bulanan,
        'brisurf_harian' : brisurf_harian,
        'non_brisurf_harian' : non_brisurf_harian,
        'brisurf_mingguan' : brisurf_mingguan,
        'non_brisurf_mingguan' : non_brisurf_mingguan,
        'sum_brisurf_mingguan' : sum_brisurf_mingguan,
        'sum_non_brisurf_mingguan' : sum_non_brisurf_mingguan,
        'cnc_perhari_pbri' : cnc_perhari_pbri, 
        'cnc_perhari_pu' : cnc_perhari_pu,
        'cnc_mingguan_pbri' : cnc_mingguan_pbri,
        'cnc_mingguan_pu' : cnc_mingguan_pu,
        'sum_cnc_mingguan_pbri' : sum_cnc_mingguan_pbri, 
        'sum_cnc_mingguan_pu' : sum_cnc_mingguan_pu,
        'brisurf_tahunan' : brisurf_tahunan,
        'non_brisurf_tahunan' : non_brisurf_tahunan,
        'sum_brisurf_tahunan' : sum_brisurf_tahunan,
        'sum_non_brisurf_tahunan' : sum_non_brisurf_tahunan,
        'cnc_tahunan_pbri' : cnc_tahunan_pbri,
        'cnc_tahunan_pu' : cnc_tahunan_pu,
        'sum_cnc_tahunan_pbri' : sum_cnc_tahunan_pbri, 
        'sum_cnc_tahunan_pu' : sum_cnc_tahunan_pu,
        'persentase' : persentase,
        'mro_detail' : mro_detail, 
        'segmentasi_kinerja_2' : segmentasi_kinerja_2,
        'mro_detail_2' : mro_detail_2, 
        'mro_detail_bulanan' : mro_detail_bulanan, 
        'mro_detail_bulanan_2' : mro_detail_bulanan_2, 
        'target' : target,
        'persentase' : persentase,
        'segker_mingguan_pbri' : segker_mingguan_pbri, 
        'segker_mingguan_pu' : segker_mingguan_pu,
        'klaim_cabang' : klaim_cabang,
        'klaim_cabang_perminggu' : klaim_cabang_perminggu, 
        'klaim_cabang_perbulan' : klaim_cabang_perbulan,
        'klaim_cabang_total' :klaim_cabang_total,
        'sum_segker_mingguan_pbri' : sum_segker_mingguan_pbri,
        'sum_segker_mingguan_pu' : sum_segker_mingguan_pu,
        'segker_bulanan_pbri' : segker_bulanan_pbri, 
        'segker_bulanan_pu' : segker_bulanan_pu,
        'segker_harian_pbri' : segker_harian_pbri,
        'segker_harian_pu' : segker_harian_pu,
        'target_per_mro' : target_per_mro,
        'persentase_target_mro' : persentase_target_mro,
        'nama_cabang_mro' : nama_cabang_mro,
        # startdate-enddate weekly segmentasi
        'startdate_weekly_mro' : startdate_weekly_mro,
        'startdate_weekly_mro_2' : startdate_weekly_mro_2,
        'startdate_weekly_mro_3' : startdate_weekly_mro_3,
        'startdate_weekly_mro_4' : startdate_weekly_mro_4,
        'startdate_weekly_mro_5' : startdate_weekly_mro_5,
        'enddate_weekly_mro' : enddate_weekly_mro,
        'enddate_weekly_mro_2' : enddate_weekly_mro_2,
        'enddate_weekly_mro_3' : enddate_weekly_mro_3,
        'enddate_weekly_mro_4' : enddate_weekly_mro_4,
        'enddate_weekly_mro_5' : enddate_weekly_mro_5,
        'sum_week_mro' : sum_week_mro,
        'sum_week_mro_2' : sum_week_mro_2,
        'sum_week_mro_3' : sum_week_mro_3, 
        'sum_week_mro_4' : sum_week_mro_4,
        'sum_week_mro_5' : sum_week_mro_5,
        # startdate - enddate weekly brisurf.
        'startdate_weekly_brisurf' : startdate_weekly_brisurf,
        'startdate_weekly_brisurf_2' : startdate_weekly_brisurf_2,
        'startdate_weekly_brisurf_3' : startdate_weekly_brisurf_3,
        'startdate_weekly_brisurf_4' : startdate_weekly_brisurf_4,
        'startdate_weekly_brisurf_5' : startdate_weekly_brisurf_5,
        'enddate_weekly_brisurf' : enddate_weekly_brisurf, 
        'enddate_weekly_brisurf_2' : enddate_weekly_brisrf_2,
        'enddate_weekly_brisurf_3' : enddate_weekly_brisrf_3, 
        'enddate_weekly_brisurf_4' : enddate_weekly_brisurf_4,
        'enddate_weekly_brisurf_5' : enddate_weekly_brisurf_5,
        'startdate_weekly_non_brisurf' : startdate_weekly_non_brisurf,
        'startdate_weekly_non_brisurf_2' : startdate_weekly_non_brisurf_2,
        'startdate_weekly_non_brisurf_3' : startdate_weekly_non_brisurf_3,
        'startdate_weekly_non_brisurf_4' : startdate_weekly_non_brisurf_4,
        'startdate_weekly_non_brisurf_5' : startdate_weekly_non_brisurf_5,
        'enddate_weekly_non_brisurf' : enddate_weekly_non_brisurf, 
        'enddate_weekly_non_brisurf_2' : enddate_weekly_non_brisrf_2,
        'enddate_weekly_non_brisurf_3' : enddate_weekly_non_brisrf_3, 
        'enddate_weekly_non_brisurf_4' : enddate_weekly_non_brisurf_4,
        'enddate_weekly_non_brisurf_5' : enddate_weekly_non_brisurf_5,
        'sum_week_brisurf' : sum_week_brisurf,
        'sum_week_brisurf_2' : sum_week_brisurf_2,
        'sum_week_brisurf_3' : sum_week_brisurf_3, 
        'sum_week_brisurf_4' : sum_week_brisurf_4,
        'sum_week_brisurf_5' : sum_week_brisurf_5,
        'sum_week_non_brisurf' : sum_week_non_brisurf,
        'sum_week_non_brisurf_2' : sum_week_non_brisurf_2,
        'sum_week_non_brisurf_3' : sum_week_non_brisurf_3, 
        'sum_week_non_brisurf_4' : sum_week_non_brisurf_4,
        'sum_week_non_brisurf_5' : sum_week_non_brisurf_5,    
        # startdate - enddate weekly captive non captive
        'startdate_weekly_captive' : startdate_weekly_captive,
        'startdate_weekly_captive_2' : startdate_weekly_captive_2,
        'startdate_weekly_captive_3' : startdate_weekly_captive_3,
        'startdate_weekly_captive_4' : startdate_weekly_captive_4,
        'startdate_weekly_captive_5' : startdate_weekly_brisurf_5,
        'enddate_weekly_captive' : enddate_weekly_captive, 
        'enddate_weekly_captive_2' : enddate_weekly_captive_2,
        'enddate_weekly_captive_3' : enddate_weekly_captive_3, 
        'enddate_weekly_captive_4' : enddate_weekly_captive_4,
        'enddate_weekly_captive_5' : enddate_weekly_captive_5,
        'sum_week_captive' : sum_week_captive,
        'sum_week_captive_2' : sum_week_captive_2,
        'sum_week_captive_3' : sum_week_captive_3, 
        'sum_week_captive_4' : sum_week_captive_4,
        'sum_week_captive_5' : sum_week_captive_5,
        'startdate_weekly_non_captive' : startdate_weekly_non_captive,
        'startdate_weekly_non_captive_2' : startdate_weekly_non_captive_2,
        'startdate_weekly_non_captive_3' : startdate_weekly_non_captive_3,
        'startdate_weekly_non_captive_4' : startdate_weekly_non_captive_4,
        'startdate_weekly_non_captive_5' : startdate_weekly_non_captive_5,
        'enddate_weekly_non_captive' : enddate_weekly_non_captive, 
        'enddate_weekly_non_captive_2' : enddate_weekly_non_captive_2,
        'enddate_weekly_non_captive_3' : enddate_weekly_non_captive_3, 
        'enddate_weekly_non_captive_4' : enddate_weekly_non_captive_4,
        'enddate_weekly_non_captive_5' : enddate_weekly_non_captive_5,
        'sum_week_non_captive' : sum_week_non_captive,
        'sum_week_non_captive_2' : sum_week_non_captive_2,
        'sum_week_non_captive_3' : sum_week_non_captive_3, 
        'sum_week_non_captive_4' : sum_week_non_captive_4,
        'sum_week_non_captive_5' : sum_week_non_captive_5,
        # monthly ros segmentasi
        'startdate_weekly_ros' : startdate_weekly_ros,
        'startdate_weekly_ros_2' : startdate_weekly_ros_2,
        'startdate_weekly_ros_3' : startdate_weekly_ros_3,
        'startdate_weekly_ros_4' : startdate_weekly_ros_4,
        'startdate_weekly_ros_5' : startdate_weekly_ros_5,
        'enddate_weekly_ros' : enddate_weekly_ros, 
        'enddate_weekly_ros_2' : enddate_weekly_ros_2,
        'enddate_weekly_ros_3' : enddate_weekly_ros_3, 
        'enddate_weekly_ros_4' : enddate_weekly_ros_4,
        'enddate_weekly_ros_5' : enddate_weekly_ros_5,
        'sum_week_ros' : sum_week_ros,
        'sum_week_ros_2' : sum_week_ros_2,
        'sum_week_ros_3' : sum_week_ros_3, 
        'sum_week_ros_4' : sum_week_ros_4,
        'sum_week_ros_5' : sum_week_ros_5,
        # mohtly klaim 
        'startdate_weekly_klaim' : startdate_weekly_klaim,
        'startdate_weekly_klaim_2' : startdate_weekly_klaim_2,
        'startdate_weekly_klaim_3' : startdate_weekly_klaim_3,
        'startdate_weekly_klaim_4' : startdate_weekly_klaim_4,
        'startdate_weekly_klaim_5' : startdate_weekly_klaim_5,
        'enddate_weekly_klaim' : enddate_weekly_klaim, 
        'enddate_weekly_klaim_2' : enddate_weekly_klaim_2,
        'enddate_weekly_klaim_3' : enddate_weekly_klaim_3, 
        'enddate_weekly_klaim_4' : enddate_weekly_klaim_4,
        'enddate_weekly_klaim_5' : enddate_weekly_klaim_5,
        'sum_week_klaim' : sum_week_klaim,
        'sum_week_klaim_2' : sum_week_klaim_2,
        'sum_week_klaim_3' : sum_week_klaim_3, 
        'sum_week_klaim_4' : sum_week_klaim_4,
        'sum_week_klaim_5' : sum_week_klaim_5,
        'posisi_outstanding' : posisi_outstanding
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

def xls_report_productivity_branch(id_job):
    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

    try:
        schedule = Shcedule.objects.get(pk = id_job)
    except  Exception as e:
        traceback.format_exc()
    
    if schedule.periode == 'harian':
        startdate = today - timedelta(1)
        enddate = today - timedelta(2)
    elif schedule.periode == 'bulanan':
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

    cabang = Shcedule.objects.get(pk = id_job)
    response = HttpResponse(content_type="application/ms-excel")
    filename = response['Content-Disposition'] = 'attachment; filename=Expenses' +\
        str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Cabang', 'Premi Total']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    transaksi = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date')
    sumTransaksi = transaksi.values("branch").order_by("branch").annotate(total_harga = Sum('Premi_Total'))
    rows = sumTransaksi.values_list('branch', 'total_harga')

    # rows = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).values_list('branch', 'premi_total')    

    for row in rows:
        row_num += 1
        # coba disini totalkan nilai unique setiap branch. 
        # lalu panggi kondisi-nya.
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

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
    msg.attach(filename, response.getvalue(), 'application/vnd.ms-excel'),

    msg.send()
