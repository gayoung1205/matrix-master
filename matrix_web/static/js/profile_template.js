function profileCreate() {
  let name = $('input[id=input-name-create]');

  // 이름 입력이 없을 경우
  if (name.val().length === 0) {
    name.addClass('is-invalid');
    name[0].scrollIntoView();
    return;
  }

  // 이름 입력시 "," 허용X
  if (name.val().includes(',')) {
    name.addClass('is-invalid');
    $('#name-feedback').text('"," 은 허용되지 않은 문자입니다.');
    name[0].scrollIntoView();
    return;
  } else {
    if (name.hasClass('is-invalid')) {
      name.removeClass('is-invalid');
      $('#name-feedback').text('');
    }
  }

  // 시스템 아이디 정렬
  let idList = new Array();
  $('.system-id').each(function (index, item) {
    idList.push($(item).val());
  });
  $('#mat-id-list').val(idList);

  // 시스템 input-1 ~ input-16 정렬 (16포트 지원)
  let selectList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'];
  for (const i in selectList) {
    let inputList = new Array();
    $(`.select-${selectList[i]} option:selected`).each(function (index, item) {
      inputList.push($(item).val());
    });
    $(`#input-${selectList[i]}`).val(inputList);
  }

  // 시스템 kvm 값 정렬
  let kvmList = new Array();
  $('.input-kvm option:selected').each(function (index, item) {
    kvmList.push($(item).val());
  });
  $('#input-kvm').val(kvmList);

  $('#profile-create-form').submit();
}

$('#profile-delete').on('show.bs.modal', function (event) {
  let button = $(event.relatedTarget); // Button that triggered the modal
  let delete_id = button.data('whatever'); // Extract info from data-* attributes
  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  let modal = $(this);
  modal.find('#delete-id').val(delete_id);
});

function profileExport() {
  let list = new Array();
  $('input[name=profile_check]').each(function (index, item) {
    if ($(item).is(':checked')) {
      list.push($(item).val());
    }
  });

  if (list.length > 0) {
    $('#export_pro_list').val(list);
    $('#profileExportForm').submit();
    $('#profileExport').modal('hide');
  } else {
    $('#export_pro_list').addClass('is-invalid');
  }
}

function profileImport() {
  let file = $('#formFile');
  if (file.val().length < 1) {
    $('#formFile').addClass('is-invalid');
    $('#file-feedback').text('파일을 선택해주세요.');
    return;
  }

  let ext = file.val().split('.').pop().toLowerCase();
  if ($.inArray(ext, ['csv']) == -1) {
    file.val(''); // input file 파일명을 다시 지워준다.
    $('#formFile').addClass('is-invalid');
    $('#file-feedback').text('.csv 파일 형식만 가능합니다.');
    return;
  }

  $('#profileImportForm').submit();
  $('#profileImport').modal('hide');
}

// id == profile id (string), name == profile name (string)
function getProfileRequest(id, name) {
  let host = window.location.host;

  $.ajax({
    type: 'GET',
    url: `http://${host}/api/profile/?id=${id}`,
    success: function (res) {
      $('#profile-update').modal('show');
      profileUpdateModalHandler(id, name, res);
    },
    error: function (err) {
      $('#errorModal').modal('show');
      $('#errorModal .modal-body span').text(JSON.stringify(err.responseText));
    },
  });
}

function forceCloseModal() {
  $('#profile-update').modal('hide');

  // 추가로 강제로 닫는 안전 처리
  setTimeout(() => {
    $('#profile-update').removeClass('show')
        .css('display', 'none')
        .attr('aria-hidden', 'true')
        .removeAttr('aria-modal')
        .removeAttr('role');
    $('.modal-backdrop').remove();
    $('body').removeClass('modal-open').css('padding-right', '');
  }, 300);  // Bootstrap 트랜지션 시간 후 적용
}

