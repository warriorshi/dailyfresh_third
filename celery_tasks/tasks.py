from django.conf import settings
from django.core.mail import send_mail
from celery import Celery
import time
#在任务处理者一端加这几句
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","dailyfresh_third.settings")
django.setup()


app = Celery('celery_tasks.tasks',broker='redis://192.168.211.220:6379/8')


@app.task
def send_register_active_email(to_email,username,token):
    '''发送激活邮件'''
    #组织邮件信息
    # 发邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下边的链接激活您的账户' \
                   '<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'\
                   % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)  # 专门有一个关键字参数是html_message#阻塞执行
    time.sleep(5)
