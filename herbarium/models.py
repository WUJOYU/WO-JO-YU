from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q

class Taxon(models.Model):
    family = models.CharField('科名（來源紀錄）', max_length=160, blank=True)
    scientific_name = models.CharField('學名（來源紀錄）', max_length=255)
    vernacular_name = models.CharField('中文名（來源紀錄）', max_length=255, blank=True)
    taxonomic_status = models.CharField('分類確認狀態', max_length=30, default='unverified', choices=[('unverified','未核對'),('accepted','已確認'),('synonym','異名')])
    notes = models.TextField('備註', blank=True)
    powo_id = models.CharField('POWO identifier', max_length=120, blank=True, db_index=True)
    powo_url = models.URLField('POWO URL', blank=True)
    accepted_taxon = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='synonyms', verbose_name='對應接受名')
    name_authorship = models.CharField('命名者', max_length=255, blank=True)
    powo_verified_at = models.DateTimeField('POWO 核對時間', null=True, blank=True)
    PUBLICATION_CHOICES = [
        ('pending', '待審核'),
        ('approved', '允許公開'),
        ('restricted', '限制公開'),
    ]
    publication_status = models.CharField(
        '學名公開審核', max_length=20, choices=PUBLICATION_CHOICES,
        default='pending', db_index=True,
    )
    publication_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name='reviewed_taxon_publications', verbose_name='學名公開審核者',
    )
    publication_reviewed_at = models.DateTimeField('學名公開審核時間', null=True, blank=True)

    class Meta:
        verbose_name='分類群'
        verbose_name_plural='分類群'
        constraints=[models.UniqueConstraint(fields=['family','scientific_name'],name='unique_family_scientific_name')]
        ordering=['family','scientific_name']
    def clean(self):
        if self.accepted_taxon_id and self.accepted_taxon_id == self.pk:
            raise ValidationError({'accepted_taxon':'分類群不可指向自己。'})
        if self.taxonomic_status == 'accepted' and self.accepted_taxon_id:
            raise ValidationError({'accepted_taxon':'接受名不可再指向另一個接受名。'})
        if self.accepted_taxon and self.accepted_taxon.taxonomic_status != 'accepted':
            raise ValidationError({'accepted_taxon':'異名必須指向已確認的接受名。'})
    @property
    def display_accepted_name(self):
        if self.accepted_taxon_id and self.accepted_taxon.publication_status == 'approved':
            return self.accepted_taxon.scientific_name
        return self.scientific_name
    def __str__(self): return self.scientific_name

