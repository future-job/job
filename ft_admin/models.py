# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
# from ckeditor.widgets import CKEditorWidget

from adminsortable.models import SortableMixin, SortableForeignKey

class Post(models.Model):
    author = models.ForeignKey('auth.User') #다른 모델에 대한 링크
    title = models.CharField(max_length=200) #글자수 제한된 텍스트
    created_date = models.DateTimeField(default=timezone.now) #날짜와 시간
    published_date = models.DateTimeField(blank=True, null=True)
    text = models.CharField(max_length=200, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self): #Post 모델의 title 반환
        return self.title


class Category(models.Model):

    MAIN_CATEGORY = 0
    MIDDLE_CATEGORY = 1
    SMALL_CATEGORY = 2
    DETAIL_CATEGORY = 3

    CATEGORY_TYPES = (
        (MAIN_CATEGORY, u'대분류'),
        (MIDDLE_CATEGORY, u'중분류'),
        (SMALL_CATEGORY, u'소분류'),
        (DETAIL_CATEGORY, u'상세분류'),
    )
    name = models.CharField(max_length=32, blank=True, verbose_name=u'카테고리 명')
    type = models.SmallIntegerField(default=0, choices=CATEGORY_TYPES, verbose_name=u'분류')
    parent_category = models.ForeignKey('Category', verbose_name=u'상위 카테고리', null=True, on_delete=models.CASCADE, default=None, blank=True)
    is_view = models.BooleanField(default=False, verbose_name=u'표시', help_text=u'메뉴로 표시할지에 대한 여부입니다.')
    # is_deprecated = models.BooleanField(default=False)
    #banner = models.CharField(max_length=128, verbose_name=u'이미지 배너', null=True, default=None)
    # banner = models.ImageField(verbose_name=u'카테고리 배너', upload_to='%Y/%m/%d', null=True, blank=True, default=None, help_text=u'해당 카테고리의 상품 리스트 화면에서 보여질 상단의 배너입니다.(PC)')
    # m_banner = models.ImageField(verbose_name=u'모바일 카테고리 배너', upload_to='%Y/%m/%d', null=True, blank=True, default=None, help_text=u'해당 카테고리의 상품 리스트 화면에서 보여질 상단의 배너입니다.(모바일)')

    #   TEST
    # products = models.ManyToManyField('Content', through='Categories')

    class Meta:
        db_table = 'category'
        verbose_name = u'카테고리 목록'
        verbose_name_plural = u'카테고리 목록'

    def __unicode__(self):
        #print u' ({})'.format(self.CATEGORY_TYPES[self.type][1])
        return self.name + u' ({})'.format(self.CATEGORY_TYPES[self.type][1])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        print 'save category...'
        return super(Category, self).save(force_insert, force_update, using, update_fields)

    #retreive direct childs
    def get_child_categories(self):
        childlist = Category.objects.filter(parent_category=self)
        return childlist

    #retreive all products recursively in this category
    def get_products_of(self):
        child_categories = self.get_child_categories()
        productlist = []
        for c in child_categories:
            temp = c.get_products_of()
            for p in temp:
                if p not in productlist:
                    productlist.append(p)

        temp = Categories.objects.filter(category=self)
        for p in temp:
            if p.product not in productlist:
                productlist.append(p.product)

        return productlist

    def __unicode__(self):
        return self.name

class ContentCategory(SortableMixin):

    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    content = models.ForeignKey('Content', on_delete=models.CASCADE)

    display_order = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = 'content_category'
        unique_together = (('category', 'content'),)
        ordering = ('display_order', )

        verbose_name_plural = u'카테고리 & 콘텐츠'

    def __unicode__(self):
        if hasattr(self, 'content'):
            return self.content.title
        else:
            return 'None'

class DisplayCategoryInfo(models.Model):

    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=256)

    category = models.OneToOneField('Category', on_delete=models.CASCADE)

    class Meta:
        db_table = 'display_category_info'



class Content(models.Model):
    is_view = models.BooleanField(default=False, verbose_name=u'진열 여부', help_text=u'진열을 체크하지 않으면, 유저에게 노출되지 않습니다.')


    title = models.CharField(max_length=64, blank=True, default='', db_index=True, verbose_name=u'제목')

    reg_time = models.DateTimeField(u'등록시간')
    # reg_time = models.DateTimeField(auto_now_add=True)
    mod_time = models.DateTimeField(auto_now=True)

    summary_desc = models.TextField(u'요약글', blank=True, default='')
    detail_desc = RichTextUploadingField(u'본문', blank=True, default='',
                                         help_text=u'사진 추가 방법은: 사진 -> 업로드 -> 파일 선택 후 -> 서버로 전송 -> 확인')

    '''
    image_01 = models.CharField(u'이미지 1', max_length=256, blank=True, default='')
    image_02 = models.CharField(u'이미지 2', max_length=256, blank=True, default='')
    image_03 = models.CharField(u'이미지 3', max_length=256, blank=True, default='')
    image_04 = models.CharField(u'이미지 4', max_length=256, blank=True, default='')
    '''
    image_01 = models.ImageField(verbose_name=u'썸네일 이미지', upload_to='%Y/%m/%d', null=True, default=None, blank=True)
    # image_02 = models.ImageField(verbose_name=u'목록 이미지', upload_to='%Y/%m/%d', null=True, blank=True, default=None)
    # image_03 = models.ImageField(verbose_name=u'작은목록 이미지', upload_to='%Y/%m/%d', null=True, blank=True, default=None)
    # image_04 = models.ImageField(verbose_name=u'축소 이미지', upload_to='%Y/%m/%d', null=True, blank=True, default=None)


    class Meta:
        db_table = 'content'
        verbose_name = u'게시글'
        verbose_name_plural = u'게시글 목록'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/link/%i/' % self.id

    # def get_delivery_period(self):
    #     if self.delivery_period != '' and self.delivery_period != None:
    #         return self.delivery_period.replace('|', '~')
    #     else:
    #         return 'unknown'

    def clean(self):

        print 'Content Clean Method..'
        #print self.name
        #print self.price

        super(Content, self).clean()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        print 'Content save...'

        super(Content, self).save(force_insert, force_update, using, update_fields)

    #   Product End

# class ContentDetail(models.Model):
#
#     content = models.OneToOneField('Content', on_delete=models.CASCADE)
#
#
#
#     class Meta:
#         db_table = 'content_detail'
#         verbose_name = u'상품 상세 설명'
#         verbose_name_plural = u'상품 상세 설명'

    #   ProductDetail End