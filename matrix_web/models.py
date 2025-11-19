# from django.db import models
# from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# # Create your models here.
# class Matrix(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=200, null=True, blank=True)
#     matrix_ip_address = models.GenericIPAddressField(null=True, blank=True)
#     kvm_ip_address = models.GenericIPAddressField(null=True, blank=True)
#     kvm_ip_address2 = models.GenericIPAddressField(null=True, blank=True)
#     port = models.IntegerField(null=True, blank=True)
#     is_main = models.BooleanField(default=False)
#     main_connect = models.IntegerField(default=0, null=True, blank=True)
#     input_a = models.CharField(max_length=50, default="01")
#     input_b = models.CharField(max_length=50, default="02")
#     input_c = models.CharField(max_length=50, default="03")
#     input_d = models.CharField(max_length=50, default="04")
#     input_e = models.CharField(max_length=50, default="05")
#     input_f = models.CharField(max_length=50, default="06")
#     input_g = models.CharField(max_length=50, default="07")
#     input_h = models.CharField(max_length=50, default="08")
#     input_i = models.CharField(max_length=50, default="09")
#     input_j = models.CharField(max_length=50, default="10")
#     input_k = models.CharField(max_length=50, default="11")
#     input_l = models.CharField(max_length=50, default="12")
#     input_m = models.CharField(max_length=50, default="13")
#     input_n = models.CharField(max_length=50, default="14")
#     input_o = models.CharField(max_length=50, default="15")
#     input_p = models.CharField(max_length=50, default="16")
#     updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#
#
# class Profile(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=200, null=True, blank=True)
#     updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#
#
# class MatrixSetting(models.Model):
#     """
#         input_a ~ input_kvm
#             - 값이 "00"이면 실행안하고 넘어감
#     """
#     id = models.AutoField(primary_key=True)
#     profile = models.ForeignKey(
#         Profile,
#         on_delete=models.CASCADE,
#         related_name="profile_sets",
#         related_query_name="profile_set",
#     )
#     matrix = models.ForeignKey(
#         Matrix,
#         on_delete=models.CASCADE,
#         related_name="matrix_sets",
#         related_query_name="matrix_set",
#     )
#     input_a = models.CharField(max_length=50, default="00")
#     input_b = models.CharField(max_length=50, default="00")
#     input_c = models.CharField(max_length=50, default="00")
#     input_d = models.CharField(max_length=50, default="00")
#     input_e = models.CharField(max_length=50, default="00")
#     input_f = models.CharField(max_length=50, default="00")
#     input_g = models.CharField(max_length=50, default="00")
#     input_h = models.CharField(max_length=50, default="00")
#     input_i = models.CharField(max_length=50, default="00")
#     input_j = models.CharField(max_length=50, default="00")
#     input_k = models.CharField(max_length=50, default="00")
#     input_l = models.CharField(max_length=50, default="00")
#     input_m = models.CharField(max_length=50, default="00")
#     input_n = models.CharField(max_length=50, default="00")
#     input_o = models.CharField(max_length=50, default="00")
#     input_p = models.CharField(max_length=50, default="00")
#     input_kvm = models.CharField(max_length=50, default="00")
#     updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#
# class License(models.Model):
#     id = models.AutoField(primary_key=True)
#     key = models.TextField(default="")
#
# class UserPermission(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#
#     """
#     유저 권한 설정
#         0 : aisol 관리자 System 설정 권한 O, Profile 설정 권한 O
#         1 : 유저 관리자 System 설정 권한 X, Profile 설정 권한 O
#         2 : 유저 사용자 System 설정 권한 X, Profile 설정 권한 X
#         3 : 학생 그룹1 사용자 System 설정 권한 X, Profile 설정 권한 X
#         4 : 학생 그룹2 사용자 System 설정 권한 X, Profile 설정 권한 X
#         5 : 학생 그룹3 사용자 System 설정 권한 X, Profile 설정 권한 X
#         6 : 학생 그룹4 사용자 System 설정 권한 X, Profile 설정 권한 X
#     """
#     permission = models.IntegerField(default=2)
#
# @receiver(post_save, sender=User)
# def create_user_permission(sender, instance, created, **kwargs):
#     if created:
#         UserPermission.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_permission(sender, instance, **kwargs):
#     instance.userpermission.save()
#
# class Document(models.Model):
#     title = models.CharField(max_length = 200)
#     upload_file = models.FileField(upload_to = "Uploaded Files/")
#     upload_date = models.DateTimeField(auto_now = True)


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# PostgreSQL의 경우 django.contrib.postgres.fields.JSONField 사용
try:
    from django.db.models import JSONField
