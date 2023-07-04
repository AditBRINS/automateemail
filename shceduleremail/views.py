from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from matplotlib.style import context
from .models import Log, Shcedule, tbl_produksi_segmentasi, Log, Running, Login, tbl_template, tbl_os
from .forms import FormShcedule, FormEmail, FormLogin, FormTemplate
from django.core.paginator import Paginator
from django.views.generic import View
from django.db.models import Sum
from .utils import render_to_pdf
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
from django.db.models.functions import TruncMonth, TruncYear
import xlwt
from datetime import date, datetime
from .models import Shcedule
# Function -------------------------
from .function.def_send_mail import *
from .function.def_schedule_mail import *
from .function.def_report_log import *
from .function.def_export_xls import *
from .modul_send_mail.def_send_mail import *
from .modul_send_mail.def_send_mail_100_200 import *
from .modul_template.configure_template import *

# --------------------------
# login & logout admin
# --------------------------
def login_admin(request): 
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = Login.objects.filter(email = email)
        if user.exists():
            if user[0].password == password:
                userlog = Login.objects.get(email = email)
                print(userlog)
                if userlog is not None:
                    login(request, userlog)
                    request.session['email'] = email
                    return HttpResponseRedirect('/dashboard')
                else:
                    return HttpResponseRedirect('')
            else:

                return HttpResponseRedirect ('')
        else:
            return HttpResponseRedirect ('')
    else:
        return render(request, 'login.html', {})
    
def logout_view(request):
    logout(request)
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = Login.objects.filter(email = email)
        if user.exists():
            if user[0].password == password:
                userlog = Login.objects.get(email = email)
                print(userlog)
                if userlog is not None:
                    login(request, userlog)
                    request.session['email'] = email
                    return HttpResponseRedirect('/dashboard')
                else:
                    return HttpResponseRedirect('')
            else:

                return HttpResponseRedirect ('')
        else:
            return HttpResponseRedirect ('')
    else:
        return render(request, 'login.html', {})
    # return render(request, 'login.html', {})
# --------------------------

# --------------------------
# Laman dashboard
# --------------------------
def dashboard(request):
    if request.session.get('email') is None:
        return HttpResponseRedirect('')
    schedule = Shcedule.objects.order_by('-running_id').values('running_id', 'waktu_eksekusi', 'jam_eksekusi', 'status', 'periodic', 'template', 'id_template', 'format_laporan', 'data_report').distinct()

    waktu_ekseksusi = Shcedule.objects.order_by('-running_id').values('waktu_eksekusi').distinct()
    print(waktu_ekseksusi)


    obj_t = Shcedule.objects.filter(status = True).order_by('running_id').values('running_id').distinct()
    obj_f = Shcedule.objects.filter(status = False).order_by('running_id').values('running_id').distinct()
    obj_true = obj_t.count()
    obj_false = obj_f.count()
    today = date.today()

    paginator = Paginator(schedule, 5)
    page_number = request.GET.get('page')
    schedule = paginator.get_page(page_number)

    template = tbl_template.objects.values('nama_template', 'id_template')

    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)

    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)

    context = {
        'schedule': schedule,
        'obj_true': obj_true,
        'obj_false': obj_false,
        'today':today,
        'template':template,
        'last_day_of_prev_month' : last_day_of_prev_month, 
        'start_day_of_prev_month' : start_day_of_prev_month
    }
    return render(request, 'dashbord.html', context)

def status_on(request, running_id):
    # statusUpdate = Shcedule.objects.filter(pk = id_job)
    statusUpdate = Shcedule.objects.filter(running_id = running_id)

    statusUpdate.update(status = True)

    return HttpResponseRedirect('/dashboard/')

def status_off(request, running_id):
    # statusUpdate = Shcedule.objects.filter(pk = id_job)
    statusUpdate = Shcedule.objects.filter(running_id = running_id)

    statusUpdate.update(status = False)

    return HttpResponseRedirect('/dashboard/')
# --------------------------
# Laman konfigurasi template
# --------------------------
def configure_template(request):    
    return insert_template(request)

def delete_template(request, id_template):
    deletemplate = tbl_template.objects.filter(id_template=id_template)
    deletemplate.delete()

    return HttpResponseRedirect('/template-report/', context)

