$('#matrixDelete').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var delete_id = button.data('whatever'); // Extract info from data-* attributes
  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this);
  modal.find('#deleteId').val(delete_id);
});

$('#matrixUpdate').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var data_list = button.data('whatever'); // Extract info from data-* attributes
  var data = data_list.split(',');
  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this);
  modal.find('#updateId').val(data[0]);
  modal.find('#update-input-name').val(data[1]);
  modal.find('#update-input-matrix-ip').val(data[2]);
  modal.find('#update-input-kvm-ip').val(data[3]);
  modal.find('#update-input-kvm-ip2').val(data[4]);
  modal.find('#update-input-port').val(data[5]);
  if (data[6] == 'True') {
    modal.find('input[id=update-input-kvm-ip2]').attr('disabled', false);
    modal.find('select[id=update-input-main-connect]').attr('disabled', true);
    modal.find('#is-main-update-true').attr('checked', true);
  } else {
    modal.find('input[id=update-input-kvm-ip2]').attr('disabled', true);
    modal.find('select[id=update-input-main-connect]').attr('disabled', false);
    modal.find('#is-main-update-false').attr('checked', true);
  }
  modal.find('option[id=update-option]').val(data[7]);
  modal.find('option[id=update-option]').text(data[7]);
});

function matrixExport() {
  var list = new Array();
  $('input[name=matrix_check]').each(function (index, item) {
    if ($(item).is(':checked')) {
      list.push($(item).val());
    }
  });

  if (list.length > 0) {
    $('#export_mat_list').val(list);
    $('#matrixExportForm').submit();
    $('#matrixExport').modal('hide');
  } else {
    $('#export_mat_list').addClass('is-invalid');
  }
}

function matrixImport() {
  file = $('#formFile');
  if (file.val().length < 1) {
    $('#formFile').addClass('is-invalid');
    $('#file-feedback').text('파일을 선택해주세요.');
    return;
  }

  var ext = file.val().split('.').pop().toLowerCase();
  if ($.inArray(ext, ['csv']) == -1) {
    file.val(''); // input file 파일명을 다시 지워준다.
    $('#formFile').addClass('is-invalid');
    $('#file-feedback').text('.csv 파일 형식만 가능합니다.');
    return;
  }

  $('#matrixImportForm').submit();
  $('#matrixImport').modal('hide');
}

function matrixCreate() {
  inputName = $('#create-input-name');
  if (inputName.val().length < 1) {
    inputName.addClass('is-invalid');
    $('#create-name-feedback').text('이름을 입력해주세요.');
    return;
  } else {
    inputName.removeClass('is-invalid');
    $('#create-name-feedback').text('');
  }

  if (inputName.val().includes(',')) {
    $('#create-input-name').addClass('is-invalid');
    $('#create-name-feedback').text('"," 은 허용되지 않은 문자입니다.');
    return;
  } else {
    inputName.removeClass('is-invalid');
    $('#create-name-feedback').text('');
  }

  inputMatrixIp = $('#create-input-matrix-ip');
  var ipFormat =
    /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  if (!inputMatrixIp.val().match(ipFormat)) {
    inputMatrixIp.addClass('is-invalid');
    $('#create-matrix-ip-feedback').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    inputMatrixIp.removeClass('is-invalid');
    $('#create-matrix-ip-feedback').text('');
  }

  inputKvmIp = $('#create-input-kvm-ip');
  if (!inputKvmIp.val().match(ipFormat)) {
    inputKvmIp.addClass('is-invalid');
    $('#create-kvm-ip-feedback').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    inputKvmIp.removeClass('is-invalid');
    $('#create-kvm-ip-feedback').text('');
  }

  inputKvmIp2 = $('#create-input-kvm-ip2');
  if (!inputKvmIp2.is(':disabled')) {
    if (!inputKvmIp2.val().match(ipFormat)) {
      inputKvmIp2.addClass('is-invalid');
      $('#create-kvm-ip-feedback2').text('IP주소가 유효하지 않습니다.');
      return;
    } else {
      inputKvmIp2.removeClass('is-invalid');
      $('#create-kvm-ip-feedback2').text('');
    }
  }

  inputPort = $('#create-input-port');
  if (inputPort.val().length < 1) {
    inputPort.addClass('is-invalid');
    $('#create-port-feedback').text('포트를 입력해주세요.');
    return;
  } else {
    inputPort.removeClass('is-invalid');
    $('#create-port-feedback').text('');
  }

  if ($('input[type=radio][name=is_main]:checked').val() == 'False') {
    selectText = $('form[id=matrixCreateForm] select[id=create-input-main-connect] option:selected').text();
    if (selectText == '번호 선택') {
      $('form[id=matrixCreateForm] select[id=create-input-main-connect]').addClass('is-invalid');
      return;
    } else {
      $('form[id=matrixCreateForm] select[id=create-input-main-connect]').removeClass('is-invalid');
    }
  }

  $('#matrixCreateForm').submit();
  $('#matrixCreate').modal('hide');
}

