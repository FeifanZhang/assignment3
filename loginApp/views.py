from django.shortcuts import render
from django.shortcuts import redirect
from loginApp.models import *
# Create your views here.

def login(request):
    print("inter the method called login")
    #首次请求
    if (type(request.POST.get('username')) != str or type(request.POST.get('password')) != str):
        print("inter the first if:username or password is null")
        return render(request, 'loginpage.html')
    #重复的请求
    if (request.POST.get('username') == ''):
        return render(request, 'loginpage.html', {"message": "用户名不能为空"})
    if(request.POST.get('password')==''):
        return render(request, 'loginpage.html',{"message":"密码不能为空"})
    if(User.objects.filter(username=request.POST.get('username'),password=request.POST.get('password')).count()!=0):
        username = request.POST.get('username')
        print(request.POST.get('username'))
        print(request.POST.get('password'))

        request = redirect('/searchApp/index/')

        request.set_cookie('username', username)
        return request
    return render(request,'loginpage.html',{"message":"用户名或密码输入错误"})

def register(request):
    print("inter the method called register")
    print(User.objects.filter(username=request.POST.get('username')).count())
    print(User.objects.filter(username=request.POST.get('password')).count())
    if (request.POST.get('username') == None):
        return render(request, 'registerpage.htmlpage', {"message": "用户名不能为空"})
    if (request.POST.get('password') == None):
        return render(request, 'registerpage.html', {"message": "密码不能为空"})
    if (User.objects.filter(username=request.POST.get('username')).count()!=0):
        return render(request, 'registerpage.html', {"message": "该用户已存在"})
    if (User.objects.filter(password=request.POST.get('password')).count()!=0):
        return render(request, 'registerpage.html', {"message": "该密码已被使用"})
    user=User.objects.create(username=request.POST.get('username'),password =request.POST.get('password'))
    print('saved the data in the database ')
    username = request.POST.get('username')
    request= redirect('/searchApp/index/')

    request.set_cookie('username',username)
    return request

def registerpage(request):
    print("inter the method called registerpage")
    return render(request,"registerpage.html")

def returnToLoginpage(request):
    return redirect('/loginApp/login/')
