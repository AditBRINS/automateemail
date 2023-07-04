from sqlite3 import Date
from django.db import models

# Create your models here.

class tbl_cabang(models.Model):
    branch = models.CharField(primary_key=True, max_length=255)
    branchName = models.CharField(max_length=255)
    Jenis = models.CharField(max_length=255)
    Email = models.CharField(max_length=255)
    # branch = models.CharField(max_length=3)
    # branchName = models.CharField(max_length=50)
    # Latitude = models.DecimalField(decimal_places=9,max_digits=21)
    # Longtitude = models.DecimalField(decimal_places=9,max_digits=21)
    # Jenis = models.CharField(max_length=50)
    # branchsupervisi = models.CharField(max_length = 3)
    # branchsupervisi_name = models.CharField(max_length=50)
    # Email = models.CharField(max_length=35)

    class Meta:
        managed = False
        db_table = 'email_test'

class tbl_cabang_report(models.Model):
    id = models.AutoField(primary_key=True)
    kode_cabang = models.IntegerField()
    cabang_report = models.CharField(max_length=50)
    premi = models.IntegerField()
    Tanggal = models.DateField()

    class Meta:
        managed = False
        db_table = 'cabang_report'

class tbl_produksi_segmentasi(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    branch = models.CharField(max_length=5)
    nama_cabang = models.CharField(max_length=50)
    Premi_WHOLESALE = models.FloatField()
    premi_mikro = models.FloatField()
    premi_ritel = models.FloatField()
    Premi_RITEL_MIKRO  = models.FloatField()
    Premi_DIGITAL = models.FloatField()
    Premi_SYARIAH = models.FloatField()
    Premi_Total = models.FloatField()
    kode_mro = models.CharField(max_length=3)
    nama_mro = models.CharField(max_length=50)
    captive_non_captive = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'produksi_segmentasi'

class persentase_mro(models.Model):
    id = models.AutoField(primary_key=True)
    kode_mro = models.CharField(max_length=3)
    premi_mikro_captive = models.FloatField()
    premi_mikro_non_captive = models.FloatField()
    premi_ritel_captive = models.FloatField()
    premi_ritel_non_captive = models.FloatField()
    premi_digital_captive = models.FloatField()
    premi_digital_non_captive = models.FloatField()
    premi_wholesale = models.FloatField()
    premi_syariah = models.FloatField()

    class Meta: 
        managed = False
        db_table = 'persentase_mro'

class target_mro(models.Model):
    id = models.AutoField(primary_key=True)
    Target_Wholesale = models.BigIntegerField()
    Target_Syariah = models.BigIntegerField()
    Target_retail_digital_captive = models.BigIntegerField()
    Target_Mikro_Captive = models.BigIntegerField()
    Target_Retail_Digital_Non_Captive = models.BigIntegerField()
    Target_Mikro_Non_Captive = models.BigIntegerField()
    Target_Retail_Digital = models.FloatField()
    branch = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'target_mro_bulanan_2023'

class captive_non_captive(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    branch = models.CharField(max_length=5)
    branchName = models.CharField(max_length=50)
    Kode_MRO = models.CharField(max_length=5)
    Nama_MRO = models.CharField(max_length=5)
    captive_non_captive = models.CharField(max_length=50)
    premi = models.FloatField()

    class Meta:
        managed = False
        db_table = 'premi_capncap'

class tbl_captive_non_captive_report(models.Model):
    id = models.IntegerField(primary_key = True)

    class Meta:
        managed = False
        db_table = 'cnc_report'

class tbl_sourcename(models.Model):
    id = models.IntegerField(primary_key=True)
    tgl_produksi = models.DateField(null=True, blank=True)
    kode_cabang = models.CharField(max_length = 10)
    cabang = models.CharField(max_length=50)
    kode_sumber = models.CharField(max_length=50)
    sumber_bisnis = models.CharField(max_length=50)
    premi = models.FloatField()

    class Meta:
        managed = False
        db_table = 'sourcename'

class tbl_marketing_officer(models.Model):
    id = models.IntegerField(primary_key=True)
    Tanggal = models.DateField(null=True, blank=True)
    kode_cabang = models.CharField(max_length = 10)
    cabang = models.CharField(max_length= 50)
    nama_akun_mo = models.CharField(max_length=100)
    nama_mo = models.CharField(max_length = 150)
    premi = models.FloatField()

    class Meta: 
        managed = False
        db_table = 'marketing_officer'

class tbl_template(models.Model):
    id_template = models.AutoField(primary_key=True)
    nama_template = models.CharField(null = True, blank = True, max_length=255)
    template = models.IntegerField(null = True, blank = True)
    periode = models.CharField(null=True, blank=True, max_length=255)
    data_report = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'template'

class Shcedule(models.Model):
    id_job = models.AutoField(primary_key=True)
    waktu_eksekusi = models.DateField(null=True, blank=True)
    jam_eksekusi = models.TimeField(null=True, blank=True)
    status = models.BooleanField(default = False)
    terakhir_eksekusi = models.DateField(null=True, blank=True)
    periodic = models.CharField(max_length=255)
    template = models.IntegerField()
    running_id = models.IntegerField(null=True, blank=True, unique = True)
    email_penerima = models.CharField(null = True, blank = True, max_length=255)
    kode_cabang = models.CharField(null=True, blank=True, max_length=255)
    # kode_cabang = models.ForeignKey("Cabang", db_column='kode_cabang', on_delete=models.DO_NOTHING)
    # id_template = models.ForeignKey("Template", db_column='id_template', on_delete=models.DO_NOTHING)
    id_template = models.IntegerField(null=True, blank=True)
    status_job = models.BooleanField(default = True)
    periode = models.CharField(null=True, blank=True, max_length=255)
    format_laporan = models.CharField(null=True, blank=True, max_length=255)
    data_report = models.CharField(null=True, blank=True, max_length=255)
    jenis_uker = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s %s %s %s %s' % (self.id_job, self.waktu_eksekusi, self.jam_eksekusi, self.status, self.terakhir_eksekusi, self.periodic, self.template, self.running_id, self.email_penerima, self.kode_cabang, self.id_template, self.status_job, self.periode)

    class Meta:
        managed = False
        db_table = 'shcedule'

class Log(models.Model):
    id_log = models.AutoField(primary_key=True)
    id_job = models.ForeignKey("Shcedule", db_column='id_job', on_delete=models.DO_NOTHING)
    status = models.BooleanField(default = False)
    eksekusi = models.DateTimeField(null=True, blank=True)
    running_id = models.IntegerField(null=True, blank=True)
    email_penerima = models.CharField(null = True, blank = True, max_length=255)
    format_laporan = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return '%s %s %s %s' % (self.id_log, self.id_job.pk, self.status, self.eksekusi)

    class Meta:
        managed = False
        db_table = 'Log'

class Running(models.Model):
    idRunning= models.AutoField(primary_key=True)
    running_id = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'running'

class Login(models.Model):
    login_admin_id = models.AutoField(primary_key=True)
    email = models.CharField(null = True, blank = True, max_length=255)
    password = models.CharField(null = True, blank = True, max_length=255)
    last_login  = models.DateTimeField(auto_now = True)

    class Meta:
        managed = False
        db_table = 'login_admin'

class tbl_brisurfnonbrisurf(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    BRANCH = models.CharField(max_length=5)
    branchName = models.CharField(max_length=50)
    kategori = models.CharField(max_length=11)
    Premi = models.FloatField()

    class Meta: 
        managed = False
        db_table = 'premi_brisurfnonbrisurf'

class tbl_os(models.Model):
    id = models.AutoField(primary_key=True)
    as_at = models.DateField()
    year = models.DateField()
    Branch = models.CharField(max_length=10)
    Branch_Supervisi_name = models.CharField(max_length=50)
    Branch_Name = models.CharField(max_length=100)
    Outstanding = models.FloatField()
    Outstanding_due = models.IntegerField()
    Outstanding_Undue = models.IntegerField()
    OS_overdue_Brisurf_Captive = models.FloatField()
    OS_overdue_Non_Brisurf_Captive = models.FloatField()
    OS_Overdue_NonCaptive = models.FloatField()
    OS_wpc_Brisurf_Captive = models.FloatField()
    OS_wpc_Non_Brisurf_Captive = models.FloatField()
    OS_wpc_NonCaptive = models.FloatField()

    class Meta:
        managed = False
        db_table = 'OS_Cabang_2'

class tbl_target_seg(models.Model):
    id = models.AutoField(primary_key=True)
    Branch = models.CharField(max_length=5)
    BranchName = models.CharField(max_length=50)
    Retail_Pos_BRI = models.FloatField()
    Retail_Pos_umum = models.FloatField()
    Mikro_Pos_BRI = models.FloatField()
    Mikro_Pos_umum = models.FloatField()
    Wholesale = models.FloatField()
    Syariah = models.FloatField()
    Digital = models.FloatField()


    class Meta:
        managed = False
        db_table = 'tbl_target_segmen_bulan_2023'

class tbl_persentase_target(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=3)
    branch_name = models.CharField(max_length=50)
    Retail_Pos_BRI = models.FloatField()
    Retail_Pos_umum = models.FloatField()
    Mikro_Pos_BRI = models.FloatField()
    Mikro_Pos_umum = models.FloatField()
    Wholesale = models.FloatField()
    Syariah = models.FloatField()
    Digital = models.FloatField()

    class Meta:
        managed = False
        db_table = 'persentase_segmentasi'    

class tbl_target_pusat(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=3)
    branch_name = models.CharField(max_length=50)
    wholesale = models.FloatField()
    ritel = models.FloatField()
    mikro = models.FloatField()
    ritel_mikro = models.FloatField()
    syariah = models.FloatField()
    digital = models.FloatField()
    premi_total = models.FloatField()

    class Meta:
        managed = False
        db_table = 'target_pusat'


class tbl_persentase_pusat(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=3)
    branch_name = models.CharField(max_length=50)
    persen_wholesale = models.FloatField()
    persen_ritel = models.FloatField()
    persen_mikro = models.FloatField()
    persen_ritel_mikro = models.FloatField()
    persen_syariah = models.FloatField()
    persen_digital = models.FloatField()
    persen_premi_total = models.FloatField()

    class Meta:
        managed = False
        db_table = 'persentase_pusat'

class tbl_klaim_cabang(models.Model): 
    id = models.AutoField(primary_key=True)
    Tanggal = models.DateField()
    Branch = models.CharField(max_length=3)
    NamaBranch = models.CharField(max_length=50)
    Nilai = models.FloatField()

    class Meta: 
        managed = False
        db_table = 'Klaim_per_cabang'

class tbl_sum_segmentasi(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=5)
    nama_cabang = models.CharField(max_length=5)
    wholesale = models.FloatField()
    syariah = models.FloatField()
    digital = models.FloatField()
    Retail_Pos_BRI = models.FloatField()
    Retail_Pos_umum = models.FloatField()
    Mikro_Pos_BRI = models.FloatField()
    Mikro_Pos_umum = models.FloatField()

    class Meta:
        managed = False
        db_table = 'sum_segmentasi'