function matrixUpdate() {
  inputName = $('#update-input-name');
  if (inputName.val().length < 1) {
    inputName.addClass('is-invalid');
    $('#update-name-feedback').text('이름을 입력해주세요.');
    return;
  } else {
    inputName.removeClass('is-invalid');
    $('#update-name-feedback').text('');
  }

  if (inputName.val().includes(',')) {
    $('#update-input-name').addClass('is-invalid');
    $('#update-name-feedback').text('"," 은 허용되지 않은 문자입니다.');
    return;
  } else {
    inputName.removeClass('is-invalid');
    $('#update-name-feedback').text('');
  }

  inputMatrixIp = $('#update-input-matrix-ip');
  var ipFormat =
    /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  if (!inputMatrixIp.val().match(ipFormat)) {
    inputMatrixIp.addClass('is-invalid');
    $('#update-matrix-ip-feedback').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    inputMatrixIp.removeClass('is-invalid');
    $('#update-matrix-ip-feedback').text('');
  }

  inputKvmIp = $('#update-input-kvm-ip');
  if (!inputKvmIp.val().match(ipFormat)) {
    inputKvmIp.addClass('is-invalid');
    $('#update-kvm-ip-feedback').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    inputKvmIp.removeClass('is-invalid');
    $('#update-kvm-ip-feedback').text('');
  }

  inputKvmIp2 = $('#update-input-kvm-ip2');
  if (!inputKvmIp2.is(':disabled')) {
    if (!inputKvmIp2.val().match(ipFormat)) {
      inputKvmIp2.addClass('is-invalid');
      $('#update-kvm-ip-feedback2').text('IP주소가 유효하지 않습니다.');
      return;
    } else {
      inputKvmIp2.removeClass('is-invalid');
      $('#update-kvm-ip-feedback2').text('');
    }
  }

  inputPort = $('#update-input-port');
  if (inputPort.val().length < 1) {
    inputPort.addClass('is-invalid');
    $('#update-port-feedback').text('포트를 입력해주세요.');
    return;
  } else {
    inputPort.removeClass('is-invalid');
    $('#update-port-feedback').text('');
  }

  if ($('input[type=radio][name=is_main]:checked').val() == 'False') {
    selectText = $('form[id=matrixUpdateForm] select[id=update-input-main-connect] option:selected').text();
    if (selectText == '번호 선택') {
      $('form[id=matrixUpdateForm] select[id=update-input-main-connect]').addClass('is-invalid');
      return;
    } else {
      $('form[id=matrixUpdateForm] select[id=update-input-main-connect]').removeClass('is-invalid');
    }
  }

  $('#matrixUpdateForm').submit();
  $('#matrixUpdate').modal('hide');
}

$('input[type=radio][name=is_main]').on('change', function () {
  switch ($(this).val()) {
    case 'True':
      $('select[id=create-input-main-connect]').attr('disabled', true);
      $('input[id=create-input-kvm-ip2]').attr('disabled', false);
      break;
    case 'False':
      $('select[id=create-input-main-connect]').attr('disabled', false);
      $('input[id=create-input-kvm-ip2]').attr('disabled', true);
      break;
  }
});
