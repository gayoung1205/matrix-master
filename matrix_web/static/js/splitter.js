/**
 * Splitter 테스트 UI JavaScript
 *
 * 프로토콜: 55 AA 04 15 XX CRC EE
 * XX = (mode << 4) | (input - 1)
 *   - Bit7-Bit4: 윈도우 모드 (0=1분할, 1=2분할, 2=4분할, 3=16분할)
 *   - Bit3-Bit0: 입력 소스 (0~15 = Input 1~16)
 */

// CSRF 토큰
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

// 현재 상태
let currentMode = 0;      // 0=1분할, 1=2분할, 2=4분할, 3=16분할
let currentInput = 1;     // 1~16

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    initModeButtons();
    initInputSelect();
    initActionButtons();
    initModeButtons2();
    updatePreview();
    updateCommandInfo();
    addLog('info', 'Splitter 테스트 UI 초기화 완료');
});

/**
 * 모드 버튼 초기화
 */
function initModeButtons() {
    const buttons = document.querySelectorAll('.btn-mode');
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            // 활성 상태 변경
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // 모드 업데이트
            currentMode = parseInt(this.dataset.mode);
            updatePreview();
            updateCommandInfo();

            const windowCount = this.dataset.windows;
            addLog('info', `분할 모드 변경: ${windowCount}분할 (mode=${currentMode})`);
        });
    });
}

/**
 * 입력 소스 선택 초기화
 */
function initInputSelect() {
    const select = document.getElementById('inputSourceSelect');
    if (select) {
        select.addEventListener('change', function() {
            currentInput = parseInt(this.value);
            updateCommandInfo();
            addLog('info', `입력 소스 변경: Input ${currentInput.toString().padStart(2, '0')}`);
        });
    }
}

/**
 * 액션 버튼 초기화
 */
function initActionButtons() {
    const sendBtn = document.getElementById('sendTestBtn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendTestCommand);
    }

    const clearBtn = document.getElementById('clearLogBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearLog);
    }
}

/**
 * 미리보기 업데이트
 */
function updatePreview() {
    const preview = document.getElementById('splitterPreview');
    if (!preview) return;

    // 기존 클래스 제거
    preview.classList.remove('mode-1', 'mode-2', 'mode-4', 'mode-16');

    // 윈도우 수 결정
    const windowCounts = [1, 2, 4, 16];
    const windowCount = windowCounts[currentMode];

    // 새 클래스 추가
    preview.classList.add(`mode-${windowCount}`);

    // 셀 생성
    let cellsHtml = '';
    for (let i = 0; i < windowCount; i++) {
        cellsHtml += `
            <div class="preview-cell${i === 0 ? ' active' : ''}" data-index="${i}">
                <span class="preview-number">${i + 1}</span>
            </div>
        `;
    }
    preview.innerHTML = cellsHtml;
}

/**
 * 명령어 정보 업데이트
 */
function updateCommandInfo() {
    const windowCounts = [1, 2, 4, 16];
    const windowCount = windowCounts[currentMode];

    // 데이터 바이트 계산
    const inputValue = currentInput - 1;  // 0-based
    const reversedMode = 3 - currentMode;  // 0→3, 1→2, 2→1, 3→0
    const dataByte = (reversedMode << 4) | inputValue;

    // CRC 계산: 모든 바이트 합의 하위 8비트
    const bytes = [0x55, 0xAA, 0x04, 0x15, dataByte];
    const crc = bytes.reduce((sum, b) => sum + b, 0) & 0xFF;

    // 전체 명령어
    const fullCommand = [...bytes, crc, 0xEE];
    const commandHex = fullCommand.map(b => b.toString(16).toUpperCase().padStart(2, '0')).join(' ');

    // UI 업데이트
    document.getElementById('cmdMode').textContent = `${currentMode} (${windowCount}분할)`;
    document.getElementById('cmdInput').textContent = `${inputValue} (Input ${currentInput})`;
    document.getElementById('cmdData').textContent = `0x${dataByte.toString(16).toUpperCase().padStart(2, '0')}`;
    document.getElementById('cmdFull').textContent = commandHex;
}

/**
 * 테스트 명령 전송
 */
async function sendTestCommand() {
    const windowCounts = [1, 2, 4, 16];
    const windowCount = windowCounts[currentMode];

    addLog('info', `=== Splitter 테스트 시작 ===`);
    updateStatus('전송 중...', 'warning');

    try {
        // 1. 먼저 Splicer 모드로 전환 (Splitter는 이 모드에서 동작)
        addLog('send', '1단계: Splicer/Splitter 모드로 전환 (0x00)');

        const modeResponse = await fetch('/api/toggle_mode/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ mode: 1 })  // Splicer 모드
        });

        const modeData = await modeResponse.json();
        if (modeData.success) {
            addLog('success', `모드 전환: ${modeData.mode_name}`);
        } else {
            addLog('error', `모드 전환 실패: ${modeData.error}`);
        }

        // 잠시 대기
        await new Promise(resolve => setTimeout(resolve, 300));

        // 2. Splitter 명령 전송
        const inputValue = currentInput - 1;
        const dataByte = (currentMode << 4) | inputValue;
        const bytes = [0x55, 0xAA, 0x04, 0x15, dataByte];
        const crc = bytes.reduce((sum, b) => sum + b, 0) & 0xFF;
        const fullCommand = [...bytes, crc, 0xEE];
        const commandHex = fullCommand.map(b => b.toString(16).toUpperCase().padStart(2, '0')).join(' ');

        addLog('send', `2단계: Splitter 명령 - ${commandHex}`);
        addLog('info', `모드: ${windowCount}분할, 입력: Input ${currentInput}`);

        const response = await fetch('/api/splitter/test/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                mode: currentMode,
                input_source: currentInput
            })
        });

        const data = await response.json();

        if (data.success) {
            addLog('success', `성공: ${data.message}`);
            if (data.response_hex && data.response_hex !== 'No response') {
                addLog('receive', `응답: ${data.response_hex}`);
            } else {
                addLog('info', `응답 없음 (명령은 전송됨)`);
            }
            updateStatus('성공', 'success');
            showToast('Splitter 명령 전송 완료!', 'success');
        } else {
            addLog('error', `실패: ${data.error}`);
            updateStatus('실패', 'danger');
            showToast(data.error, 'error');
        }

        addLog('info', `=== Splitter 테스트 완료 ===`);

    } catch (error) {
        addLog('error', `오류: ${error.message}`);
        updateStatus('오류', 'danger');
        showToast('통신 오류', 'error');
    }
}

