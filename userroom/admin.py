# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserChangeForm, CustomUserCreationForm
# from .models import User


# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = User
#     list_display = ('email', 'first_name', 'last_name', 'is_staff')
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name')}),
#         ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}  # noqa: E501
#         ),
#     )
#     search_fields = ('email',)
#     ordering = ('email',)

# admin.site.register(User, CustomUserAdmin)
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'auth0_sub')
    search_fields = ('username', 'email')
