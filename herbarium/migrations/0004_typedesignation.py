from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('herbarium','0003_sitesettings'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[migrations.CreateModel(name='TypeDesignation',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('type_status',models.CharField(choices=[('holotype','Holotype'),('isotype','Isotype'),('lectotype','Lectotype'),('isolectotype','Isolectotype'),('neotype','Neotype'),('isoneotype','Isoneotype'),('syntype','Syntype'),('paratype','Paratype'),('epitype','Epitype'),('isoepitype','Isoepitype'),('other','Other (specify in notes)')],max_length=24,verbose_name='模式類型')),
        ('type_name',models.CharField(help_text='The name typified, NOT necessarily the current POWO accepted name.',max_length=500,verbose_name='模式學名（含命名者；保留原文）')),
        ('original_publication',models.TextField(blank=True,verbose_name='原始發表文獻')),
        ('designation_reference',models.TextField(blank=True,verbose_name='模式指定文獻')),
        ('related_type_barcode',models.CharField(blank=True,max_length=255,verbose_name='相關模式標本館與條碼')),
        ('evidence_url',models.URLField(blank=True,verbose_name='文獻或證據網址')),
        ('verification_status',models.CharField(choices=[('unverified','Unverified'),('verified','Verified'),('disputed','Disputed')],default='unverified',max_length=20,verbose_name='核實狀態')),
        ('verified_by',models.CharField(blank=True,max_length=255,verbose_name='核實者')),
        ('verified_on',models.DateField(blank=True,null=True,verbose_name='核實日期')),
        ('notes',models.TextField(blank=True,verbose_name='備註與依據')),
        ('is_public',models.BooleanField(default=False,help_text='Unverified assertions should normally remain internal until reviewed.',verbose_name='已核准公開')),
        ('created_at',models.DateTimeField(auto_now_add=True,verbose_name='建立時間')),
        ('updated_at',models.DateTimeField(auto_now=True,verbose_name='修改時間')),
        ('recorded_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='recorded_type_designations',to=settings.AUTH_USER_MODEL,verbose_name='登錄 Curator')),
        ('specimen',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='type_designations',to='herbarium.specimen',verbose_name='實體標本')),
        ('type_taxon',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='type_designations',to='herbarium.taxon',verbose_name='對應名稱（可選）')),
    ],options={'verbose_name':'模式標本指定紀錄','verbose_name_plural':'模式標本指定紀錄','ordering':['specimen_id','type_name','id']})]
