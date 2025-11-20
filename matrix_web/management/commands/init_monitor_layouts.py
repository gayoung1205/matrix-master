# matrix_web/management/commands/init_monitor_layouts.py
# 기존 사용자들을 위한 기본 레이아웃 생성 명령어

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from matrix_web.models import Matrix, MonitorLayout

class Command(BaseCommand):
    help = '모든 사용자와 매트릭스에 대해 기본 모니터 레이아웃을 생성합니다.'

    def handle(self, *args, **options):
        users = User.objects.all()
        matrices = Matrix.objects.all()

        created_count = 0

        for user in users:
            for matrix in matrices:
                # 기존 레이아웃이 없는 경우에만 생성
                existing_layouts = MonitorLayout.objects.filter(user=user, matrix=matrix)

                if not existing_layouts.exists():
                    # 16포트 기본 레이아웃 생성
                    for i in range(1, 17):
                        row_position = 1 if i <= 8 else 2
                        col_position = i if i <= 8 else i - 8

                        MonitorLayout.objects.create(
                            user=user,
                            matrix=matrix,
                            monitor_position=i,
                            row_position=row_position,
                            col_position=col_position,
                            display_order=i - 1,
                            is_visible=True
                        )
                        created_count += 1

                    self.stdout.write(f'User {user.username} - Matrix {matrix.name}: 16개 레이아웃 생성')

        self.stdout.write(
            self.style.SUCCESS(
                f'총 {created_count}개의 모니터 레이아웃이 생성되었습니다.'
            )
        )

# 실행 방법:
# python manage.py init_monitor_layouts