from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from ..models import User

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(GroupAdmin, UnfoldModelAdmin):
    pass


@admin.register(User)
class UserAdmin(UserAdmin, UnfoldModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    model = User

    ordering = ['date_joined']

    list_display_links = ('id', 'email')

    def get_readonly_fields(self, request, obj = ...):
        readonly_fields = ()
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            readonly_fields = ('role',)
        return readonly_fields

    def get_list_display(self, request):
        list_display = ('id', 'email', 'full_name', 'venue', 'is_active')
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            list_display = ('email', 'full_name', 'role')
        return list_display

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        fieldsets = (
            (None, {"fields": ("email", "password")}),
            (
                "Permissions",
                {
                    "fields": (
                        "is_staff",
                        "is_active",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    )
                },
            ),
            ("Dates", {"fields": ("last_login", "date_joined")}),
            ('required', {
                'fields': ('venue', 'role', 'phone', 'full_name')}),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            fieldsets = (
                (None, {"fields": ("email", "password")}),
                ("Dates", {"fields": ("last_login",)}),
                ('required', {'fields': ('role', 'phone', 'full_name')}),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner' and not change:
            obj.venue = request.user.venue
            obj.is_staff = True
            obj.role = 'admin'
            super().save_model(request, obj, form, change)

            admin_group = Group.objects.get(name='Администратор')
            obj.groups.add(admin_group)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue=request.user.venue)

