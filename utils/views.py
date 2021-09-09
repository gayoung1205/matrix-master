from django.shortcuts import render
import os, sys, hashlib
from .salt import salt
import binascii
from matrix_web.models import License

# Create your views here.
def license_auth(func):
    def auth(req, *args, **kwargs):
        try:
            license = License.objects.all()
        except Exception as e:
            print(e)
            return render(req, 'errors/license_error.html')            
        if license:
            baseboard = ""
            os_type = sys.platform.lower()  
            salt_key = binascii.unhexlify(salt["key"])

            if "windows" in os_type or "win" in os_type:
                command = "wmic baseboard get product, Manufacturer, version, serialnumber"
                baseboard = os.popen(command).read().replace("\n","").replace("	","").replace(" ","").replace("ManufacturerProductSerialNumberVersion","")
            
            if "linux" in os_type:
                command = "cat /proc/cpuinfo | grep Serial | awk '{print $3}'"
                baseboard = os.popen(command).read().replace("\n","").replace("	","").replace(" ","")

            hash_key = hashlib.sha256(salt_key + baseboard.encode())

            if hash_key.hexdigest() == license[0].key:
                return func(req, *args, **kwargs)
            else:
                return render(req, 'errors/license_error.html')
        else:
            return render(req, 'errors/license_error.html') 
    return auth 
