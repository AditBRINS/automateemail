from django.contrib import admin
from django.urls import path
from shceduleremail.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # -----login & logout admin-----------------------------------
    path('', login_admin), #-> login.html
    path('logut-admin/', logout_view),
    # ------------------------------------------------------------
    # ------Dashbord----------------------------------------------
    path('dashboard/', dashboard), #->dashboard.html
    path('form', form),
    path('delete/<int:running_id>', delete_schedule),
    path('update/<int:running_id>', update_schedule),
    path('detail-scheduler/<int:running_id>', detail_scheduler),
    path('status_update_on/<int:running_id>', status_on),
    path('status_update_off/<int:running_id>', status_off),
    # ------------------------------------------------------------
    # -------Insert Schedule report-------------------------------
    path('scheduler/', scheduler), #-> scheduler.html
    path('update_scheduler/<int:running_id>', update),
    # ------------------------------------------------------------
    # -------Konifguras template----------------------------------
    path('template-report/', template_report), #->configure_template.html
    path('configure_template/', configure_template),
    path('update_template_form/<int:id_template>/', update_template_form),
    path('update_template/<int:id_template>', update_template),
    path('delete_template/<int:id_template>', delete_template),
    # -------------------------------------------------------------
    # -------detail schdeuler--------------------------------------
    path('pdf_report/<int:id_log>/', GenerateReportLog.as_view()),
    path('report/<int:id_job>/', GenerateReport.as_view()),
    path('excel_report/<int:id_log>/', export_excel),
    # --------------------------------------------------------------
    path('update_job/<int:id_job>', update_job),
    path('send_email/<int:id_job>', send_email_func),
    
    path('status_update_on_job/<int:running_id>/<int:id_job>', status_on_job),
    path('status_update_off_job/<int:running_id>/<int:id_job>', status_off_job),
] 
