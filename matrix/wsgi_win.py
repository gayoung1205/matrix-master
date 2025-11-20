activate_this = "C:\Users\user\matrix\venv\Scripts/activate"

exec(open(activate_this).read(), dict(__file__=activate_this))

import os
import sys
import site

# 가상환경의 패키지 추가
site.addsitedir("C:\Users\user\matrix\venv\Scripts/site-packages")

# PYTHONPATH에 application directory 추가
path = os.path.abspath(__file__ + "/../..")
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "matrix.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "matrix.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
