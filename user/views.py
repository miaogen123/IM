import json

from django.contrib.auth import login
from django.forms import forms
from django.http import HttpResponse
from django.shortcuts import render
from .models import Users
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
class UserForm(UserCreationForm):
    #username = forms.CharField(label='user_name',max_length=50)
    #password = forms.CharField(label='passwrod',widget=forms.PasswordInput())
    class Meta(UserCreationForm.Meta):
        model = Users
        fields = ("username",)

@csrf_exempt
def Register(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        # 验证数据的合法性
        if form.is_valid():
            # 如果提交数据合法，调用表单的 save 方法将用户数据保存到数据库
            form.save()
            return HttpResponse(json.dumps({'status':'OK', 'msg':'success'}),content_type='application/json')
        else:
            return HttpResponse(json.dumps({'status':'failed', 'msg':'form is invalid'}),content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status':'failed', 'msg':'get not support'}),content_type='application/json')


@csrf_exempt
def Login(request):
    if request.method=='POST':
        username=request.POST.get('username', '')
        password=request.POST.get('password', '')
        if username and password:
            try:
                user=Users.objects.get(username=username)
                if user.check_password(password):
                    login(request, user)
                    return HttpResponse(json.dumps({'status':'OK', 'msg':'success'}),content_type='application/json')
                else:
                    return HttpResponse(json.dumps({'status':'failed', 'msg':'password not correct'}),content_type='application/json')
            except Users.DoesNotExist:
                return HttpResponse(json.dumps({'status':'failed', 'msg':'users not found'}),content_type='application/json')


@csrf_exempt
def Search(request):
    if request.method=='GET':
        username=request.GET.get('username', '')
        user_list=[]
        filter_set=None
        if username:
            filter_set=Users.objects.filter(username__contains=username)
        else:
            id=request.GET.get('ID')
            filter_set=Users.objects.filter(id__contains=id)
        for oneUser in filter_set:
            user_list.append((oneUser.id, oneUser.username))
        return HttpResponse(json.dumps(user_list),content_type='application/json')



