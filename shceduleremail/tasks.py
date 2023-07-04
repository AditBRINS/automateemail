# from automateemail.celery import shared_task, app
from datetime import timedelta, datetime, date
# import datetime

from anyio import current_time
# from pymysql import NULL
from sqlalchemy import null
from .models import Shcedule, Log
from .views import send_email_func
from celery import shared_task
from dateutil.relativedelta import relativedelta
# from django.conf import settings

# @shared_task(bind = True)
# def test_func(self):
#     for i in range(10):
#         print(i)
#     return "done"

@shared_task(bind = True)
def job(self):    
    today = date.today()
    Time = datetime.now().strftime("%H:%M:%S")
    currentTimes = datetime.strptime(Time, '%H:%M:%S').time()

    dateNow = datetime.now()
    
    # format date 
    shcedule_monthly = dateNow.strftime("%Y-%m-%d")
    month = datetime.strptime(shcedule_monthly, "%Y-%m-%d") 
    monthly = month.day
    shcedule_yearly = dateNow.strftime("%Y-%m-%d") 
    year = datetime.strptime(shcedule_yearly, "%Y-%m-%d")
    yearly = year.month
   
    schedule = Shcedule.objects.all()
    # monthlyDB = Shcedule.objects.filter(Fecha=date.strftime("%MM-%DD"))
    # monthlyDB2 = datetime.strptime(monthlyDB, '%m-%d')
    #----------------
    # Next Day
    #----------------
    tomorrow = datetime.now() + timedelta(days=1)
    nextDay = tomorrow.strftime("%Y-%m-%d")
    nextDay2 = datetime.strptime(nextDay, "%Y-%m-%d")
    print(nextDay2)
    #----------------
    # Next Week
    #----------------
    week = datetime.now() + timedelta(days=7)
    nextWeek = week.strftime("%Y-%m-%d")
    nextWeek2 = datetime.strptime(nextWeek, "%Y-%m-%d")
    print(nextWeek2)
    #----------------
    #Next month 
    #----------------
    d2 = datetime.now()
    d3 = d2 + relativedelta(months=1)
    nextmonth = d3.strftime("%Y-%m-%d")
    nextMonth = datetime.strptime(nextmonth, "%Y-%m-%d")
    print(d3)
    #----------------
    #Next year
    #----------------
    y2 = datetime.now()
    y3 = y2 + relativedelta(months=12)
    nextyear = y3.strftime("%Y-%m-%d")
    nextYear = datetime.strptime(nextyear, "%Y-%m-%d")

    for schedules in schedule:
        dates = schedules.waktu_eksekusi
        times = schedules.jam_eksekusi     
        status = schedules.status
        email = schedules.email_penerima
        # eksekusi = schedules.terakhir_eksekusi
        id_job = schedules.id_job
        period = schedules.periodic
        status_job = schedules.status_job
        kode_cabang_2 = schedules.kode_cabang
       
        # Periodic tanggal
        if period == 'daily':
            if kode_cabang_2 == '100' or kode_cabang_2 == '200':
                delete_cabang_100 = Shcedule.objects.filter(pk = id_job).filter(kode_cabang = '100')
                delete_cabang_200 = Shcedule.objects.filter(pk = id_job).filter(kode_cabang = '200')
                delete_cabang_100.delete()
                delete_cabang_200.delete()
            else:
                print('data terhapus')
                if status == True and status_job == True:
                    if times == currentTimes:
                        # --------------------------------
                        # kasih pengecualian id 100 & 200
                        # --------------------------------
                        if send_email_func(id_job):                        
                            Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                            Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
                            job = Shcedule.objects.get(pk = id_job)
                            format_laporan = Shcedule.objects.values('format_laporan')
                            log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                            log.save()
                        else:
                            Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                            Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
                            job = Shcedule.objects.get(pk = id_job)
                            format_laporan = Shcedule.objects.values('format_laporan')
                            log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                            log.save()
                if status == True and status_job == False:
                    if times == currentTimes:
                        Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                        Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
                if status == False:
                    if times == currentTimes:
                        Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                        Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
                else:
                    print('waiting-daily')
        elif period == 'weekly':
            if kode_cabang_2 == '100' or kode_cabang_2 == '200':
                delete_cabang_100 = Shcedule.objects.filter(pk = id_job).filter(kode_cabang = '100')
                delete_cabang_200 = Shcedule.objects.filter(pk = id_job).filter(kode_cabang = '200')
                delete_cabang_100.delete()
                delete_cabang_200.delete()
            else:
                print('data terhapus')
                if status == True and status_job == True:
                    if dates == today: 
                        if times == currentTimes:
                            if send_email_func(id_job):
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextWeek2)
                                job = Shcedule.objects.get(pk = id_job)
                                format_laporan = Shcedule.objects.values('format_laporan')
                                log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                                log.save()
                            else:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextWeek2)
                                job = Shcedule.objects.get(pk = id_job)
                                format_laporan = Shcedule.objects.values('format_laporan')
                                log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                                log.save()
                if status == True and status_job == False:
                    if dates == today:
                            if times == currentTimes:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextWeek2)
                if status == False:
                    if dates == today:
                            if times == currentTimes:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextWeek2)
                else:
                    print('waiting-weekly')
        elif period == 'monthly':
            if status == True and status_job == True:
                if dates == today:
                    if monthly ==  dates.day:
                        if times == currentTimes:
                            # --------------------------------
                            # kasih pengecualian id 100 & 200
                            # --------------------------------
                            if send_email_func(id_job):
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
                                job = Shcedule.objects.get(pk = id_job)
                                format_laporan = Shcedule.objects.values('format_laporan')
                                log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                                log.save()
                            else:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
                                job = Shcedule.objects.get(pk = id_job)
                                format_laporan = Shcedule.objects.values('format_laporan')
                                log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                                log.save()
            if status == True and status_job == False:
                if dates == today:
                    if monthly ==  dates.day:
                        if times == currentTimes:
                            Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                            Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
            if status == False:
                if dates == today:
                    if monthly ==  dates.day:
                        if times == currentTimes:
                            Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                            Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
            else:
                print('waiting-monthly')
        elif period == 'yearly':
            if status == True and status_job == True:
                if dates == today:
                    if yearly == dates.month:
                        if monthly == dates.day: 
                            if times == currentTimes:
                            # --------------------------------
                            # kasih pengecualian id 100 & 200
                            # --------------------------------
                                if send_email_func(id_job):
                                    Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                    Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
                                    job = Shcedule.objects.get(pk = id_job)
                                    format_laporan = Shcedule.objects.values('format_laporan')
                                    log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                                    log.save()
                                else:
                                    Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                    Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
                                    job = Shcedule.objects.get(pk = id_job)
                                    format_laporan = Shcedule.objects.values('format_laporan')
                                    log = Log(id_job = job, status = 1, eksekusi = dateNow, running_id = job.running_id, email_penerima = email, format_laporan = job.format_laporan)
                                    log.save()
            if status == True and status_job == False:
                if dates == today:
                    if yearly == dates.month:
                        if monthly == dates.day: 
                            if times == currentTimes:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
            if status == False:
                if dates == today:
                    if yearly == dates.month:
                        if monthly == dates.day: 
                            if times == currentTimes:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
            else:
                print('waiting-yearly')
        else: 
            print('no-job')       
    