/**
 * 로그 추가
 */
function addLog(type, message) {
    const logContainer = document.getElementById('testLog');
    if (!logContainer) return;

    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];

    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `
        <span class="log-time">${timeStr}</span>
        <span class="log-message">${message}</span>
    `;

    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

/**
 * 로그 지우기
 */
function clearLog() {
    const logContainer = document.getElementById('testLog');
    if (logContainer) {
        logContainer.innerHTML = `
            <div class="log-entry log-info">
                <span class="log-time">${new Date().toTimeString().split(' ')[0]}</span>
                <span class="log-message">로그가 초기화되었습니다</span>
            </div>
        `;
    }
}

/**
 * 상태 업데이트
 */
function updateStatus(text, type) {
    const badge = document.getElementById('statusBadge');
    const statusText = document.getElementById('statusText');

    if (badge) {
        badge.className = `badge bg-${type}`;
    }
    if (statusText) {
        statusText.textContent = text;
    }
}

/**
 * Toast 알림
 */
function showToast(message, type) {
    const toastEl = document.getElementById('toastNotification');
    const toastBody = document.getElementById('toastMessage');

    if (!toastEl || !toastBody) return;

    toastEl.className = `toast bg-${type === 'error' ? 'danger' : type}`;

    const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
    toastBody.innerHTML = `<i class="fas fa-${icon} me-2"></i>${message}`;

    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();
}

// ============================================
// 모드 전환 기능
// ============================================

/**
 * 모드 전환 버튼 초기화
 */
function initModeButtons2() {
    const matrixBtn = document.getElementById('switchToMatrixBtn');
    const splicerBtn = document.getElementById('switchToSplicerBtn');
    const splitterBtn = document.getElementById('switchToSplitterBtn');

    if (matrixBtn) {
        matrixBtn.addEventListener('click', () => switchModeToggle(0, 'Matrix'));
    }
    if (splicerBtn) {
        splicerBtn.addEventListener('click', () => switchModeToggle(1, 'Splicer'));
    }
    if (splitterBtn) {
        // Splitter는 별도 테스트 (mode=2 시도)
        splitterBtn.addEventListener('click', () => switchModeToggle(2, 'Splitter'));
    }
}

/**
 * 모드 전환 (기존 toggle_mode API 사용)
 */
async function switchModeToggle(mode, modeName) {
    addLog('send', `모드 전환 → ${modeName} (mode=${mode})`);
    updateStatus('전환 중...', 'warning');

    try {
        const response = await fetch('/api/toggle_mode/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ mode: mode })
        });

        const data = await response.json();

        if (data.success) {
            addLog('success', `${data.mode_name} 모드 전환 완료`);
            addLog('info', data.message);
            updateStatus(data.mode_name, 'success');
            showToast(data.message, 'success');
        } else {
            addLog('error', `실패: ${data.error}`);
            updateStatus('실패', 'danger');
            showToast(data.error, 'error');
        }
    } catch (error) {
        addLog('error', `오류: ${error.message}`);
        updateStatus('오류', 'danger');
        showToast('통신 오류', 'error');
    }
}

/**
 * 모드 전환 명령 전송
 * 명령: 55 AA 04 0B XX CRC EE
 */
async function switchMode(modeValue, modeName) {
    // CRC 계산
    const bytes = [0x55, 0xAA, 0x04, 0x0B, modeValue];
    const crc = bytes.reduce((sum, b) => sum + b, 0) & 0xFF;
    const command = [...bytes, crc, 0xEE];
    const commandHex = command.map(b => b.toString(16).toUpperCase().padStart(2, '0')).join(' ');

    addLog('send', `모드 전환 → ${modeName}: ${commandHex}`);
    updateStatus('전환 중...', 'warning');

    try {
        const response = await fetch('/api/splitter/switch-mode/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                mode_value: modeValue,
                mode_name: modeName
            })
        });

        const data = await response.json();

        if (data.success) {
            addLog('success', `${modeName} 모드 전환 완료`);
            if (data.response_hex) {
                addLog('receive', `응답: ${data.response_hex}`);
            }
            if (data.device_mode !== undefined) {
                addLog('info', `DeviceMode 응답: raw=${data.device_mode_raw}`);
            }
            updateStatus(modeName, 'success');
            showToast(`${modeName} 모드로 전환!`, 'success');
        } else {
            addLog('error', `실패: ${data.error}`);
            updateStatus('실패', 'danger');
            showToast(data.error, 'error');
        }
    } catch (error) {
        addLog('error', `오류: ${error.message}`);
        updateStatus('오류', 'danger');
        showToast('통신 오류', 'error');
    }
}

