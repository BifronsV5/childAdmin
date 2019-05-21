from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import User, Baby, Dependent, Suggest, Activity, ActivityJion, ActiviteRoom
from django.core.mail import send_mail
from django.conf import settings
import time
import jwt
import re


def message(message):
    return {'message': message}


def verify_bearer_token(token):
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = User.objects.get(username=payload['sub'])
        user.status = 2
        user.save()
        return True
    except BaseException as e:
        return False


def verifytoken(token):
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return True, payload
    except BaseException as e:
        return False, payload


def get_pages(totalpage=1, current_page=1):
    WEB_DISPLAY_PAGE = 8
    front_offset = int(WEB_DISPLAY_PAGE / 2)
    if WEB_DISPLAY_PAGE % 2 == 1:
        behind_offset = front_offset
    else:
        behind_offset = front_offset - 1
    if totalpage < WEB_DISPLAY_PAGE:
        return list(range(1, totalpage + 1))
    elif current_page <= front_offset:
        return list(range(1, WEB_DISPLAY_PAGE + 1))
    elif current_page >= totalpage - behind_offset:
        start_page = totalpage - WEB_DISPLAY_PAGE + 1
        return list(range(start_page, totalpage + 1))
    else:
        start_page = current_page - front_offset
        end_page = current_page + behind_offset
        return list(range(start_page, end_page + 1))


def gender(sex):
    if sex == "男":
        return True
    return False


# Create your views here.
# 首页
@require_http_methods('GET')
def index(request):
    activity = Activity.objects.all().order_by('-datetime')[0:7]
    return render(request, 'index.html', locals())


# 登录
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == '' or password == '':
            return render(request, 'login.html', message('密码用户名不能为空!!!'))
        user = User.objects.filter(username=username)
        if len(user) == 0:
            return render(request, 'login.html', message('用户名不存在!!!'))
        if not user[0].verify_password(password):
            return render(request, 'login.html', message('密码错误!!!'))
        if user[0].status == 1:
            return render(request, 'login.html', message('用户未激活!!!'))
        request.session['user_id'] = user[0].id
        request.session['username'] = username
        return redirect('/')


# 注册
@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if username == '' or password == '' or email == '':
            return render(request, 'register.html', message('用户名、密码、邮箱不能为空!!!'))
        if re.match('^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$', email) is None:
            return render(request, 'register.html', message('邮箱格式错误!!!'))
        user = User.objects.filter(email=email)
        if len(user) == 1:
            return render(request, 'register.html', message('邮箱已存在!!!'))
        user = User.objects.filter(username=username)
        if len(user) == 1:
            return render(request, 'register.html', message('用户名已存在!!!'))
        user = User(username=username, password=password, email=email)
        user.save()
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + 5 * 60,
            'sub': username
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        send_mail('验证信息', '请点击验证http://{}/verification?token={}'.format(request.get_host(), token.decode()),
                  settings.EMAIL_HOST_USER,
                  ['{}'.format(User.objects.get(username=username).email)], fail_silently=False)
        return redirect('/login/')


# 退出
@require_http_methods('GET')
def quit_(request):
    if 'username' in request.session:
        del request.session['username']
        del request.session['user_id']
    return redirect('/')


# 修改密码验证
@require_http_methods('GET')
def token_password(request):
    if 'username' in request.session:
        user = User.objects.get(id=request.session.get('user_id'))
        if request.GET.get('ok') == '1':
            payload = {
                "iat": int(time.time()),
                "exp": int(time.time()) + 5 * 60,
                'sub': user.username
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            send_mail('验证信息', '请点击验证http://{}/psw_token?token={}'.format(request.get_host(), token.decode()),
                      settings.EMAIL_HOST_USER,
                      ['{}'.format(user.email)], fail_silently=False)
            return render(request, 'tokenpassword.html', message('发送成功!!'))
        return render(request, 'tokenpassword.html', locals())
    return redirect('/login/')


# 修改密码
@require_http_methods(['GET', 'POST'])
def psw_token(request):
    if 'username' in request.session:
        if request.method == 'GET':
            if verify_bearer_token(request.GET.get('token')):
                return render(request, 'psw_token.html')
            return render(request, 'tokenpassword.html', message('验证失败!!'))
        if request.method == 'POST':
            user = User.objects.get(id=request.session.get('user_id'))
            user.password = request.POST.get('password')
            user.save()
            return redirect('/login/')
    return redirect('/login/')


# 忘记密码
@require_http_methods(['GET', 'POST'])
def forget(request):
    if request.method == 'GET':
        return render(request, 'forget.html')
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email)
        if len(user) == 0:
            return render(request, 'forget.html', message('邮箱不存在!!'))
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + 5 * 60,
            "sub": email
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        send_mail('验证信息', '请点击验证http://{}/forget_token?token={}'.format(request.get_host(), token.decode()),
                  settings.EMAIL_HOST_USER, ['{}'.format(email)], fail_silently=False)
        return render(request, 'forget.html', message('发送成功!!'))


# 验证
@require_http_methods(['GET', 'POST'])
def forget_token(request):
    if request.method == 'GET':
        token = request.GET.get('token')
        bool_, payload = verifytoken(token)
        if bool_:
            return render(request, 'forget_token.html', locals())
        return render(request, 'forget.html', message('验证失败!!'))
    if request.method == 'POST':
        user = User.objects.get(email=request.POST.get('email'))
        user.password = request.POST.get('password')
        user.save()
        return HttpResponse('修改成功')


