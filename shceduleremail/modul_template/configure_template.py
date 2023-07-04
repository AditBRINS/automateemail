from django.http import HttpResponseRedirect
from matplotlib.style import context
from ..models import tbl_template
from ..forms import FormTemplate
from django.http import HttpResponse
from django.contrib import messages

def insert_template(request):    
    form_temp = FormTemplate(request.POST)
    template = tbl_template.objects.all()
    id_template = tbl_template.objects.latest('id_template')
    field_object = tbl_template._meta.get_field('id_template')
    field_value = field_object.value_from_object(id_template)
    field_value2 = field_value + 1

    if request.method == 'POST':
        if form_temp.is_valid():
            nama_template = request.POST.get('nama_template')
            template = request.POST.get('template')
            periode = request.POST.get('periode')
            data_report = request.POST.get('data_report')
            form_temp = tbl_template(id_template = field_value2, nama_template = nama_template, template = template ,periode = periode, data_report = data_report)
            form_temp.save()
    
    return HttpResponseRedirect('/template-report')

def insert_update_template(request, id_template):
    if request.method == 'POST':
        nama_template = request.POST.get('nama_template')
        template = request.POST.get('template')
        periode = request.POST.get('periode')
        tbl_template.objects.filter(id_template = id_template).update(nama_template = nama_template, template = template, periode = periode)
        messages.success(request, 'Data berhasil diperbarui' )
    
        return HttpResponseRedirect('/template-report/', context)