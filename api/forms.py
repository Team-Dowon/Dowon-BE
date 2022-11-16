from django import forms
from .models import *

# 폼으로 임시 설정
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'


class ImprovementForm(forms.ModelForm):
    class Meta:
        model = Improvement
        fields = '__all__'


class AnalyzerForm(forms.ModelForm):
    class Meta:
        model = Analyzer
        fields = '__all__'