from django.contrib import admin
from django.contrib import messages
from .models import User, Question, Answer, Config
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
)
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _
import json
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


# Register your models here.
class MyAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        try:
            target_config = Config.objects.get_or_create(key="target_location")[0]
            target_location = json.loads(target_config.value)
            lat = target_location.get('lat', '0.0')
            lng = target_location.get('lng', '0.0')
        except Exception:
            lat = '0.0'
            lng = '0.0'

        extra_context["target_lat"] = lat
        extra_context["target_lng"] = lng
        return super().index(request, extra_context)


my_admin_site = MyAdminSite(name="myadmin")
my_admin_site.site_header = "Standom Administration"
my_admin_site.site_title = "Standom Admin"
my_admin_site.index_title = "Standom Administration"

class AnswerInline(admin.TabularInline):
    model = Answer

    def save_model(self, request, obj, form, change):
        print("=== save answer inline " + str(obj.id))
        super().save_model(request, obj, form, change)


class UserMyAdmin(admin.ModelAdmin):

    inlines = [
        AnswerInline,
    ]
    change_user_password_template = None
    add_form_template = None
    fieldsets = (
        (None, {'fields': ('name', 'email', 'avatar', 'score')}),
    )
    readonly_fields = ('score', )
    list_display = ('email', 'name', 'avatar', 'score', 'is_staff')
    list_filter = ('is_staff',)
    search_fields = ('email', 'name',)
    change_password_form = AdminPasswordChangeForm
    current_obj = None

    def save_model(self, request, obj, form, change):
        obj.username = obj.email
        super().save_model(request, obj, form, change)
        self.current_obj = obj

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        print("=======Save realted")
        if self.current_obj:
            self.current_obj.update_score()
            self.current_obj.save()
        self.current_obj = None

    def get_urls(self):
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
            path('set_location/', self.admin_site.admin_view(self.set_location), name='set_location',)
        ] + super().get_urls()

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     extra_context['questions'] = self.get_dynamic_info()
    #     return super(UserMyAdmin, self).change_view(
    #         request, object_id, form_url, extra_context=extra_context,
    #     )

    def set_location(self, request):
        if request.method == 'POST':
            target_config = Config.objects.get_or_create(key="target_location")[0]
            lat = request.POST.get('lat', '0.0')
            lng = request.POST.get('lng', '0.0')
            target_config.value = "{\"lat\": %s ,\"lng\": %s}" % (lat, lng)
            target_config.save()

            messages.add_message(request, messages.INFO, 'SetLocation successfully')
            return HttpResponseRedirect(
                   '/admin/'
                )


    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
            IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )


my_admin_site.register(User, UserMyAdmin)
my_admin_site.register(Question)
# admin.site.register(Answer)
# my_admin_site.unregister(Group)
