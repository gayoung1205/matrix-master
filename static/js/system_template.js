// 매트릭스 삭제 모달 이벤트
$('#matrixDelete').on('show.bs.modal', function(event) {
  var button = $(event.relatedTarget);
  var matrixId = button.data('whatever');

  if (!matrixId) {
    alert('삭제할 매트릭스를 찾을 수 없습니다.');
    return false;
  }

  // 8포트와 동일하게 matrix_detail URL 사용하고 hidden input에 id 설정
  $(this).find('#deleteId').val(matrixId);
});

// DOM이 완전히 로드된 후 실행
$(document).ready(function () {

  $('.toggle-name-buttons').on('click', function () {
    const targetId = $(this).data('toggle-id');
    const $group = $('#' + targetId);
    $group.toggleClass('d-none');
  });

  // 모든 관련 이벤트 리스너 완전히 제거
  $(document).off('click', '[data-target="#matrixUpdate"]');
  $('#matrixUpdate').off('show.bs.modal');

  // 수정 버튼 이벤트 바인딩 함수
  function bindUpdateButton() {
    $(document).one('click', '[data-target="#matrixUpdate"]', function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();

      var $button = $(this);
      var id = $button.attr('data-id');
      var name = $button.attr('data-name');
      var matrix_ip = $button.attr('data-matrix-ip');
      var kvm_ip = $button.attr('data-kvm-ip');
      var kvm_ip2 = $button.attr('data-kvm-ip2');
      var port = $button.attr('data-port');
      var is_main = $button.attr('data-is-main');
      var main_connect = $button.attr('data-main-connect');


      // 데이터가 없으면 리턴
      if (!id || !name) {
        bindUpdateButton(); // 이벤트 다시 바인딩
        return;
      }

      if (!kvm_ip2 || kvm_ip2 === 'None' || kvm_ip2 === 'null') {
        kvm_ip2 = '';
      }

      // 모달의 입력 필드에 데이터 설정
      $('#updateId').val(id);
      $('#update-input-name').val(name);
      $('#update-input-matrix-ip').val(matrix_ip);
      $('#update-input-kvm-ip').val(kvm_ip);
      $('#update-input-kvm-ip2').val(kvm_ip2);
      $('#update-input-port').val(port);

      // 라디오 버튼 설정
      if (is_main === 'True' || is_main === true) {
        $('#is-main-update-true').prop('checked', true);
        $('#is-main-update-false').prop('checked', false);
      } else {
        $('#is-main-update-true').prop('checked', false);
        $('#is-main-update-false').prop('checked', true);
      }

      // 메인 연결 번호 설정
      if (main_connect) {
        $('#update-input-main-connect').val(main_connect);
      }

      // 모달 직접 열기
      $('#matrixUpdate').modal('show');

      // 모달 닫힐 때 이벤트 다시 바인딩
      $('#matrixUpdate').one('hidden.bs.modal', function() {
        bindUpdateButton();
      });
    });
  }

  // 초기 바인딩
  bindUpdateButton();

  // 모달 닫기 버튼들에 직접 이벤트 바인딩
  $(document).on('click', '#matrixUpdate .close, #matrixUpdate .btn-modal-secondary', function(e) {
    e.preventDefault();
    closeUpdateModal();
  });
});

function closeUpdateModal() {

  // 방법 1: jQuery modal hide
  $('#matrixUpdate').modal('hide');

  // 방법 2: 직접 DOM 조작 (강제 닫기)
  setTimeout(function() {
    $('#matrixUpdate').removeClass('show');
    $('#matrixUpdate').removeClass('fade');
    $('#matrixUpdate').hide();
    $('.modal-backdrop').remove();
    $('body').removeClass('modal-open');
    $('body').css('padding-right', '');
    $('body').css('overflow', 'auto');

    // fade 클래스 다시 추가 (다음 번 열기를 위해)
    setTimeout(function() {
      $('#matrixUpdate').addClass('fade');
    }, 150);
  }, 150);
}

// 매트릭스 수정 모달 이벤트 (Bootstrap 4 방식)
$('#matrixUpdate').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);

  var id = button.data('id');
  var name = button.data('name');
  var matrix_ip = button.data('matrix-ip');
  var kvm_ip = button.data('kvm-ip');
  var kvm_ip2 = button.data('kvm-ip2');
  var port = button.data('port');
  var is_main = button.data('is-main');
  var main_connect = button.data('main-connect');


  if (!kvm_ip2 || kvm_ip2 === 'None') kvm_ip2 = '';

  $('#updateId').val(id);
  $('#update-input-name').val(name);
  $('#update-input-matrix-ip').val(matrix_ip);
  $('#update-input-kvm-ip').val(kvm_ip);
  $('#update-input-kvm-ip2').val(kvm_ip2);
  $('#update-input-port').val(port);

  $('#is-main-update-true').prop('checked', is_main === true || is_main === 'True');
  $('#is-main-update-false').prop('checked', is_main === false || is_main === 'False');

  $('#update-input-main-connect option').each(function () {
    if ($(this).val() === main_connect) {
      $(this).prop('selected', true);
    }
  });
});

