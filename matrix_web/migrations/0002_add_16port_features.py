# Generated migration for 16-port features
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('matrix_web', '0001_initial'),
    ]

    operations = [
        # 1. monitor_names 필드 타입 변경 (TEXT -> JSON)
        migrations.AlterField(
            model_name='matrix',
            name='monitor_names',
            field=JSONField(blank=True, default=list, verbose_name='모니터 이름들'),
        ),
        
        # 2. device_names JSONField 추가
        migrations.AddField(
            model_name='matrix',
            name='device_names',
            field=JSONField(blank=True, default=list, verbose_name='디바이스 이름들'),
        ),
        
        # 3. kvm_input 필드 추가
        migrations.AddField(
            model_name='matrix',
            name='kvm_input',
            field=models.CharField(blank=True, default='01', max_length=50, null=True),
        ),
        
        # 4. MonitorLayout 모델 추가
        migrations.CreateModel(
            name='MonitorLayout',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('monitor_position', models.IntegerField()),
                ('display_order', models.IntegerField(default=0)),
                ('is_visible', models.BooleanField(default=True)),
                ('row_position', models.IntegerField(default=1)),
                ('col_position', models.IntegerField(default=1)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('matrix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matrix_web.matrix')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '모니터 레이아웃',
                'verbose_name_plural': '모니터 레이아웃들',
                'db_table': 'matrix_web_monitorlayout',
                'unique_together': {('user', 'matrix', 'monitor_position')},
            },
        ),
        
        # 5. SystemPassword 모델 추가
        migrations.CreateModel(
            name='SystemPassword',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('password', models.CharField(default='admin123', max_length=255)),
                ('description', models.CharField(blank=True, default='시스템 관리 비밀번호', max_length=255, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': '시스템 비밀번호',
                'verbose_name_plural': '시스템 비밀번호',
                'db_table': 'matrix_web_systempassword',
            },
        ),
        
        # 6. ProfileOrderConfig 모델 추가
        migrations.CreateModel(
            name='ProfileOrderConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', JSONField(blank=True, default=list)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, 
                                             related_name='profile_order_config', 
                                             to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '프로필 순서 설정',
                'verbose_name_plural': '프로필 순서 설정들',
                'db_table': 'matrix_web_profileorderconfig',
            },
        ),
        
        # 7. DeviceNameConfig 모델 추가
        migrations.CreateModel(
            name='DeviceNameConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('device_type', models.CharField(choices=[('hardware', '하드웨어'), ('server', '서버')], max_length=50)),
                ('device_name', models.CharField(default='', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '디바이스 이름 설정',
                'verbose_name_plural': '디바이스 이름 설정들',
                'db_table': 'matrix_web_devicenameconfig',
                'unique_together': {('user', 'device_type')},
            },
        ),
    ]