class CollectingEvent(models.Model):
    REVIEW_STATUS = [
        ('pending', '未審核'),
        ('in_review', '審核中'),
        ('verified', '已核實'),
        ('needs_correction', '需修正'),
    ]

    COORDINATE_REVIEW_STATUS = [
        ('pending', '未核對'),
        ('verified', '已核實'),
        ('needs_correction', '需修正'),
        ('not_available', '無座標'),
    ]

    review_status = models.CharField(
        '資料審核狀態',
        max_length=20,
        choices=REVIEW_STATUS,
        default='pending',
        db_index=True,
    )

    coordinate_review_status = models.CharField(
        '座標審核狀態',
        max_length=20,
        choices=COORDINATE_REVIEW_STATUS,
        default='pending',
        db_index=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='最後審核者',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reviewed_collecting_events',
    )

    reviewed_at = models.DateTimeField(
        '最後審核時間',
        null=True,
        blank=True,
    )

    review_notes = models.TextField(
        '內部審核備註',
        blank=True,
    )
    source_identifier = models.CharField('來源列識別碼', max_length=300, unique=True)
    collecting_number = models.CharField('採集號', max_length=120, blank=True, db_index=True)
    collector = models.CharField('採集者', max_length=500, blank=True)
    identified_by = models.CharField('鑑定者', max_length=500, blank=True)
    collection_date_text = models.CharField('採集日期（原始文字）', max_length=100, blank=True)
    locality = models.TextField('採集地', blank=True)
    habitat = models.TextField('生境', blank=True)
    latitude = models.DecimalField('緯度', max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField('經度', max_digits=10, decimal_places=7, null=True, blank=True)
    elevation_m = models.DecimalField('海拔（m）', max_digits=9, decimal_places=2, null=True, blank=True)
    phenology = models.CharField('物候', max_length=120, blank=True)
    life_form = models.CharField('生活型', max_length=120, blank=True)
    quantity_note = models.CharField('份數註記（原始值）', max_length=120, blank=True)
    repository = models.CharField('存放標本館（來源紀錄）', max_length=120, blank=True)
    preserved_in_fluid = models.CharField('浸液註記', max_length=255, blank=True)
    cultivated = models.CharField('種植註記', max_length=120, blank=True)
    vernacular_name_source = models.CharField('中文名（來源紀錄）', max_length=255, blank=True)
    taxon = models.ForeignKey(Taxon, verbose_name='來源分類群', null=True, blank=True, on_delete=models.SET_NULL, related_name='events')
    is_public = models.BooleanField('允許公開顯示', default=False, help_text='匯入資料預設不公開；完成欄位、地點及分類資料檢查後再勾選。')
    source_workbook = models.CharField('來源檔案', max_length=255, default='同步的採集紀錄簿.xlsx')
    source_sheet = models.CharField('來源工作表', max_length=100, default='工作表1')
    source_row = models.PositiveIntegerField('來源列號', null=True, blank=True)
    raw_source = models.JSONField('原始來源欄位', default=dict, blank=True)
    created_at = models.DateTimeField('匯入時間', auto_now_add=True)
    class Meta:
        verbose_name='採集事件／來源紀錄'
        verbose_name_plural='採集事件／來源紀錄'
        ordering=['-collection_date_text','collecting_number']
    def __str__(self): return f'{self.collecting_number or "未編採集號"} — {self.locality[:60]}'

class Specimen(models.Model):
    STATUS=[('pending','待實物確認'),('verified','已確認實物'),('digitised','已數位化'),('deaccessioned','已除藏')]
    collecting_event=models.ForeignKey(CollectingEvent,verbose_name='所屬採集事件',on_delete=models.PROTECT,related_name='specimens')
    barcode=models.CharField('永久 Barcode',max_length=40,unique=True,null=True,blank=True,help_text='僅在實物確認後由管理員手動編配；不可使用採集號代替。')
    physically_verified=models.BooleanField('已確認實體標本存在',default=False)
    status=models.CharField('典藏狀態',max_length=20,choices=STATUS,default='pending')
    preparation_type=models.CharField('標本型態',max_length=100,blank=True,help_text='例如乾燥標本、浸液標本；請依實物填寫。')
    storage_location=models.CharField('館內位置',max_length=255,blank=True)
    public_notes=models.TextField('公開備註',blank=True)
    internal_notes=models.TextField('內部備註',blank=True)
    created_at=models.DateTimeField('建立時間',auto_now_add=True)
    updated_at=models.DateTimeField('更新時間',auto_now=True)
    class Meta:
        verbose_name='實體標本'
        verbose_name_plural='實體標本'
        ordering=['barcode','id']
    def clean(self):
        if self.barcode and not self.physically_verified:
            raise ValidationError({'barcode':'必須先勾選「已確認實體標本存在」，才能編配 Barcode。'})
        if self.barcode and self.status == 'pending':
            raise ValidationError({'status':'已編配 Barcode 的標本不可維持「待實物確認」狀態。'})
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)
    def __str__(self): return self.barcode or f'未編碼標本 #{self.pk or "新建"}'

class Identification(models.Model):
    specimen=models.ForeignKey(Specimen,verbose_name='實體標本',on_delete=models.CASCADE,related_name='identifications')
    taxon=models.ForeignKey(Taxon,verbose_name='鑑定分類群',on_delete=models.PROTECT)
    identified_by=models.CharField('鑑定者',max_length=255,blank=True)
    identified_on=models.DateField('鑑定日期',null=True,blank=True)
    is_current=models.BooleanField('目前有效鑑定',default=True)
    remarks=models.TextField('備註',blank=True)
    original_name=models.CharField('原始鑑定學名',max_length=255,blank=True)
    recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='登錄 Curator',on_delete=models.PROTECT,null=True,blank=True,related_name='recorded_identifications')
    created_at=models.DateTimeField('建立時間',auto_now_add=True)
    updated_at=models.DateTimeField('更新時間',auto_now=True)
    withdrawn_at=models.DateTimeField('撤回時間',null=True,blank=True)
    withdrawal_reason=models.TextField('撤回原因',blank=True)
    class Meta:
        verbose_name='鑑定紀錄'
        verbose_name_plural='鑑定歷史'
        ordering=['-identified_on','-id']
        constraints=[models.UniqueConstraint(fields=['specimen'],condition=Q(is_current=True),name='one_current_identification_per_specimen')]
    def __str__(self): return f'{self.specimen} → {self.taxon}'

