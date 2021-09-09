from django.conf.urls import url
from .views import MatrixView, MatrixDetailView, ProfileView, ProfileDetailView, MatrixExportView, MatrixImportView, ProfileExportView, ProfileImportView, LicenseAuthView

urlpatterns = [
    url(r"^matrixes/", MatrixView.as_view(), name="matrix"),
    url(r"^matrix/", MatrixDetailView.as_view(), name="matrix_detail"),
    url(r"^profiles/", ProfileView.as_view(), name="profile"),
    url(r"^profile/", ProfileDetailView.as_view(), name="profile_detail"),
    url(r"^matrix_export/", MatrixExportView.as_view(), name="matrix_export"),
    url(r"^matrix_import/", MatrixImportView.as_view(), name="matrix_import"),
    url(r"^profile_export/", ProfileExportView.as_view(), name="profile_export"),
    url(r"^profile_import/", ProfileImportView.as_view(), name="profile_import"),
    url(r"^license_auth/", LicenseAuthView.as_view(), name="license_auth"),
]