def update_template(request, id_template):
    return insert_update_template(request, id_template)

def formtemplate(request):
    template = tbl_template.objects.all()

    context = {
        'template': template
    }

    return render(request, 'tambah-email.html', context)

# --------------------------
# Buat Penjadwalan
# --------------------------
def scheduler(request):
    if request.session.get('email') is None:
        return HttpResponseRedirect('')  
    return insert_scheduler(request) #def di file -> def_schedule_mail

def form(request):
    schedule = Shcedule.objects.all()
    template = tbl_template.objects.all()
    email_pengirim = settings.EMAIL_HOST_USER

    context = {
        'schedule': schedule,
        'template': template,
        'email_pengirim': email_pengirim
    }

    return render(request, 'scheduler.html', context)

def delete_schedule(self, running_id):
    delschedule = Shcedule.objects.filter(running_id = running_id)
    delschedule.delete()

    schedule = Shcedule.objects.all()

    context = {
        'schedule' : schedule
    }

    return HttpResponseRedirect('/dashboard/', context)

def update(request, running_id):
    return update_scheduler(request, running_id) #def di file -> def_schedule_mail

def update_schedule(request, running_id):
    schedule = Shcedule.objects.filter(running_id = running_id)
    template = tbl_template.objects.all()
    running_id = Shcedule.objects.filter(running_id = running_id).values('running_id', 'waktu_eksekusi', 'jam_eksekusi', 'status', 'periodic', 'template', 'id_template', 'format_laporan', 'data_report').distinct()

    context = {
        'schedule' : schedule,
        'running_id' : running_id,
        'template' : template,
        'form' : form
    }
    return render(request, 'scheduler.html', context)
# --------------------------

# --------------------------
# laman detail scheduler
# --------------------------
def detail_scheduler(request, running_id):
    if request.session.get('email') is None:
        return HttpResponseRedirect('/login')  
    schedule = Shcedule.objects.filter(running_id = running_id)

    obj_t = Log.objects.filter(status = True)
    obj_f = Log.objects.filter(status = False)
    true = obj_t.filter(id_job__running_id__contains = running_id)
    false = obj_f.filter(id_job__running_id__contains = running_id)
    obj_true = true.count()
    obj_false = false.count()
    today = date.today()

    log = Log.objects.filter(running_id = running_id).order_by('-id_log')

    paginator = Paginator(log, 9)
    page_number = request.GET.get('page')
    log = paginator.get_page(page_number)

    running_id = Shcedule.objects.values('running_id')

    context = {
        'schedule': schedule,
        'obj_true': obj_true,
        'obj_false': obj_false,
        'today':today,
        'log' : log,
        'running_id':running_id,
    }

    return render(request, 'detail-scheduler.html', context)

def template_report(request):
    if request.session.get('email') is None:
        return HttpResponseRedirect('/login')  
    template = tbl_template.objects.all()

    paginator = Paginator(template, 5)
    page_number = request.GET.get('page')
    templatepage = paginator.get_page(page_number)

    context = {
        'template' : template,
        'templatepage' : templatepage
    }

    return render(request,'configure_template.html', context)

def update_template_form(request, id_template):
    template = tbl_template.objects.filter(id_template = id_template)

    context = {
        'template' : template,
        'id_template' : id_template,
        'formtemplate' : formtemplate,
    }

    return render(request, 'configure_template.html', context)
# -------------------------

# --------------------------
# Generate lihat pdf
# --------------------------
class GenerateReportLog(View):
    # Pada pembuatan pdf akan dilakukan inputan 2 kali dari database.
    # Database email dan database detail transaksi.
    def get(self, request, id_log,  *args, **kwargs):
        try:
            log = Log.objects.get(pk = id_log)
        except  Exception as e:
            traceback.format_exc()

        if log.format_laporan == 'pdf':
            if log.id_job.template == 1:
                return report_segker_1(id_log)
        else: 
                return report_segker_2(id_log)