class Media(models.Model):
    specimen=models.ForeignKey(Specimen,verbose_name='實體標本',on_delete=models.CASCADE,related_name='media')
    image=models.ImageField('影像檔',upload_to='specimens/%Y/%m/')
    caption=models.CharField('圖說',max_length=500,blank=True)
    credit=models.CharField('影像權利／來源',max_length=255,blank=True)
    is_public=models.BooleanField('公開顯示',default=False)
    created_at=models.DateTimeField('上傳時間',auto_now_add=True)
    class Meta:
        verbose_name='標本影像'
        verbose_name_plural='標本影像'
    def __str__(self): return self.caption or self.image.name


class SiteSettings(models.Model):
    """Single editable public-site configuration, managed by authorised staff."""
    site_title = models.CharField('網站名稱', max_length=160, default='TCF Digital Herbarium')
    site_subtitle = models.CharField('網站副標題', max_length=250, default='Forest Herbarium · National Chung Hsing University')
    hero_title = models.CharField('首頁主標題', max_length=250, default='Documenting plant diversity, one specimen at a time.')
    hero_description = models.TextField('首頁介紹', default='A living archive of botanical collections, research and biodiversity.')
    hero_image = models.ImageField('首頁圖片', upload_to='site/', blank=True)
    hero_image_credit = models.CharField('圖片來源／授權', max_length=300, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = '網站設定'
        verbose_name_plural = '網站設定'
    def __str__(self):
        return self.site_title


class TypeDesignation(models.Model):
    """A nomenclatural type assertion for a *name*, not the current accepted taxon."""
    TYPE_STATUSES = [
        ('holotype','Holotype'), ('isotype','Isotype'),
        ('lectotype','Lectotype'), ('isolectotype','Isolectotype'),
        ('neotype','Neotype'), ('isoneotype','Isoneotype'),
        ('syntype','Syntype'), ('paratype','Paratype'),
        ('epitype','Epitype'), ('isoepitype','Isoepitype'),
        ('other','Other (specify in notes)'),
    ]
    VERIFICATION = [('unverified','Unverified'),('verified','Verified'),('disputed','Disputed')]
    specimen = models.ForeignKey(Specimen, on_delete=models.PROTECT, related_name='type_designations', verbose_name='實體標本')
    type_status = models.CharField('模式類型',max_length=24,choices=TYPE_STATUSES)
    type_name = models.CharField('模式學名（含命名者；保留原文）',max_length=500,help_text='The name typified, NOT necessarily the current POWO accepted name.')
    type_taxon = models.ForeignKey(Taxon,on_delete=models.SET_NULL,null=True,blank=True,related_name='type_designations',verbose_name='對應名稱（可選）')
    original_publication = models.TextField('原始發表文獻',blank=True)
    designation_reference = models.TextField('模式指定文獻',blank=True)
    related_type_barcode = models.CharField('相關模式標本館與條碼',max_length=255,blank=True)
    evidence_url = models.URLField('文獻或證據網址',blank=True)
    verification_status = models.CharField('核實狀態',max_length=20,choices=VERIFICATION,default='unverified')
    verified_by = models.CharField('核實者',max_length=255,blank=True)
    verified_on = models.DateField('核實日期',null=True,blank=True)
    notes = models.TextField('備註與依據',blank=True)
    is_public = models.BooleanField('已核准公開',default=False,help_text='Unverified assertions should normally remain internal until reviewed.')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='recorded_type_designations',verbose_name='登錄 Curator')
    created_at = models.DateTimeField('建立時間',auto_now_add=True)
    updated_at = models.DateTimeField('修改時間',auto_now=True)

    class Meta:
        verbose_name='模式標本指定紀錄'
        verbose_name_plural='模式標本指定紀錄'
        ordering=['specimen_id','type_name','id']

    def clean(self):
        errors={}
        if self.is_public and self.verification_status != 'verified':
            errors['is_public']='僅可公開已核實的模式指定紀錄。'
        if self.verification_status == 'verified' and (not self.verified_by.strip() or not self.verified_on):
            errors['verification_status']='已核實紀錄必須填寫核實者與日期。'
        if errors: raise ValidationError(errors)

    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)

    def __str__(self):
        return f'{self.get_type_status_display()} of {self.type_name} ({self.specimen})'