// id == profile id (string), name == profile name (string), re == systemSetting data (object),
function profileUpdateModalHandler(id, name, res) {
  $('#update-id').attr('value', id);
  $('#input-name-update').attr('value', name);

  let len = $('.update-system-id').length;
  console.log(len);
  // 16포트를 지원하기 위해 input_a부터 input_p까지 확장
  let inputList = ['input_a', 'input_b', 'input_c', 'input_d', 'input_e', 'input_f', 'input_g', 'input_h', 'input_i', 'input_j', 'input_k', 'input_l', 'input_m', 'input_n', 'input_o', 'input_p'];
  for (let systemIndex = 0; systemIndex < len; systemIndex++) {
    // matrix input setting. input_a ~ input_p (16포트)
    for (let inputIndex = 0; inputIndex < inputList.length; inputIndex++) {
      let selectVal = Number(res[systemIndex][inputList[inputIndex]]);
      $(`#update-input-select-${res[systemIndex].matrix}-${inputIndex + 1} option:eq(${selectVal})`)
          .prop('selected', 'selected')
          .change();
    }

    // kvm input setting
    let selectVal = Number(res[systemIndex]['input_kvm']);
    let mainConnect = res[systemIndex]['main_connect'];
    if (mainConnect) {
      $(`#update-sub-input-kvm-${mainConnect} option:eq(${selectVal})`).prop('selected', 'selected').change();
    } else {
      $(`#update-main-input-kvm option:eq(${selectVal})`).prop('selected', 'selected').change();
    }
  }
}

function profileUpdate() {
  let name = $('input[id=input-name-update]');

  // 이름 입력이 없을 경우
  if (name.val().length === 0) {
    name.addClass('is-invalid');
    name[0].scrollIntoView();
    return;
  }

  // 이름 입력시 "," 허용X
  if (name.val().includes(',')) {
    name.addClass('is-invalid');
    $('#update-name-feedback').text('"," 은 허용되지 않은 문자입니다.');
    name[0].scrollIntoView();
    return;
  } else {
    if (name.hasClass('is-invalid')) {
      name.removeClass('is-invalid');
      $('#update-name-feedback').text('');
    }
  }

  // 시스템 아이디 정렬
  let idList = new Array();
  $('.update-system-id').each(function (index, item) {
    idList.push($(item).val());
  });
  $('#update-mat-id-list').val(idList);

  // 시스템 input-1 ~ input-16 정렬 (16포트 지원)
  for (let inputNumber = 1; inputNumber < 17; inputNumber++) {
    let inputList = new Array();
    $(`.update-select-${inputNumber} option:selected`).each(function (index, item) {
      inputList.push($(item).val());
    });
    $(`#update-input-${inputNumber}`).val(inputList);
  }

  // 시스템 kvm 값 정렬
  let kvmList = new Array();
  $('.update-input-kvm option:selected').each(function (index, item) {
    kvmList.push($(item).val());
  });
  $('#update-input-kvm').val(kvmList);

  $('#profile-update-form').submit();
}

