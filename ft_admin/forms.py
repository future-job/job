# -*- coding: utf-8 -*-

from __future__ import absolute_import
from ckeditor.fields import RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingField
from django import forms  # forms 모델을 import
# from .models import Post  # Post모델 임포트

# class PostForm(forms.ModelForm):  # 우리가 만들 폼의 이름, 그리고 이 폼은 `ModelForm`이란걸 알려주면 장고가 이것저것 해준다.
#     class Meta:
#         model = Post  # 이 폼을 만들기 위해 어떤 모델이 쓰여야 하는지
#         fields = ('title', 'text')  # 필드를 넣는다.


class CkEditorForm(forms.Form):
    content = RichTextFormField()