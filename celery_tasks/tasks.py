# 使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail


# 创建一个Celery实例对象
app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/8')

# from kombu import serialization
# serialization.registry._decoders.pop("application/x-python-serialize")
#
# app.conf.update(
#     CELERY_ACCEPT_CONTENT = ['json'],
#     CELERY_TASK_SERIALIZER = 'json',
#     CELERY_RESULT_SERIALIZER = 'json',
# )

# 定义任务函数
@app.task
def send_register_active_mail(email,username,token):
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [email]
    html_message = '<h1>%s,欢迎您成为天天生鲜的注册会员</h1></br>请点击下面的链接完成激活</br><a href ="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)

    send_mail(subject, message, sender, receiver, html_message=html_message)
