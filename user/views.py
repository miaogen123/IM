import _thread
import time
import json
import threading

from django.contrib.auth import login
from django.http import HttpResponse
from django.views import View
from threading import Lock

from .models import Users
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from dwebsocket.decorators import accept_websocket

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
                    request.session['user_id']=user.id
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

class MessageManage(View):
    lock=Lock()
    websocket_dict=dict()
    processingFlag=False
    @classmethod
    def process_message(cls):
        while True:
                for onewb in MessageManage.websocket_dict:
                    try:
                        wb=MessageManage.websocket_dict[onewb]
                        msg=wb.wait()
                        wb.send("nihao")
                        if msg==None:
                            time.sleep(0.2)
                            continue
                        #while wb.has_messages():
                        msg=str(msg,encoding='utf-8')
                        print(msg+" "+str(wb.count_messages()))
                        fields=msg.split(':')
                        if fields[0]!='msg':
                            continue
                        receiver=fields[3]
                        if receiver in MessageManage.websocket_dict:
                            MessageManage.websocket_dict[receiver].send(msg)
                        time.sleep(0.2)
                    except Exception as e:
                        print(e.what)


@accept_websocket
def listenWebsocket_test( request):
    if request.is_websocket():
        msg=request.websocket.wait()
        msg=str(msg,encoding='utf-8')
        fileds=msg.split(':')
        if fileds[0]=="reg":
            userid=fileds[1]
            MessageManage.lock.acquire()
            MessageManage.websocket_dict[userid]=request.websocket
            if MessageManage.processingFlag==False:
#                process=threading.Thread(target=MessageManage.process_message)
#                process.start()
                MessageManage.processingFlag=True
            MessageManage.lock.release()
        elif fileds[0]=="msg":
            receiver=fileds[3]
            if receiver not in MessageManage.websocket_dict:
                request.websocket.send("error:no such receiver")
            else:
                MessageManage.websocket_dict[receiver].send(msg)
        wb=request.websocket
        while True:
            msg=wb.read()
            if msg==None:
                time.sleep(0.2)
                continue
            msg=str(msg,encoding='utf-8')
            print(msg+" "+str(wb.count_messages()))
            fields=msg.split(':')
            if fields[0]!='msg':
                continue
            receiver=fields[3]
            if receiver in MessageManage.websocket_dict:
                MessageManage.websocket_dict[receiver].send(msg)