// Main/Sub 라디오 버튼 변경 이벤트
$('input[name=is_main]').on('change', function () {
  if (this.value === 'True') {
    $('#create-input-main-connect').prop('disabled', true);
    $('#create-input-kvm-ip2').prop('disabled', false);
  } else {
    $('#create-input-main-connect').prop('disabled', false);
    $('#create-input-kvm-ip2').prop('disabled', true);
  }
});

// 매트릭스 내보내기 함수
function matrixExport() {
  var list = [];
  $('input[name=matrix_check]').each(function () {
    if ($(this).is(':checked')) list.push($(this).val());
  });

  if (list.length) {
    $('#export_mat_list').val(list);
    $('#matrixExportForm').submit();
    $('#matrixExport').modal('hide');
  } else {
    $('#export_mat_list').addClass('is-invalid');
  }
}

// 매트릭스 가져오기 함수
function matrixImport() {
  var file = $('#formFile');
  if (!file.val()) {
    file.addClass('is-invalid');
    $('#file-feedback').text('파일을 선택해주세요.');
    return;
  }

  var ext = file.val().split('.').pop().toLowerCase();
  if ($.inArray(ext, ['csv']) === -1) {
    file.val('');
    file.addClass('is-invalid');
    $('#file-feedback').text('.csv 파일 형식만 가능합니다.');
    return;
  }

  $('#matrixImportForm').submit();
  $('#matrixImport').modal('hide');
}

// 매트릭스 생성 함수 (8포트 로직 기반)
function matrixCreate() {
  var inputName = $('#create-input-name');
  if (!inputName.val()) {
    inputName.addClass('is-invalid');
    $('#create-name-feedback').text('이름을 입력해주세요.');
    return;
  } else {
    inputName.removeClass('is-invalid');
    $('#create-name-feedback').text('');
  }

  if (inputName.val().includes(',')) {
    inputName.addClass('is-invalid');
    $('#create-name-feedback').text('"," 은 허용되지 않은 문자입니다.');
    return;
  }

  var ipFormat = /^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$/;

  var inputMatrixIp = $('#create-input-matrix-ip');
  var matrixIpValue = inputMatrixIp.val().trim();

  if (!matrixIpValue) {
    inputMatrixIp.addClass('is-invalid');
    $('#create-matrix-ip-feedback').text('Matrix IP를 입력해주세요.');
    return;
  } else if (!ipFormat.test(matrixIpValue)) {
    inputMatrixIp.addClass('is-invalid');
    $('#create-matrix-ip-feedback').text('IP주소가 유효하지 않습니다. (입력값: ' + matrixIpValue + ')');
    return;
  } else {
    inputMatrixIp.removeClass('is-invalid');
    $('#create-matrix-ip-feedback').text('');
    inputMatrixIp.val(matrixIpValue);
  }

  var inputKvmIp = $('#create-input-kvm-ip');
  var kvmIpValue = inputKvmIp.val().trim();


  if (!kvmIpValue) {
    inputKvmIp.addClass('is-invalid');
    $('#create-kvm-ip-feedback').text('KVM IP를 입력해주세요.');
    return;
  } else if (!ipFormat.test(kvmIpValue)) {
    inputKvmIp.addClass('is-invalid');
    $('#create-kvm-ip-feedback').text('IP주소가 유효하지 않습니다. (입력값: ' + kvmIpValue + ')');
    return;
  } else {
    inputKvmIp.removeClass('is-invalid');
    $('#create-kvm-ip-feedback').text('');
    inputKvmIp.val(kvmIpValue);
  }

  var inputKvmIp2 = $('#create-input-kvm-ip2');
  if (!inputKvmIp2.prop('disabled') && inputKvmIp2.val()) {
    var kvmIp2Value = inputKvmIp2.val().trim();
    if (!ipFormat.test(kvmIp2Value)) {
      inputKvmIp2.addClass('is-invalid');
      $('#create-kvm-ip-feedback2').text('IP주소가 유효하지 않습니다.');
      return;
    } else {
      inputKvmIp2.removeClass('is-invalid');
      $('#create-kvm-ip-feedback2').text('');
      inputKvmIp2.val(kvmIp2Value);
    }
  }

  var inputPort = $('#create-input-port');
  if (!inputPort.val()) {
    inputPort.addClass('is-invalid');
    $('#create-port-feedback').text('포트를 입력해주세요.');
    return;
  } else {
    inputPort.removeClass('is-invalid');
    $('#create-port-feedback').text('');
  }

  if ($('input[name=is_main]:checked').val() === 'False') {
    var selectText = $('#create-input-main-connect option:selected').text();
    if (selectText === '번호 선택') {
      $('#create-input-main-connect').addClass('is-invalid');
      return;
    } else {
      $('#create-input-main-connect').removeClass('is-invalid');
    }
  }

  $('#matrixCreateForm').submit();
  $('#matrixCreate').modal('hide');
}