class GenerateReport(View):
    # Pada pembuatan pdf akan dilakukan inputan 2 kali dari database.
    # Database email dan database detail transaksi.
    def get(self, request, id_job,  *args, **kwargs):
        try:
            schedules = Shcedule.objects.get(pk = id_job)
        except  Exception as e:
            traceback.format_exc()

        # template 1, merupakan template rekapan. 
        # template 2, meupakan template detail.
        if schedules.kode_cabang != '100' and schedules.kode_cabang !=  '200': 
            if schedules.template == 1:
                return report_performace_branch_1(id_job)
            else: 
                return report_performace_branch_2(id_job)
        else:
            if schedules.template == 1:
                return report_performace_100_200_1(id_job)
            else: 
                return report_performace_100_200_2(id_job)
        
# ---------------------------
# export excel
# ---------------------------
def export_excel(request, id_log):
    try:
        log = Log.objects.get(pk = id_log)
    except  Exception as e:
        traceback.format_exc()
    
    today = date.today()
    startdate = today - timedelta(1)
    enddate = today + relativedelta(day=1)

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=Expenses' +\
        str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    if(log.id_job.template == 1):
        columns = ['Tanggal', 'Branch', 'Premi WholeSale', 'Premi Mikro', 'Premi Ritel', 'Premi Ritel Mikro', 'Premi Digital', 'Premi Syariah', 'Premi Total']
        
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date').values_list('date', 'branch', 'Premi_WHOLESALE', 'premi_mikro', 'premi_ritel', 'Premi_RITEL_MIKRO', 'Premi_DIGITAL', 'Premi_SYARIAH', 'Premi_Total')

        for row in rows:
            # row_num = row_num + 1
            if(log.id_job.kode_cabang == row[:][1]):
                row_num += 1
                print(row[:][1])
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, str(row[col_num]), font_style)
            else:
                False
        wb.save(response)
    else:
        columns = ['Branch', 'Premi Total']
        
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date').values_list('branch', 'Premi_Total')

        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)

        wb.save(response)

    return response
# ---------------------------

def status_on_job(request, id_job, running_id):
    statusUpdate = Shcedule.objects.filter(pk = id_job)
    id_running = Shcedule.objects.filter(running_id = running_id)
    
    statusUpdate.update(status_job = True)

    obj = Shcedule.objects.get(pk = id_job)
    field_object = Shcedule._meta.get_field('running_id')
    field_value = field_object.value_from_object(obj)
    field_value2 = field_value
    
    return HttpResponseRedirect('/detail-scheduler/'+str(field_value2)+'')
    
def status_off_job(request, id_job, running_id):
    id_running = Shcedule.objects.filter(running_id = running_id)
    statusUpdate = Shcedule.objects.filter(pk = id_job)

    statusUpdate.update(status_job = False)
    
    obj = Shcedule.objects.get(pk = id_job)
    field_object = Shcedule._meta.get_field('running_id')
    field_value = field_object.value_from_object(obj)
    field_value2 = field_value
    
    return HttpResponseRedirect('/detail-scheduler/'+str(field_value2)+'')

def update_job(request, id_job):
    update_schedule = Shcedule.objects.get(pk = id_job)

    context = {
        'updateSchedule' : update_schedule
    }

    return render(request, 'update-scheduler.html', context)

# ---------------------------
# Kirim Email
# ---------------------------
def send_email_func(id_job):
    try:
        schedule = Shcedule.objects.get(pk = id_job)
    except  Exception as e:
        traceback.format_exc()

    # Ambil data satu hari sebelum pengiriman.
    if schedule.template == 1: 
        if schedule.format_laporan == 'pdf':
            if schedule.kode_cabang != '100' and schedule.kode_cabang != '200':
                # template pengiriman rekapan cabang
                return pdf_report_performance_branch_1(id_job)
            else:
                # template pengiriman rekapan pusat
                return schedule_100_200_1(id_job)
    else :
        if schedule.format_laporan == 'pdf':
            if schedule.kode_cabang != '100' and schedule.kode_cabang != '200':
                # template pengiriman detail, bukan pusat
                return pdf_report_performance_branch_2(id_job)
            else:
                # template pengiriman detail, pusat
                return schedule_100_200_2(id_job)
            
    # return HttpResponse ('email berhasil dikrim')

from .tasks import job
# today = date.today()

def test(request, id_job):
    job.delay()
    
    return HttpResponse('done')


