from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Matrix(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    matrix_ip_address = models.GenericIPAddressField(null=True, blank=True)
    kvm_ip_address = models.GenericIPAddressField(null=True, blank=True)
    kvm_ip_address2 = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    is_main = models.BooleanField(default=False)
    main_connect = models.IntegerField(default=0, null=True, blank=True)
    input_a = models.CharField(max_length=50, default="01")
    input_b = models.CharField(max_length=50, default="02")
    input_c = models.CharField(max_length=50, default="03")
    input_d = models.CharField(max_length=50, default="04")
    input_e = models.CharField(max_length=50, default="05")
    input_f = models.CharField(max_length=50, default="06")
    input_g = models.CharField(max_length=50, default="07")
    input_h = models.CharField(max_length=50, default="08")
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class MatrixSetting(models.Model):
    """
        input_a ~ input_kvm
            - 값이 "00"이면 실행안하고 넘어감
    """
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="profile_sets",
        related_query_name="profile_set",
    )
    matrix = models.ForeignKey(
        Matrix,
        on_delete=models.CASCADE,
        related_name="matrix_sets",
        related_query_name="matrix_set",
    )
    input_a = models.CharField(max_length=50, default="00")
    input_b = models.CharField(max_length=50, default="00")
    input_c = models.CharField(max_length=50, default="00")
    input_d = models.CharField(max_length=50, default="00")
    input_e = models.CharField(max_length=50, default="00")
    input_f = models.CharField(max_length=50, default="00")
    input_g = models.CharField(max_length=50, default="00")
    input_h = models.CharField(max_length=50, default="00")
    input_kvm = models.CharField(max_length=50, default="00")
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class License(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.TextField(default="")

class UserPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    """
    유저 권한 설정
        0 : aisol 관리자 Matrix O, Profile O
        1 : 유저 관리자 Matrix X, Profile O
        2 : 유저 사용자 Matrix X, Profile X
    """ 
    permission = models.IntegerField(default=2)

@receiver(post_save, sender=User)
def create_user_permission(sender, instance, created, **kwargs):
    if created:
        UserPermission.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_permission(sender, instance, **kwargs):
    instance.userpermission.save()