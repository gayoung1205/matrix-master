let selection = { startX: -1, startY: -1, endX: -1, endY: -1 };
let isDragging = false;
let dragStartCell = null;

// CSRF 토큰 (쿠키에서 읽기)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken');  // ✅ 여기서 한 번만 선언

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    initDragSelection();
    initButtons();
    updateModeDisplay();
    loadVideoWallList();
});

// Toast 알림
function showToast(message, type = 'info') {
    const toast = document.getElementById('toastNotification');
    const toastBody = document.getElementById('toastMessage');
    if (!toast || !toastBody) return;

    toastBody.textContent = message;

    toast.classList.remove('bg-success', 'bg-danger', 'bg-info');
    if (type === 'success') toast.classList.add('bg-success', 'text-white');
    else if (type === 'error') toast.classList.add('bg-danger', 'text-white');

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// 모드 조회 중복 방지
let isModeLoading = false;

function updateModeDisplay() {
    if (isModeLoading) return;  // 이미 로딩 중이면 무시
    isModeLoading = true;

    fetch('/api/device_mode/')
        .then(response => response.json())
        .then(data => {
            const modeText = document.getElementById('currentModeText');
            const alert = document.getElementById('modeAlert');

            if (data.success) {
                modeText.textContent = data.mode_name + ' 모드';
                alert.className = data.mode === 1
                    ? 'alert alert-success d-flex align-items-center justify-content-between mb-4'
                    : 'alert alert-info d-flex align-items-center justify-content-between mb-4';

                const badge = document.getElementById('deviceModeBadge');
                if (badge) {
                    badge.textContent = data.mode_name;
                    badge.className = data.mode === 1
                        ? 'badge bg-success ms-1'
                        : 'badge bg-secondary ms-1';
                }
            } else {
                modeText.textContent = '연결 실패';
            }
        })
        .catch(err => {
            const modeText = document.getElementById('currentModeText');
            if (modeText) modeText.textContent = '연결 실패';
            console.log('모드 조회 실패:', err);
        })
        .finally(() => {
            isModeLoading = false;  // 완료 후 플래그 해제
        });
}

// 모드 전환
function switchMode(mode) {
    fetch('/api/toggle_mode/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ mode: mode })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                updateModeDisplay();
            } else {
                showToast('모드 전환 실패: ' + data.error, 'error');
            }
        })
        .catch(err => {
            showToast('통신 오류', 'error');
        });
}

// 모니터 좌표 → 번호
function coordToMonitor(x, y) {
    return y * 4 + x + 1;
}

// 선택 영역 업데이트
function updateSelection() {
    // 모든 셀 선택 해제
    document.querySelectorAll('.monitor-cell').forEach(cell => {
        cell.classList.remove('selected');
    });

    const selectionText = document.getElementById('selectionText');
    const createBtn = document.getElementById('createVideoWallBtn');
    const applyBtn = document.getElementById('applyDirectBtn');

    if (selection.startX < 0) {
        if (selectionText) selectionText.textContent = '드래그하여 영역을 선택하세요 (직사각형 형태)';
        if (createBtn) createBtn.disabled = true;
        if (applyBtn) applyBtn.disabled = true;
        return;
    }

    // 정규화 (시작점이 끝점보다 클 수 있음)
    const minX = Math.min(selection.startX, selection.endX);
    const maxX = Math.max(selection.startX, selection.endX);
    const minY = Math.min(selection.startY, selection.endY);
    const maxY = Math.max(selection.startY, selection.endY);

    // 선택된 셀 표시
    const selectedMonitors = [];
    for (let y = minY; y <= maxY; y++) {
        for (let x = minX; x <= maxX; x++) {
            const monitor = coordToMonitor(x, y);
            selectedMonitors.push(monitor);
            const cell = document.querySelector(`.monitor-cell[data-monitor="${monitor}"]`);
            if (cell) cell.classList.add('selected');
        }
    }

    // 정보 업데이트
    const width = maxX - minX + 1;
    const height = maxY - minY + 1;
    if (selectionText) {
        selectionText.textContent = `${width}×${height} 비디오월 (모니터: ${selectedMonitors.join(', ')})`;
    }

    // 버튼 활성화 (최소 2개 이상)
    const isValid = selectedMonitors.length >= 2;
    if (createBtn) createBtn.disabled = !isValid;
    if (applyBtn) applyBtn.disabled = !isValid;

    // 정규화된 값 저장
    selection.startX = minX;
    selection.startY = minY;
    selection.endX = maxX;
    selection.endY = maxY;
}

// 드래그 선택 초기화
function initDragSelection() {
    const grid = document.getElementById('videowallGrid');
    if (!grid) return;

    grid.addEventListener('mousedown', function(e) {
        const cell = e.target.closest('.monitor-cell');
        if (!cell) return;

        isDragging = true;
        dragStartCell = cell;

        selection.startX = parseInt(cell.dataset.x);
        selection.startY = parseInt(cell.dataset.y);
        selection.endX = selection.startX;
        selection.endY = selection.startY;

        updateSelection();
    });

    grid.addEventListener('mousemove', function(e) {
        if (!isDragging) return;

        const cell = e.target.closest('.monitor-cell');
        if (!cell) return;

        selection.endX = parseInt(cell.dataset.x);
        selection.endY = parseInt(cell.dataset.y);

        updateSelection();
    });

    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            dragStartCell = null;
        }
    });
}

