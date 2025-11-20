# matrix_web/management/commands/initialize_matrix.py
# 이 파일을 만들어서 기존 데이터를 초기화할 수 있습니다.

from django.core.management.base import BaseCommand
from matrix_web.models import Matrix

class Command(BaseCommand):
    help = '모든 Matrix 객체를 16포트용으로 초기화합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-inputs',
            action='store_true',
            help='입력 설정도 초기화합니다 (monitor01->device01, monitor02->device02, ...)',
        )

    def handle(self, *args, **options):
        matrices = Matrix.objects.all()

        for matrix in matrices:
            # 기본 모니터 이름 설정
            if not isinstance(matrix.monitor_names, list) or len(matrix.monitor_names) < 16:
                matrix.monitor_names = [f"monitor{i+1:02d}" for i in range(16)]
                self.stdout.write(f'Matrix {matrix.id}: monitor_names 초기화 완료')

            # 기본 디바이스 이름 설정
            if not isinstance(matrix.device_names, list) or len(matrix.device_names) < 16:
                matrix.device_names = [f"device{i+1:02d}" for i in range(16)]
                self.stdout.write(f'Matrix {matrix.id}: device_names 초기화 완료')

            # 입력 설정 초기화 (옵션)
            if options['reset_inputs']:
                matrix.input_a = "01"
                matrix.input_b = "02"
                matrix.input_c = "03"
                matrix.input_d = "04"
                matrix.input_e = "05"
                matrix.input_f = "06"
                matrix.input_g = "07"
                matrix.input_h = "08"
                matrix.input_i = "09"
                matrix.input_j = "10"
                matrix.input_k = "11"
                matrix.input_l = "12"
                matrix.input_m = "13"
                matrix.input_n = "14"
                matrix.input_o = "15"
                matrix.input_p = "16"
                self.stdout.write(f'Matrix {matrix.id}: 입력 설정 초기화 완료')

            # _skip_initial_setup 플래그를 설정하여 save 메서드에서 중복 초기화 방지
            matrix._skip_initial_setup = True
            matrix.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'성공적으로 {matrices.count()}개의 Matrix를 초기화했습니다.'
            )
        )

# 사용법:
# python manage.py initialize_matrix
# python manage.py initialize_matrix --reset-inputs