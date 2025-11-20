from django.contrib import admin
from .models import Matrix, Profile, MatrixSetting, UserPermission

# Register your models here.
class MatrixAdmin(admin.ModelAdmin):
    list_display=[
        'id',
        'name',
        'matrix_ip_address',
        'kvm_ip_address',
        'port',
        'is_main',
        'main_connect',
        'input_a',
        'input_b',
        'input_c',
        'input_d',
        'input_e',
        'input_f',
        'input_g',
        'input_h',
        'input_i',
        'input_j',
        'input_k',
        'input_l',
        'input_m',
        'input_n',
        'input_o',
        'input_p',
    ]


class MatrixSettingAdmin(admin.ModelAdmin):
    list_display=[
        'id',
        'profile',
        'matrix',
        'input_a',
        'input_b',
        'input_c',
        'input_d',
        'input_e',
        'input_f',
        'input_g',
        'input_h',
        'input_i',
        'input_j',
        'input_k',
        'input_l',
        'input_m',
        'input_n',
        'input_o',
        'input_p',
        'input_kvm',
    ]
    list_editable=[
        'input_a',
        'input_b',
        'input_c',
        'input_d',
        'input_e',
        'input_f',
        'input_g',
        'input_h',
        'input_i',
        'input_j',
        'input_k',
        'input_l',
        'input_m',
        'input_n',
        'input_o',
        'input_p',
        'input_kvm',
    ]
    list_per_page=30


class UserPermissionAdmin(admin.ModelAdmin):
    list_display=[
        'user',
        'permission',
    ]
    list_editable=[
        'permission',
    ]


class ProfileAdmin(admin.ModelAdmin):
    list_display=[
        'id',
        'name',
        'created_date',
    ]
    list_editable=[
        'name',
    ]

admin.site.register(Matrix, MatrixAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(MatrixSetting, MatrixSettingAdmin)
admin.site.register(UserPermission, UserPermissionAdmin)