# 个人中心
@require_http_methods('GET')
def personal(request):
    if 'username' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        try:
            baby = Baby.objects.filter(user_id=user.id)[0]
        except BaseException:
            baby = None
        dependent = Dependent.objects.filter(user_id=user.id)
        dependent_len = len(dependent)
        activityjion = ActivityJion.objects.filter(user_id=user.id)
        paginator = Paginator(activityjion, 5)
        page = request.GET.get('page', 1)
        pagi = paginator.page(page)
        total_page_number = paginator.num_pages
        page_list = get_pages(int(total_page_number), int(page))
        suggest = Suggest.objects.filter(baby__user_id=user.id)
        paginator_ = Paginator(suggest, 5)
        page_ = request.GET.get('page_', 1)
        pagi_ = paginator_.page(page_)
        total_page_number_ = paginator_.num_pages
        page_list_ = get_pages(int(total_page_number_), int(page_))
        return render(request, 'personal.html', locals())
    return redirect('/login/')


# 增加孩子信息
@require_http_methods('POST')
def addchild(request):
    if 'username' in request.session:
        image = request.FILES.get('image')
        name = request.POST.get('name')
        sexuality = request.POST.get('sexuality')
        birthday = request.POST.get('birthday')
        baby = Baby.objects.filter(user_id=request.session.get('user_id'))
        if image is None or name == '' or sexuality == '' or birthday == '':
            return HttpResponse('提交不可以为空!!!')
        if len(baby) == 0:
            Baby(image=image, name=name, gender=gender(sexuality), birthday=birthday,
                 user_id=request.session['user_id']).save()
            return HttpResponse('成功')
        return HttpResponse('异常')
    return HttpResponse('请去登录')


# 修改孩子信息
@require_http_methods('POST')
def modifychild(request):
    if 'username' in request.session:
        image = request.FILES.get('image')
        name = request.POST.get('name')
        sexuality = request.POST.get('sexuality')
        birthday = request.POST.get('birthday')
        print(request.POST.get('childid'))
        child = Baby.objects.get(id=request.POST.get('childid'))
        if image is not None:
            child.image = image
        if name != '':
            child.name = name
        if birthday != '':
            child.birthday = birthday
        child.gender = gender(sexuality)
        child.save()
        return HttpResponse('修改成功')
    return HttpResponse('请去登录')


# 增加抚养人信息
@require_http_methods('POST')
def add_dependent(request):
    if 'username' in request.session:
        name = request.POST.get('name')
        career = request.POST.get('career')
        phone = request.POST.get('phone')
        relation = request.POST.get('relation')
        if name == '' or career == '' or phone == '' or relation == '':
            return HttpResponse('提交不可以为空!!!')
        if re.match(r'^[1][3-9][0-9]{9}$', phone):
            return HttpResponse('手机号格式错误!!!')
        Dependent(name=name, career=career, phone=phone, relation=relation, user_id=request.session.get('user_id')).save()
        return HttpResponse('成功')
    return HttpResponse('请去登录')


# 修改扶养人信息
@require_http_methods('POST')
def modify_dependent(request):
    if 'username' in request.session:
        dependent = Dependent.objects.get(id=request.POST.get('id'))
        name = request.POST.get('name')
        career = request.POST.get('career')
        phone = request.POST.get('phone')
        relation = request.POST.get('relation')
        if name != '':
            dependent.name = name
        if career != '':
            dependent.career = career
        if phone != '':
            if re.match(r'^[1][3-9][0-9]{9}$', phone) is None:
                return HttpResponse('手机号格式错误!!!')
            dependent.phone = phone
        if relation != '':
            dependent.relation = relation
        dependent.save()
        return HttpResponse('修改成功')
    return HttpResponse('请去登录')


# 反馈活动信息
@require_http_methods('POST')
def feedback(request):
    activityjion = ActivityJion.objects.get(id=request.POST.get('id'))
    activityjion.centent = request.POST.get('feedback')
    activityjion.save()
    return HttpResponse('反馈成功')


# 验证
@require_http_methods('GET')
def verification(request):
    if verify_bearer_token(request.GET.get('token')):
        return redirect('/login/')


# 社区活动
@require_http_methods('GET')
def community(request):
    if 'username' in request.session:
        id = request.GET.get('communityid', None)
        if id:
            activity = Activity.objects.get(id=id)
            activityjion = len(ActivityJion.objects.filter(user_id=request.session.get('user_id'), activity_id=id))
            return render(request, 'communityinfo.html', locals())
        activity = Activity.objects.all()
        paginator = Paginator(activity, 15)
        page = request.GET.get('page', 1)
        pagi = paginator.page(page)
        total_page_number = paginator.num_pages
        page_list = get_pages(int(total_page_number), int(page))
        return render(request, 'community.html', locals())
    return redirect('/login/')


# 参加社区活动
@require_http_methods('POST')
def join_activite(request):
    if 'username' in request.session:
        id = request.POST.get('id')
        ActivityJion(activity_id=id, user_id=request.session.get('user_id')).save()
        return HttpResponse('参加成功')
    return HttpResponse('请去登录!!')


# 社区活动室
@require_http_methods('GET')
def activiteroom(request):
    id = request.GET.get('activiteid', None)
    if id:
        activiteroom_ = ActiviteRoom.objects.get(id=id)
        return render(request, 'activateinfo.html', locals())
    activiteroom_ = ActiviteRoom.objects.all()
    return render(request, 'activiteroom.html', locals())


# 系统介绍
@require_http_methods('GET')
def introduction(request):
    return render(request, 'introduction.html')