except ImportError:
    # Django 3.1 미만 버전
    from django.contrib.postgres.fields import JSONField


class Matrix(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    # 16포트 확장 기능 - JSONField 사용
    monitor_names = JSONField(
        verbose_name="모니터 이름들",
        default=list,
        blank=True,
        help_text="16개 모니터의 이름 목록"
    )
    device_names = JSONField(
        verbose_name="디바이스 이름들",
        default=list,
        blank=True,
        help_text="16개 디바이스의 이름 목록"
    )

    matrix_ip_address = models.GenericIPAddressField(null=True, blank=True)
    kvm_ip_address = models.GenericIPAddressField(null=True, blank=True)
    kvm_ip_address2 = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    is_main = models.BooleanField(default=False)
    main_connect = models.IntegerField(default=0, null=True, blank=True)

    # 16포트 지원
    input_a = models.CharField(max_length=50, default="01")
    input_b = models.CharField(max_length=50, default="02")
    input_c = models.CharField(max_length=50, default="03")
    input_d = models.CharField(max_length=50, default="04")
    input_e = models.CharField(max_length=50, default="05")
    input_f = models.CharField(max_length=50, default="06")
    input_g = models.CharField(max_length=50, default="07")
    input_h = models.CharField(max_length=50, default="08")
    input_i = models.CharField(max_length=50, default="09")
    input_j = models.CharField(max_length=50, default="10")
    input_k = models.CharField(max_length=50, default="11")
    input_l = models.CharField(max_length=50, default="12")
    input_m = models.CharField(max_length=50, default="13")
    input_n = models.CharField(max_length=50, default="14")
    input_o = models.CharField(max_length=50, default="15")
    input_p = models.CharField(max_length=50, default="16")

    # KVM 입력 상태
    kvm_input = models.CharField(
        max_length=50,
        default="01",
        null=True,
        blank=True,
        help_text="현재 선택된 KVM 입력"
    )

    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'matrix_web_matrix'  # 기존 테이블 이름 유지
        verbose_name = "매트릭스 장비"
        verbose_name_plural = "매트릭스 장비들"

    def __str__(self):
        return self.name or f"Matrix #{self.id}"

    def save(self, *args, **kwargs):
        """저장 시 자동으로 16포트 초기값 설정"""
        # monitor_names 초기화
        if not self.monitor_names or len(self.monitor_names) != 16:
            self.monitor_names = [f"Monitor {i+1:02d}" for i in range(16)]

        # device_names 초기화
        if not self.device_names or len(self.device_names) != 16:
            self.device_names = [f"Device {i+1:02d}" for i in range(16)]

        super().save(*args, **kwargs)

    def get_monitor_name(self, index):
        """특정 인덱스의 모니터 이름 반환"""
        if 0 <= index < 16 and self.monitor_names and len(self.monitor_names) > index:
            return self.monitor_names[index]
        return f"Monitor {index+1:02d}"

    def get_device_name(self, index):
        """특정 인덱스의 디바이스 이름 반환"""
        if 0 <= index < 16 and self.device_names and len(self.device_names) > index:
            return self.device_names[index]
        return f"Device {index+1:02d}"


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    order = models.IntegerField(default=0, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'matrix_web_profile'  # 기존 테이블 이름 유지
        verbose_name = "프로필"
        verbose_name_plural = "프로필들"

    def __str__(self):
        return self.name or f"Profile #{self.id}"


class MatrixSetting(models.Model):
    """프로필별 매트릭스 설정 (16포트 지원)"""
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

    # 16포트 설정
    input_a = models.CharField(max_length=50, default="00")
    input_b = models.CharField(max_length=50, default="00")
    input_c = models.CharField(max_length=50, default="00")
    input_d = models.CharField(max_length=50, default="00")
    input_e = models.CharField(max_length=50, default="00")
    input_f = models.CharField(max_length=50, default="00")
    input_g = models.CharField(max_length=50, default="00")
    input_h = models.CharField(max_length=50, default="00")
    input_i = models.CharField(max_length=50, default="00")
    input_j = models.CharField(max_length=50, default="00")
    input_k = models.CharField(max_length=50, default="00")
    input_l = models.CharField(max_length=50, default="00")
    input_m = models.CharField(max_length=50, default="00")
    input_n = models.CharField(max_length=50, default="00")
    input_o = models.CharField(max_length=50, default="00")
    input_p = models.CharField(max_length=50, default="00")
    input_kvm = models.CharField(max_length=50, default="00")

    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'matrix_web_matrixsetting'  # 기존 테이블 이름 유지
        constraints = [
            models.UniqueConstraint(fields=['profile', 'matrix'], name='uq_profile_matrix')
        ]
        verbose_name = "매트릭스 설정"
        verbose_name_plural = "매트릭스 설정들"

    def __str__(self):
        return f"{self.profile.name} - {self.matrix.name}"


class License(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.TextField(default="")

    class Meta:
        db_table = 'matrix_web_license'  # 기존 테이블 이름 유지
        verbose_name = "라이센스"
        verbose_name_plural = "라이센스들"

    def __str__(self):
        return f"License #{self.id}"


class UserPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    """
    유저 권한 설정
        0 : aisol 관리자 - System 설정 권한O, Profile 설정 권한O
        1 : 유저 관리자 - System 설정 권한X, Profile 설정 권한O
        2 : 유저 사용자 - System 설정 권한X, Profile 설정 권한X
        3-6 : 학생 그룹 사용자 - System 설정 권한X, Profile 설정 권한X
    """
    permission = models.IntegerField(default=2)

    class Meta:
        db_table = 'matrix_web_userpermission'  # 기존 테이블 이름 유지
        verbose_name = "유저 권한"
        verbose_name_plural = "유저 권한들"

    def __str__(self):
        return f"{self.user.username} - 권한레벨: {self.permission}"


class Document(models.Model):
    title = models.CharField(max_length=200)
    upload_file = models.FileField(upload_to="Uploaded Files/")
    upload_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matrix_web_document'  # 기존 테이블 이름 유지
        verbose_name = "문서"
        verbose_name_plural = "문서들"

    def __str__(self):
        return self.title


# ============================================
# 16포트 확장 고급 기능 모델들 (신규)
# ============================================

class MonitorLayout(models.Model):
    """사용자별 모니터 레이아웃 설정 (16포트 지원)"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    matrix = models.ForeignKey(Matrix, on_delete=models.CASCADE)
    monitor_position = models.IntegerField(help_text="1~16 (실제 모니터 포트 번호)")
    display_order = models.IntegerField(default=0, help_text="화면상 표시 순서")
    is_visible = models.BooleanField(default=True, help_text="숨김/표시 여부")
    row_position = models.IntegerField(default=1, help_text="1 or 2 (상하 행)")
    col_position = models.IntegerField(default=1, help_text="1~8 (좌우 열)")
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'matrix_web_monitorlayout'
        unique_together = ('user', 'matrix', 'monitor_position')
        verbose_name = "모니터 레이아웃"
        verbose_name_plural = "모니터 레이아웃들"

    def __str__(self):
        return f"{self.user.username} - {self.matrix.name} - Monitor {self.monitor_position}"


class SystemPassword(models.Model):
    """시스템 관리 접근용 비밀번호"""
    id = models.AutoField(primary_key=True)
    password = models.CharField(
        max_length=255,
        default="admin123",
        help_text="시스템 관리자 비밀번호"
    )
    description = models.CharField(
        max_length=255,
        default="시스템 관리 비밀번호",
        null=True,
        blank=True
    )
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'matrix_web_systempassword'
        verbose_name = "시스템 비밀번호"
        verbose_name_plural = "시스템 비밀번호"

    def __str__(self):
        return f"시스템 비밀번호 (최종 수정: {self.updated_date.strftime('%Y-%m-%d %H:%M') if self.updated_date else 'N/A'})"


class ProfileOrderConfig(models.Model):
    """프로필 순서 설정 (드래그앤드롭 순서 저장)"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile_order_config'
    )
    order = JSONField(
        default=list,
        blank=True,
        help_text="프로필 ID 순서 리스트"
    )

    class Meta:
        db_table = 'matrix_web_profileorderconfig'
        verbose_name = "프로필 순서 설정"
        verbose_name_plural = "프로필 순서 설정들"

    def __str__(self):
        return f'{self.user.username} profile order'


class DeviceNameConfig(models.Model):
    """온디바이스 페이지의 장비 이름 설정"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('hardware', '하드웨어'),
            ('server', '서버')
        ]
    )
    device_name = models.CharField(
        max_length=200,
        default='',
        help_text="표시할 장비 이름"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matrix_web_devicenameconfig'
        unique_together = ('user', 'device_type')
        verbose_name = "디바이스 이름 설정"
        verbose_name_plural = "디바이스 이름 설정들"

    def __str__(self):
        return f"{self.user.username} - {self.device_type}: {self.device_name}"


# ============================================
# 시그널 핸들러들 (16포트 지원)
# ============================================

@receiver(post_save, sender=User)
def create_user_permission(sender, instance, created, **kwargs):
    if created:
        UserPermission.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_permission(sender, instance, **kwargs):
    if hasattr(instance, 'userpermission'):
        instance.userpermission.save()


@receiver(post_save, sender=Matrix)
def create_settings_for_new_matrix(sender, instance, created, **kwargs):
    """새 매트릭스 생성 시 모든 프로필에 대해 MatrixSetting 생성"""
    if not created:
        return

    for profile in Profile.objects.all():
        MatrixSetting.objects.get_or_create(
            profile=profile,
            matrix=instance,
            defaults={
                'input_a': '00', 'input_b': '00', 'input_c': '00', 'input_d': '00',
                'input_e': '00', 'input_f': '00', 'input_g': '00', 'input_h': '00',
                'input_i': '00', 'input_j': '00', 'input_k': '00', 'input_l': '00',
                'input_m': '00', 'input_n': '00', 'input_o': '00', 'input_p': '00',
                'input_kvm': '00'
            }
        )


@receiver(post_save, sender=Profile)
def create_settings_for_new_profile(sender, instance, created, **kwargs):
    """새 프로필 생성 시 모든 매트릭스에 대해 MatrixSetting 생성"""
    if not created:
        return

    for matrix in Matrix.objects.all():
        MatrixSetting.objects.get_or_create(
            profile=instance,
            matrix=matrix,
            defaults={
                'input_a': '00', 'input_b': '00', 'input_c': '00', 'input_d': '00',
                'input_e': '00', 'input_f': '00', 'input_g': '00', 'input_h': '00',
                'input_i': '00', 'input_j': '00', 'input_k': '00', 'input_l': '00',
                'input_m': '00', 'input_n': '00', 'input_o': '00', 'input_p': '00',
                'input_kvm': '00'
            }
        )


@receiver(post_save, sender=User)
def create_default_monitor_layout(sender, instance, created, **kwargs):
    """새 유저 생성 시 기본 모니터 레이아웃 생성"""
    if not created:
        return

    # 모든 매트릭스에 대해 기본 레이아웃 생성
    for matrix in Matrix.objects.all():
        for i in range(16):  # 16포트
            MonitorLayout.objects.get_or_create(
                user=instance,
                matrix=matrix,
                monitor_position=i+1,
                defaults={
                    'display_order': i,
                    'is_visible': True,
                    'row_position': 1 if i < 8 else 2,  # 1~8: 첫째줄, 9~16: 둘째줄
                    'col_position': (i % 8) + 1
                }
            )