(function () {
  // ---- CSRF ----
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return '';
  }
  const csrftoken = getCookie('csrftoken');

  const tbodySel = '#profile-tbody';

  function getCurrentOrder() {
    return Array.from(document.querySelectorAll(`${tbodySel} tr[data-id]`))
        .map(tr => tr.getAttribute('data-id'));
  }

  async function postOrder(orderIds) {
    try {
      const res = await fetch('/api/profile-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
        },
        body: JSON.stringify({ order: orderIds })
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      // 응답을 꼭 JSON으로 돌려줄 필요 없으면 생략 가능
      const data = await res.json().catch(function () { return {}; });
      return data;
    } catch (err) {
      console.error('[postOrder] failed:', err);
      throw err;
    }
  }

  async function applySavedOrder() {
    try {
      const res = await fetch('/api/profile-order', {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      if (!res.ok) return;

      const data = await res.json();
      const order = Array.isArray(data.order) ? data.order.map(String) : [];
      if (!order.length) return;

      const tbody = document.querySelector(tbodySel);
      if (!tbody) return;

      // 기존 행 맵
      const map = {};
      Array.from(tbody.querySelectorAll('tr[data-id]')).forEach(function (tr) {
        map[tr.getAttribute('data-id')] = tr;
      });

      // 저장된 순서대로 재배치
      const frag = document.createDocumentFragment();
      order.forEach(function (id) {
        if (map[id]) frag.appendChild(map[id]);
      });

      // 저장에 없던(새로 추가된) 행은 뒤에 말붙임
      Array.from(tbody.querySelectorAll('tr[data-id]')).forEach(function (tr) {
        if (order.indexOf(tr.getAttribute('data-id')) === -1) {
          frag.appendChild(tr);
        }
      });

      tbody.appendChild(frag);
    } catch (err) {
      console.warn('[applySavedOrder] ignored:', err);
    }
  }

  // 드래그 정렬 + 자동 저장(디바운스)
  function setupDragSort() {
    const tbody = document.querySelector(tbodySel);
    if (!tbody) return;

    let dragEl = null;
    let saveTimer = null;
    const SAVE_DEBOUNCE_MS = 250;

    function scheduleSave() {
      if (saveTimer) clearTimeout(saveTimer);
      saveTimer = setTimeout(async function () {
        const order = getCurrentOrder();
        if (!order.length) return;
        try {
          await postOrder(order);
        } catch (err) {
          alert('자동 저장 중 오류가 발생했습니다.');
        }
      }, SAVE_DEBOUNCE_MS);
    }

    tbody.addEventListener('dragstart', function (e) {
      const tr = e.target.closest('tr[data-id]');
      if (!tr) return;
      dragEl = tr;
      tr.classList.add('dragging');
      if (e.dataTransfer) {
        e.dataTransfer.effectAllowed = 'move';
        try { e.dataTransfer.setData('text/plain', tr.dataset.id); } catch (err) {}
      }
    });

    tbody.addEventListener('dragend', function (e) {
      const tr = e.target.closest('tr[data-id]');
      if (tr) tr.classList.remove('dragging');
      Array.from(tbody.querySelectorAll('tr.drop-target')).forEach(function (el) {
        el.classList.remove('drop-target');
      });
      dragEl = null;
      scheduleSave();
    });

    tbody.addEventListener('dragover', function (e) {
      e.preventDefault();
      const tr = e.target.closest('tr[data-id]');
      if (!tr || tr === dragEl) return;

      Array.from(tbody.querySelectorAll('tr.drop-target')).forEach(function (el) {
        el.classList.remove('drop-target');
      });
      tr.classList.add('drop-target');

      const b = tr.getBoundingClientRect();
      const offset = e.clientY - b.top;
      const before = offset < b.height / 2;
      if (before) tbody.insertBefore(dragEl, tr);
      else tbody.insertBefore(dragEl, tr.nextSibling);
    });

    tbody.addEventListener('drop', function (e) {
      e.preventDefault();
      Array.from(tbody.querySelectorAll('tr.drop-target')).forEach(function (el) {
        el.classList.remove('drop-target');
      });
      scheduleSave();
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    applySavedOrder();
    setupDragSort();
  });
})();

// 프로필 실행 함수 (즐겨찾기 버튼 클릭 시 사용)
function profileControl(profileId) {
  if (!profileId) {
    alert('프로필 ID가 없습니다.');
    return;
  }

  if (confirm('이 즐겨찾기 설정을 적용하시겠습니까?\n모든 연결된 장비의 입력이 변경됩니다.')) {
    // 버튼 상태 변경 (실행 중 표시)
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '실행 중...';
    button.disabled = true;

    // 프로필 실행 요청
    window.location.href = `/control/profile/?id=${profileId}`;

    // 잠시 후 버튼 상태 복원 (페이지 리로드로 인해 실제론 불필요)
    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 2000);
  }
}

// AJAX 방식으로 프로필 실행 (페이지 리로드 없이)
function profileControlAjax(profileId) {
  if (!profileId) {
    alert('프로필 ID가 없습니다.');
    return;
  }

  if (confirm('이 즐겨찾기 설정을 적용하시겠습니까?\n모든 연결된 장비의 입력이 변경됩니다.')) {
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = '실행 중...';
    button.disabled = true;

    fetch(`/control/profile/?id=${profileId}`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
        .then(response => {
          if (response.ok) {
            alert('즐겨찾기가 성공적으로 적용되었습니다.');
            // 필요시 하드웨어 상태 업데이트
            if (typeof updateHardwareStatus === 'function') {
              updateHardwareStatus();
            }
          } else {
            throw new Error('서버 오류');
          }
        })
        .catch(error => {
          console.error('Profile control error:', error);
          alert('즐겨찾기 적용 중 오류가 발생했습니다.');
        })
        .finally(() => {
          button.textContent = originalText;
          button.disabled = false;
        });
  }
}