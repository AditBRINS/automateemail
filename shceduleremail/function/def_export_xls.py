from django.http import HttpResponseRedirect, HttpResponse
from ..models import Log, Shcedule, tbl_cabang, tbl_produksi_segmentasi, Log, Running, Login, tbl_template
from django.http import HttpResponse
from django.contrib.auth.hashers import *
from django.contrib.auth.hashers import check_password
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
import traceback 
from django.db.models.functions import TruncMonth
import xlwt
from datetime import date, datetime
from ..models import Shcedule

def export_xls(id_log):
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

    columns = ['Tanggal', 'Branch', 'Premi WholeSale', 'Premi Mikro', 'Premi Ritel', 'Premi Ritel Mikro', 'Premi Digital', 'Premi Syariah', 'Premi Total']
    
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = tbl_produksi_segmentasi.objects.filter(date__range=[enddate, startdate]).order_by('date').values_list('date', 'branch', 'Premi_WHOLESALE', 'premi_mikro', 'premi_ritel', 'Premi_RITEL_MIKRO', 'Premi_DIGITAL', 'Premi_SYARIAH', 'Premi_Total')

    for row in rows:
        row_num += 1
        if(log.id_job.kode_cabang == row[:][1]):
            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        else: 
            pass
    wb.save(response)

    return response