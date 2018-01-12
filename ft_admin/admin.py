# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import ContentCategory
from .models import Category
from .models import Content
from .models import Post
from adminsortable.admin import NonSortableParentAdmin, SortableAdmin  # , SortableStackedInline,

# from .models import ContentDetail

# Register your models here.

# class CategoryAdmin(NonSortableParentAdmin):
#     fields = ('id', 'name', 'is_view', )
#     readonly_fields = ('id',)
#     list_display = ('id', 'name', 'is_view')
#     list_display_links = ('name',)
#     # list_filter = ('type', 'parent_category',)  # CategoryParentFilter
#     inlines = (ProductCategoryInlineForOrdering,)
#
#     def product_count(self, obj):
#         return str(ProductCategory.objects.filter(category=obj.id).count())
#
#     product_count.short_description = u'상품 수'
#
#     def save_related(self, request, form, formsets, change):
#         print 'Category Admin - save_related : start'
#         super(CategoryAdmin, self).save_related(request, form, formsets, change)
#
#     def save_model(self, request, obj, form, change):
#         print 'CategoryAdmin - save_model'
#         super(CategoryAdmin, self).save_model(request, obj, form, change)
#
#     def has_add_permission(self, request):
#         # if '/mall/admin/libs/category/add/' == request.path:
#         #     return False
#
#         popup = int(request.GET.get('_popup', 0))
#         if popup == 1:
#             return False
#
#         return True
#
#     class Media:
#         css = {'all': ('css/no-addanother-button.css', 'css/category_add.css',)}
#
# class ProductCategoryInlineForOrdering(SortableTabularInline):
#     model = ProductCategory
#     extra = 0
#
#     fields = ('view_product', 'current_product_price', 'current_product_view', 'current_product_sell',
#                 'current_product_npay_sell')
#     readonly_fields = ('view_product', 'current_product_price', 'current_product_view', 'current_product_sell',
#                          'current_product_npay_sell')
#
#     def view_product(self, obj):
#         data = '<a href="/mall/admin/libs/product/%s/change/">%s</a>' % (obj.product.id, obj.product.name)
#         return data
#
#     view_product.short_description = u'상품명'
#     view_product.allow_tags = True
#
#     def has_add_permission(self, request):
#         return False
#
#     def current_product_view(self, obj):
#         return 'O' if obj.product.is_view else 'X'
#
#         current_product_view.short_description = u'진열 여부'
#
#         def current_product_sell(self, obj):
#             return 'O' if obj.product.is_sell else 'X'
#
#         current_product_sell.short_description = u'판매 여부'
#
#         def current_product_npay_sell(self, obj):
#             return 'O' if obj.product.is_npay_sell else 'X'
#
#         current_product_npay_sell.short_description = u'네이버 판매 여부'


# 상품 Admin
class ContentAdmin(admin.ModelAdmin):
    list_per_page = 15

    #   목록 화면 설정 옵션들
    list_display = ('id', 'title', 'summary_desc', 'reg_time', 'is_view',)
    list_filter = ('is_view',)
    search_fields = ('title', )
    list_display_links = ('id', 'title', 'summary_desc',)

    #   자세히보기 화면 설정 옵션들
    readonly_fields = ('id',)
    fieldsets = (
        # (('상품 정보'), {
        (None, {
            'fields': (
                'id',
                'is_view',
                'title',
                'summary_desc',
                'detail_desc',
                'image_01',
                'reg_time',
                # 'image_02',
            ),
        }),
    )

    # def thumbnails(self, obj):
    #     pd = Content.objects.get(obj.id)
    #     if pd and pd.image_01:
    #         return u'<div onclick="location.href = \'/mall/admin/libs/product/{}/change/\';" style="width: 100px; height: 64px; text-align: center;"><img style="max-width: 100px; max-height: 64px; height: 64px;" src="/mall/upload/{}" /></div>'.format(
    #             obj.id, pd.image_01)
    #     else:
    #         return u'<div onclick="location.href = \'/mall/admin/libs/product/{}/change/\';" style="width: 100px; height: 64px; text-align: center; line-height: 64px;">None Image</div>'.format(
    #             obj.id, )
    #
    # thumbnails.allow_tags = True
    # thumbnails.short_description = u'썸네일'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super(ContentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super(ContentAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super(ContentAdmin, self).change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        return super(ContentAdmin, self).add_view(request, form_url, extra_context)

    def get_fields(self, request, obj=None):
        return super(ContentAdmin, self).get_fields(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        return super(ContentAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(ContentCategory)
admin.site.register(Content, ContentAdmin)
# admin.site.register(ContentDetail)
admin.site.register(Category)
admin.site.register(Post)