// 프리셋 선택
function selectPreset(preset) {
    switch(preset) {
        case '2x2':
            selection = { startX: 0, startY: 0, endX: 1, endY: 1 };
            break;
        case '2x4':
            selection = { startX: 0, startY: 0, endX: 3, endY: 1 };
            break;
        case '4x4':
            selection = { startX: 0, startY: 0, endX: 3, endY: 3 };
            break;
    }
    updateSelection();
}

// 선택 초기화
function clearSelection() {
    selection = { startX: -1, startY: -1, endX: -1, endY: -1 };
    updateSelection();
}

// 버튼 이벤트 초기화
function initButtons() {
    // 선택 초기화
    const clearBtn = document.getElementById('clearSelectionBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearSelection);
    }

    // 비디오월 저장
    const createBtn = document.getElementById('createVideoWallBtn');
    if (createBtn) {
        createBtn.addEventListener('click', createVideoWall);
    }

    // 바로 적용
    const applyBtn = document.getElementById('applyDirectBtn');
    if (applyBtn) {
        applyBtn.addEventListener('click', applyDirect);
    }

    // 비디오월 해제
    const releaseBtn = document.getElementById('releaseVideoWallBtn');
    if (releaseBtn) {
        releaseBtn.addEventListener('click', releaseVideoWall);
    }

    // 모드 전환 버튼
    const matrixBtn = document.getElementById('switchToMatrixBtn');
    const splicerBtn = document.getElementById('switchToSplicerBtn');
    if (matrixBtn) matrixBtn.addEventListener('click', () => switchMode(0));
    if (splicerBtn) splicerBtn.addEventListener('click', () => switchMode(1));
}

// 비디오월 저장
function createVideoWall() {
    const nameInput = document.getElementById('videoWallName');
    const name = nameInput?.value.trim();

    if (!name) {
        showToast('비디오월 이름을 입력해주세요.', 'error');
        nameInput?.focus();
        return;
    }

    const inputSource = parseInt(document.getElementById('inputSourceSelect')?.value || 1);

    fetch('/api/video_wall/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            name: name,
            start_x: selection.startX,
            start_y: selection.startY,
            end_x: selection.endX,
            end_y: selection.endY,
            input_source: inputSource
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                if (nameInput) nameInput.value = '';
                loadVideoWallList();
            } else {
                showToast(data.error, 'error');
            }
        })
        .catch(err => {
            showToast('저장 실패', 'error');
        });
}

// 바로 적용
function applyDirect() {
    const inputSource = parseInt(document.getElementById('inputSourceSelect')?.value || 1);

    // 임시 생성 후 바로 적용
    fetch('/api/video_wall/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            name: '_temp_' + Date.now(),
            start_x: selection.startX,
            start_y: selection.startY,
            end_x: selection.endX,
            end_y: selection.endY,
            input_source: inputSource
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return fetch(`/api/video_wall/apply/${data.id}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken }
                });
            }
            throw new Error(data.error);
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('비디오월이 적용되었습니다!', 'success');
                updateModeDisplay();
            } else {
                showToast(data.error, 'error');
            }
        })
        .catch(err => {
            showToast('적용 실패: ' + err.message, 'error');
        });
}

// 비디오월 해제
function releaseVideoWall() {
    if (!confirm('비디오월을 해제하고 Matrix 모드로 복귀하시겠습니까?')) return;

    fetch('/api/video_wall/release/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                updateModeDisplay();
            } else {
                showToast(data.error, 'error');
            }
        });
}

// 비디오월 목록 로드
function loadVideoWallList() {
    fetch('/api/video_wall/list/')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('videoWallList');
            if (!list) return;

            if (!data.success || data.video_walls.length === 0) {
                list.innerHTML = `
                    <div class="list-group-item text-center text-muted py-4">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p class="mb-0">저장된 비디오월이 없습니다</p>
                    </div>
                `;
                return;
            }

            list.innerHTML = data.video_walls.map(vw => `
                <div class="videowall-item">
                    <div class="videowall-item-info">
                        <div class="videowall-item-name">${escapeHtml(vw.name)}</div>
                        <div class="videowall-item-details">
                            ${vw.size} · Device ${String(vw.input_source).padStart(2, '0')} · 
                            모니터 ${vw.monitors.join(',')}
                        </div>
                    </div>
                    <div class="videowall-item-actions">
                        <button class="btn btn-primary btn-sm" onclick="applyVideoWall(${vw.id})">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteVideoWall(${vw.id}, '${escapeHtml(vw.name)}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        });
}

// 비디오월 적용
function applyVideoWall(id) {
    fetch(`/api/video_wall/apply/${id}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                updateModeDisplay();
            } else {
                showToast(data.error, 'error');
            }
        });
}

// 비디오월 삭제
function deleteVideoWall(id, name) {
    if (!confirm(`"${name}" 비디오월을 삭제하시겠습니까?`)) return;

    fetch(`/api/video_wall/delete/${id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': csrfToken }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                loadVideoWallList();
            } else {
                showToast(data.error, 'error');
            }
        });
}

// HTML 이스케이프
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}