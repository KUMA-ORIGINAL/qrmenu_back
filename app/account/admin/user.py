from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from venues.models import Spot
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
    autocomplete_fields = ("groups",)

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
            list_display = ('email', 'full_name', 'role', 'spot')
        return list_display

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        fieldsets = (
            (None, {"fields": ("email", "password")}),
            (
                "Права",
                {
                    "fields": (
                        "is_staff",
                        "is_active",
                        "is_superuser",
                        "groups",
                    )
                },
            ),
            ("Даты", {"fields": ("last_login", "date_joined")}),
            (None, {
                'fields': ('venue', 'spot', 'role', 'phone_number', 'full_name', 'tg_chat_id')}),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role == 'owner':
            fieldsets = (
                (None, {"fields": ("email", "password")}),
                ("Dates", {"fields": ("last_login",)}),
                ('required', {'fields': ('role', 'spot', 'phone_number', 'full_name', 'tg_chat_id')}),
            )
        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == 'owner' and db_field.name == 'spot':
            venue = request.user.venue
            if venue:
                kwargs["queryset"] = Spot.objects.filter(venue=venue)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if request.user.role == 'owner':
            if not change:
                obj.venue = request.user.venue
                obj.is_staff = True
                obj.role = 'admin'
            super().save_model(request, obj, form, change)

            admin_group = Group.objects.get(name='Администратор')
            obj.groups.add(admin_group)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == 'owner':
            return qs.filter(venue=request.user.venue)