// 매트릭스 수정 함수 (8포트 로직 기반)
function matrixUpdate() {
  var inputName = $('#update-input-name');
  if (!inputName.val()) {
    inputName.addClass('is-invalid');
    $('#update-name-feedback').text('이름을 입력해주세요.');
    return;
  } else {
    inputName.removeClass('is-invalid');
    $('#update-name-feedback').text('');
  }

  if (inputName.val().includes(',')) {
    inputName.addClass('is-invalid');
    $('#update-name-feedback').text('"," 은 허용되지 않은 문자입니다.');
    return;
  }

  var ipFormat = /^(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$/;
  var mIp = $('#update-input-matrix-ip');
  if (!ipFormat.test(mIp.val())) {
    mIp.addClass('is-invalid');
    $('#update-matrix-ip-feedback').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    mIp.removeClass('is-invalid');
    $('#update-matrix-ip-feedback').text('');
  }

  var kIp = $('#update-input-kvm-ip');
  if (!ipFormat.test(kIp.val())) {
    kIp.addClass('is-invalid');
    $('#update-kvm-ip-feedback').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    kIp.removeClass('is-invalid');
    $('#update-kvm-ip-feedback').text('');
  }

  var kIp2 = $('#update-input-kvm-ip2');
  var kIp2Val = kIp2.val();

  if (kIp2Val && !ipFormat.test(kIp2Val)) {
    kIp2.addClass('is-invalid');
    $('#update-kvm-ip-feedback2').text('IP주소가 유효하지 않습니다.');
    return;
  } else {
    kIp2.removeClass('is-invalid');
    $('#update-kvm-ip-feedback2').text('');
  }

  var p = $('#update-input-port');
  if (!p.val()) {
    p.addClass('is-invalid');
    $('#update-port-feedback').text('포트를 입력해주세요.');
    return;
  } else {
    p.removeClass('is-invalid');
    $('#update-port-feedback').text('');
  }

  if ($('input[name=is_main]:checked').val() === 'False') {
    var txt = $('#update-input-main-connect option:selected').text();
    if (txt === '번호 선택') {
      $('#update-input-main-connect').addClass('is-invalid');
      return;
    } else {
      $('#update-input-main-connect').removeClass('is-invalid');
    }
  }

  $('#matrixUpdateForm').submit();
  $('#matrixUpdate').modal('hide');
}

// IP 형식 검증 함수
function validateIP(ip) {
  var ipFormat = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  return ipFormat.test(ip);
}

// 하드웨어 IP 스캔 기능 (Create 모달용)
function scanHardwareIPs() {
  const matrixSelect = document.getElementById('matrix-ip-select');
  const kvmSelect = document.getElementById('kvm-ip-select');
  const scanBtn = document.getElementById('scan-ip-btn');

  matrixSelect.innerHTML = '<option value="">스캔 중...</option>';
  kvmSelect.innerHTML = '<option value="">스캔 중...</option>';
  matrixSelect.disabled = true;
  kvmSelect.disabled = true;
  scanBtn.disabled = true;
  scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 검색 중...';

  fetch('/api/scan_kvm_devices/')
      .then(response => response.json())
      .then(data => {
        if (data.success && data.devices && data.devices.length > 0) {
          updateIPDropdowns(data.devices);
          console.log(`${data.devices.length}개의 장비를 찾았습니다.`);
        } else {
          matrixSelect.innerHTML = '<option value="">장비를 찾을 수 없습니다</option>';
          kvmSelect.innerHTML = '<option value="">장비를 찾을 수 없습니다</option>';
          console.log('하드웨어 장비를 찾을 수 없습니다.');
        }
      })
      .catch(error => {
        console.error('IP 스캔 오류:', error);
        matrixSelect.innerHTML = '<option value="">스캔 실패</option>';
        kvmSelect.innerHTML = '<option value="">스캔 실패</option>';
        alert('IP 스캔 중 오류가 발생했습니다.');
      })
      .finally(() => {
        matrixSelect.disabled = false;
        kvmSelect.disabled = false;
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i class="fas fa-search"></i> 하드웨어 IP 검색';
      });
}

// IP 드롭다운 업데이트 함수 (Create용)
function updateIPDropdowns(devices) {
  const matrixSelect = document.getElementById('matrix-ip-select');
  const kvmSelect = document.getElementById('kvm-ip-select');

  let options = '<option value="">직접 입력</option>';
  devices.forEach(ip => {
    options += `<option value="${ip}">${ip}</option>`;
  });

  matrixSelect.innerHTML = options;
  kvmSelect.innerHTML = options;
}

// IP 선택 변경 함수 (Create용)
function onIPSelectChange(selectId, inputId) {
  const select = document.getElementById(selectId);
  const input = document.getElementById(inputId);

  if (select.value) {
    input.value = select.value.trim();
    input.readOnly = true;
    input.classList.add('bg-light');
    input.classList.remove('is-invalid');

    if (inputId === 'create-input-matrix-ip') {
      document.getElementById('create-matrix-ip-feedback').textContent = '';
    } else if (inputId === 'create-input-kvm-ip') {
      document.getElementById('create-kvm-ip-feedback').textContent = '';
    }
  } else {
    input.value = '';
    input.readOnly = false;
    input.classList.remove('bg-light');
    input.focus();
  }
}

// 하드웨어 IP 스캔 기능 (Update 모달용)
function scanHardwareIPsUpdate() {
  const matrixSelect = document.getElementById('matrix-ip-select-u');
  const kvmSelect = document.getElementById('kvm-ip-select-u');
  const scanBtn = document.getElementById('scan-ip-btn-u');

  matrixSelect.innerHTML = '<option value="">스캔 중...</option>';
  kvmSelect.innerHTML = '<option value="">스캔 중...</option>';
  matrixSelect.disabled = true;
  kvmSelect.disabled = true;
  scanBtn.disabled = true;
  scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 검색 중...';

  fetch('/api/scan_kvm_devices/')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.devices && data.devices.length > 0) {
          updateIPDropdownsU(data.devices);
          console.log(`${data.devices.length}개의 장비를 찾았습니다.`);
        } else {
          matrixSelect.innerHTML = '<option value="">장비를 찾을 수 없습니다</option>';
          kvmSelect.innerHTML = '<option value="">장비를 찾을 수 없습니다</option>';
          console.log('하드웨어 장비를 찾을 수 없습니다.');
        }
      })
      .catch(err => {
        console.error('IP 스캔 오류(수정 모달):', err);
        matrixSelect.innerHTML = '<option value="">스캔 실패</option>';
        kvmSelect.innerHTML = '<option value="">스캔 실패</option>';
        alert('IP 스캔 중 오류가 발생했습니다.');
      })
      .finally(() => {
        matrixSelect.disabled = false;
        kvmSelect.disabled = false;
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i class="fas fa-search"></i> 하드웨어 IP 검색';
      });
}

// IP 드롭다운 업데이트 함수 (Update용)
function updateIPDropdownsU(devices) {
  const matrixSelect = document.getElementById('matrix-ip-select-u');
  const kvmSelect = document.getElementById('kvm-ip-select-u');

  let options = '<option value="">직접 입력</option>';
  devices.forEach(ip => {
    options += `<option value="${ip}">${ip}</option>`;
  });

  matrixSelect.innerHTML = options;
  kvmSelect.innerHTML = options;
}

// IP 선택 변경 함수 (Update용)
function onIPSelectChangeU(selectId, inputId) {
  const select = document.getElementById(selectId);
  const input = document.getElementById(inputId);

  if (select.value) {
    input.value = select.value.trim();
    input.readOnly = true;
    input.classList.add('bg-light');
    input.classList.remove('is-invalid');

    if (inputId === 'update-input-matrix-ip') {
      const fb = document.getElementById('update-matrix-ip-feedback');
      if (fb) fb.textContent = '';
    } else if (inputId === 'update-input-kvm-ip') {
      const fb = document.getElementById('update-kvm-ip-feedback');
      if (fb) fb.textContent = '';
    }
  } else {
    input.value = '';
    input.readOnly = false;
    input.classList.remove('bg-light');
    input.focus();
  }
}