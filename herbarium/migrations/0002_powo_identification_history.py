from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('herbarium','0001_initial'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.AddField('taxon','powo_id',models.CharField(blank=True,db_index=True,max_length=120,verbose_name='POWO identifier')),
        migrations.AddField('taxon','powo_url',models.URLField(blank=True,verbose_name='POWO URL')),
        migrations.AddField('taxon','name_authorship',models.CharField(blank=True,max_length=255,verbose_name='命名者')),
        migrations.AddField('taxon','powo_verified_at',models.DateTimeField(blank=True,null=True,verbose_name='POWO 核對時間')),
        migrations.AddField('taxon','accepted_taxon',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='synonyms',to='herbarium.taxon',verbose_name='對應接受名')),
        migrations.AddField('identification','original_name',models.CharField(blank=True,max_length=255,verbose_name='原始鑑定學名')),
        migrations.AddField('identification','recorded_by',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='recorded_identifications',to=settings.AUTH_USER_MODEL,verbose_name='登錄 Curator')),
        migrations.AddField('identification','created_at',models.DateTimeField(auto_now_add=True,null=True,verbose_name='建立時間')),
        migrations.AddField('identification','updated_at',models.DateTimeField(auto_now=True,null=True,verbose_name='更新時間')),
        migrations.AddField('identification','withdrawn_at',models.DateTimeField(blank=True,null=True,verbose_name='撤回時間')),
        migrations.AddField('identification','withdrawal_reason',models.TextField(blank=True,verbose_name='撤回原因')),
        migrations.AddConstraint('identification',models.UniqueConstraint(fields=('specimen',),condition=Q(is_current=True),name='one_current_identification_per_specimen')),
    ]
