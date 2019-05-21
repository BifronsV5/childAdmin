from xadmin import views
from .models import User, Baby, Dependent, Suggest, Activity, ActivityJion, ActiviteRoom
import xadmin


# Register your models here.
class ChildSetting(object):
    site_title = '社区儿童成长跟踪系统'
    site_footer = '社区儿童成长跟踪系统'


class UserAdmin(object):
    list_display = ['username', 'hash_password', 'email', 'status', 'datetime']


class BabyAdmin(object):
    list_display = ['image', 'name', 'gender', 'birthday', 'user']


class DependentAdmin(object):
    list_display = ['name', 'career', 'phone', 'relation', 'user']


class SuggestAdmin(object):
    list_display = ['content', 'baby', 'date']


class ActivityAdmin(object):
    list_display = ['title', 'location', 'datetime','introduction', 'principal']


class ActivityJionAdmin(object):
    list_display = ['centent', 'activity', 'user']


class ActivityRoomAdmin(object):
    list_display = ['image', 'title', 'description', 'principal', 'phone']


xadmin.site.register(views.CommAdminView, ChildSetting)
xadmin.site.register(User, UserAdmin)
xadmin.site.register(Baby, BabyAdmin)
xadmin.site.register(Dependent, DependentAdmin)
xadmin.site.register(Suggest, SuggestAdmin)
xadmin.site.register(Activity, ActivityAdmin)
xadmin.site.register(ActivityJion, ActivityJionAdmin)
xadmin.site.register(ActiviteRoom, ActivityRoomAdmin)
