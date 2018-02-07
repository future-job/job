# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from .models import Category, Content, Member, ContentCategory, ContentDetail
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline, SortableAdmin

class CategoryAdmin(admin.TabularInline):
    model = Category

class CategoryForm(forms.ModelForm):
    def clean(self):
        super(CategoryForm, self).clean()

class ContentCategoryInlineForOrdering(SortableTabularInline):
    model = ContentCategory
    extra = 0

    fields = ('category_id', 'view_content', 'summary_desc', 'is_view',)
    readonly_fields = ('category_id','view_content', 'summary_desc', 'is_view',)

    def category_id(self, obj):
        print obj.content
        return obj.content.category_id

    def view_content(self, obj):
        data = '<a href="/admin/ft_admin/content/%s/change/">%s</a>' % (obj.content.id, obj.content.title)
        return data

    view_content.short_description = u'콘텐츠 제목'
    view_content.allow_tags = True

    def has_add_permission(self, request):
        return False

    def summary_desc(self, obj):
        print obj.content
        return obj.content.summary_desc

    summary_desc.short_description = u'요약본'

    def is_view(self, obj):
        return 'O' if obj.content.is_view else 'X'

    is_view.short_description = u'노출 여부'


class CategoryAdmin(NonSortableParentAdmin):
    form = CategoryForm
    fields = ('id', 'name', 'is_view',)
    readonly_fields = ('id',)
    list_display = ('id', 'name', 'is_view', 'content_count')
    list_display_links = ('name',)
    # list_filter = ('type', 'parent_category',)  # CategoryParentFilter
    inlines = (ContentCategoryInlineForOrdering,)

    def content_count(self, obj):

        print obj, obj.id
        print ContentCategory.objects.all().values()
        return str(ContentCategory.objects.filter(category=obj.id).count())

    content_count.short_description = u'컨텐츠 수'

    # def save_model(self, request, obj, form, change):
    #     print 'CategoryAdmin - save_model'
    #     super(CategoryAdmin, self).save_model(request, obj, form, change)

    # def has_add_permission(self, request):
    #     # if '/mall/admin/libs/category/add/' == request.path:
    #     #     return False
    #
    #     popup = int(request.GET.get('_popup', 0))
    #     if popup == 1:
    #         return False
    #
    #     return True

    # class Media:
    #     css = {'all': ('css/no-addanother-button.css', 'css/category_add.css',)}


class ContentDetailInline(admin.StackedInline):
    model = ContentDetail
    # form = ProductDetailForm
    can_delete = False

    fields = (
        'summary_desc',
        'detail_desc',
        ('image_01', 'preview_img_01'),
    )
    readonly_fields = ('preview_img_01',)

    def preview_img_01(self, obj):
        if obj.image_01:
            print obj.image_01
            return u'<img style="max-width: 100px;" src="/future/upload/{}" />'.format(obj.image_01)
        else:
            return u'None Image'

    preview_img_01.allow_tags = True
    preview_img_01.short_description = u'썸네일'

class ContentCategoryInline(admin.TabularInline):
    model = ContentCategory
    extra = 0
    exclude = ('display_order',)

    def get_fields(self, request, obj=None):
        return super(ContentCategoryInline, self).get_fields(request, obj)


# 상품 Admin
class ContentAdmin(admin.ModelAdmin):
    list_per_page = 15

    #   목록 화면 설정 옵션들
    list_display = ('id', 'display_order', 'title', 'reg_time', 'good_job', 'is_view',)
    list_filter = ('is_view',)
    search_fields = ('title', )
    list_display_links = ('display_order', 'title',)

    #   자세히보기 화면 설정 옵션들
    readonly_fields = ('id',)
    fieldsets = (
        # (('상품 정보'), {
        (None, {
            'fields': (
                'id',
                'good_job',
                # 'category',
                'is_view',
                'title',
                'display_order',
                'hit_count',
                # 'summary_desc',
                # 'detail_desc',
                # 'image_01',
                'reg_time',
                # 'image_02',
            ),
        }),
    )
    inlines = (ContentCategoryInline, ContentDetailInline, )

class MemberAdmin(admin.ModelAdmin):
    list_per_page = 15

    #   목록 화면 설정 옵션들
    list_display = ('email', 'age', 'job', 'reg_time',)
    list_filter = ('age',)
    search_fields = ('email',)

admin.site.register(Content, ContentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Member, MemberAdmin)

