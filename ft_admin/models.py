# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.base_user import AbstractBaseUser
# from ckeditor.widgets import CKEditorWidget

from datetime import date
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession

from adminsortable.models import SortableMixin, SortableForeignKey

class ContentCategory(SortableMixin):

    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    content = models.ForeignKey('Content', on_delete=models.CASCADE)

    def title(self, obj):
        return obj.content.title

    display_order = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = 'content_category'
        unique_together = (('category', 'content'),)
        ordering = ('display_order', )

        verbose_name_plural = u'콘텐츠 카테고리'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        print 'Content save...'
        super(ContentCategory, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        if hasattr(self, 'content'):
            return self.content.title
        else:
            return 'None'

    #   ProductCategory

class Category(models.Model):

    # id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=32, blank=False, verbose_name=u'카테고리 명')
    is_view = models.BooleanField(default=False, verbose_name=u'표시', help_text=u'메뉴로 표시할지에 대한 여부입니다.')

    # contents = models.ManyToManyField('Content', through='ContentCategory')

    class Meta:
        db_table = 'category'
        verbose_name = u'카테고리 목록'
        verbose_name_plural = u'카테고리 목록'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        print 'save category...'
        return super(Category, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.name


class Content(models.Model):

    # id = models.IntegerField(primary_key=True, db_index=True)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, verbose_name=u'카테고리')
    is_view = models.BooleanField(default=False, verbose_name=u'진열 여부', help_text=u'진열을 체크하지 않으면, 유저에게 노출되지 않습니다.')
    title = models.CharField(max_length=64, null=False, blank=True, default='', db_index=True, verbose_name=u'제목')
    reg_time = models.DateTimeField(u'등록시간')
    mod_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content'
        verbose_name = u'게시글'
        verbose_name_plural = u'게시글 목록'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '/link/%i/' % self.id

    def clean(self):

        print 'Content Clean Method..'

        super(Content, self).clean()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        print 'Content save...'

        super(Content, self).save(force_insert, force_update, using, update_fields)

class ContentDetail(models.Model):

    content = models.OneToOneField('Content', on_delete=models.CASCADE)
    summary_desc = models.TextField(u'요약글', null=False, blank=True, default='')
    detail_desc = RichTextUploadingField(u'본문', null=False, blank=True, default='',
                                         help_text=u'사진 추가 방법은: 사진 -> 업로드 -> 파일 선택 후 -> 서버로 전송 -> 확인')

    '''
    image_01 = models.CharField(u'이미지 1', max_length=256, blank=True, default='')
    image_02 = models.CharField(u'이미지 2', max_length=256, blank=True, default='')
    image_03 = models.CharField(u'이미지 3', max_length=256, blank=True, default='')
    image_04 = models.CharField(u'이미지 4', max_length=256, blank=True, default='')
    '''
    image_01 = models.ImageField(verbose_name=u'썸네일 이미지', upload_to='%Y/%m/%d', null=False, default=None, blank=True)

    class Meta:
        db_table = 'content_detail'
        verbose_name = u'컨텐츠 상세 설명'
        verbose_name_plural = u'컨텐츠 상세 설명'

    # def save(self, *args, **kwargs):
    #     super(Member, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.summary_desc

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        print 'Content save...'

        super(ContentDetail, self).save(force_insert, force_update, using, update_fields)


class Member(models.Model):

    email = models.CharField(max_length=64, db_index=True, verbose_name="이메일 주소")
    job = models.CharField(max_length=32, blank=False, null=False, verbose_name="직업")
    age = models.PositiveSmallIntegerField(blank=False, null=False, verbose_name="나이")
    is_drop_member = models.BooleanField(default=0, verbose_name="탈퇴 여부")
    reg_time = models.DateTimeField(auto_now_add=True, verbose_name="구독 신청일")
    mod_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member"
        verbose_name = u'회원'
        verbose_name_plural = u"회원"
    #
    # def save(self, *args, **kwargs):
    #
    #     super(Member, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.email


