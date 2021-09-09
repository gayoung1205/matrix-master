function licenseAuth() {
  var license = $('input[id=inputLicense]');
  if (license.val().length === 0) {
    license.addClass('is-invalid');
    return;
  }

  $('#licenseAuthForm').submit();
}
