from django.db import models
from django.contrib.auth.hashers import make_password, check_password

GENDER = ((True, '男'), (False, '女'))


# Create your models here.
class User(models.Model):
    username = models.CharField('用户名', max_length=256, null=False)
    hash_password = models.CharField('密码', max_length=256, null=False)
    email = models.EmailField('邮箱', max_length=256, null=False)
    status = models.IntegerField('状态', choices=((1, '未激活'), (2, '激活')), default=1)
    datetime = models.DateTimeField('注册时间', auto_now=True)

    @property
    def password(self):
        raise AttributeError('Can not read password！')

    @password.setter
    def password(self, password):
        self.hash_password = make_password(password, '', 'pbkdf2_sha256')

    def verify_password(self, password):
        return check_password(password, self.hash_password)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name


class Baby(models.Model):
    image = models.ImageField('照片', upload_to='images/baby')
    name = models.CharField('孩子姓名', max_length=256, null=False)
    gender = models.BooleanField('性别', choices=GENDER, max_length=2, default=1)
    birthday = models.DateField('出生日期', null=False)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_gender(self):
        if self.gender:
            return '男'
        return '女'

    class Meta:
        db_table = 'baby'
        verbose_name = '儿童管理'
        verbose_name_plural = verbose_name


class Dependent(models.Model):
    name = models.CharField('姓名', max_length=32, null=False)
    career = models.CharField('职业', max_length=256, null=False)
    phone = models.CharField('手机号', max_length=16, null=False)
    relation = models.CharField('关系', max_length=64, null=False)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'dependert'
        verbose_name = '扶养人管理'
        verbose_name_plural = verbose_name


class Suggest(models.Model):
    content = models.CharField('建议', max_length=1024, null=False)
    baby = models.ForeignKey(Baby, verbose_name='被建议的孩子', on_delete=models.CASCADE)
    date = models.DateTimeField('建议时间', auto_now=True)

    class Meta:
        db_table = 'suggest'
        verbose_name = '建议管理'
        verbose_name_plural = verbose_name


class Activity(models.Model):
    title = models.CharField('活动名称', max_length=256, null=False)
    location = models.CharField('活动地点', max_length=255, null=False)
    datetime = models.DateTimeField('活动时间')
    introduction = models.TextField('活动介绍', null=False)
    principal = models.CharField('负责人', max_length=16, null=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'activate'
        verbose_name = '活动管理'
        verbose_name_plural = verbose_name


class ActivityJion(models.Model):
    centent = models.TextField('反馈内容', null=True)
    activity = models.ForeignKey(Activity, verbose_name='参加活动', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)

    class Meta:
        db_table = 'activityjion'
        verbose_name = '参加活动管理'
        verbose_name_plural = verbose_name


class ActiviteRoom(models.Model):
    image = models.ImageField('活动室图片', upload_to='static/images/activate')
    title = models.CharField('活动室名称', max_length=256, null=False)
    description = models.TextField('活动室描述', null=False)
    principal = models.CharField('负责人', max_length=32, null=False)
    phone = models.CharField('电话', max_length=11, null=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'activiteroom'
        verbose_name = '活动室管理'
        verbose_name_plural = verbose_name
