from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Matrix,
    MatrixSetting,
    Profile,
)


class MatrixSettingSerializer(serializers.ModelSerializer):
    matrix_name = serializers.SerializerMethodField()
    profile_name = serializers.SerializerMethodField()
    main_connect = serializers.SerializerMethodField()

    class Meta:
        model = MatrixSetting
        fields = "__all__"

    def get_matrix_name(self, obj):
        return obj.matrix.name

    def get_profile_name(self, obj):
        return obj.profile.name

    def get_main_connect(self, obj):
        return obj.matrix.main_connect
    
class MatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matrix
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"