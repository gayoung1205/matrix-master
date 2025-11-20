$(document).ready(function() {
    loadCurrentKvmState();

    // ========== 1. Select 박스 변경 이벤트 (장비 연동) ==========
    $(document).on('change', 'select[name="input_select"]', function() {
        const selectElement = $(this);
        const selectId = selectElement.attr('id');
        const selectedValue = selectElement.val();

        const matches = selectId.match(/input_select-(\d+)-(\d+)/);
        if (!matches) {
            console.error('Invalid select ID format:', selectId);
            return;
        }

        const target = matches[1];
        const matrixId = matches[2];
        const input = selectedValue;

        selectElement.prop('disabled', true);
        const originalBg = selectElement.css('background-color');
        selectElement.css('background-color', '#ffffcc');

        $.ajax({
            url: '/control/',
            type: 'GET',
            data: {
                id: matrixId,
                target: target,
                input: input
            },
            success: function(response) {
                selectElement.css('background-color', '#d4edda');
                setTimeout(function() {
                    selectElement.css('background-color', originalBg);
                }, 1000);
            },
            error: function(xhr, status, error) {
                console.error('장비 설정 실패:', error);
                selectElement.css('background-color', '#f8d7da');
                alert('장비 설정에 실패했습니다: ' + (xhr.responseJSON?.error || error));
                setTimeout(function() {
                    selectElement.css('background-color', originalBg);
                }, 2000);
            },
            complete: function() {
                selectElement.prop('disabled', false);
            }
        });
    });

    // ========== 2. KVM 버튼 클릭 이벤트 (장비 연동) ==========
    $(document).on('click', 'button[name="kvm_button"]', function() {
        const button = $(this);
        const buttonValue = button.val();
        const parts = buttonValue.split('-');

        if (parts.length !== 2) {
            console.error('Invalid button value:', buttonValue);
            return;
        }

        const matrixId = parts[0];
        const channel = parts[1];

        const allButtons = $(`button[name="kvm_button"][value^="${matrixId}-"]`);
        allButtons.prop('disabled', true);

        $.ajax({
            url: '/kvm/',
            type: 'GET',
            data: {
                id: matrixId,
                input: channel
            },
            success: function(response) {
                allButtons.removeClass('btn-gradient active-kvm')
                    .addClass('btn-outline-gradient');
                button.removeClass('btn-outline-gradient')
                    .addClass('btn-gradient active-kvm');
                localStorage.setItem(`kvm_state_${matrixId}`, channel);
                showToast('success', `KVM 채널 ${channel}로 전환되었습니다.`);
            },
            error: function(xhr, status, error) {
                console.error('KVM 전환 실패:', error);
                showToast('error', 'KVM 전환에 실패했습니다.');
            },
            complete: function() {
                allButtons.prop('disabled', false);
            }
        });
    });

    // ========== 3. 프로필(즐겨찾기) 버튼 클릭 이벤트 ==========
    $(document).on('click', 'button[name="profile_button"]', function() {
        const profileId = $(this).val();
        const profileName = $(this).text().trim();

        showToast('info', `"${profileName}" 적용 중...`);

        $.ajax({
            type: 'GET',
            url: `/api/profile/?id=${profileId}`,
            success: function(profileData) {
                applyProfileToDevice(profileData, profileName);
            },
            error: function(xhr, status, error) {
                console.error('프로필 로드 실패:', error);
                showToast('error', '프로필을 불러오는데 실패했습니다.');
            }
        });
    });
});

// ========== 페이지 로드 시 KVM 상태 복원 ==========
function loadCurrentKvmState() {
    // 모든 KVM 버튼을 비활성 상태로 초기화
    $('button[name="kvm_button"]').removeClass('btn-gradient active-kvm')
        .addClass('btn-outline-gradient');

    // localStorage에 저장된 상태 복원
    $('button[name="kvm_button"]').each(function() {
        const button = $(this);
        const value = button.val();
        const parts = value.split('-');

        if (parts.length === 2) {
            const matrixId = parts[0];
            const channel = parts[1];
            const savedState = localStorage.getItem(`kvm_state_${matrixId}`);

            if (savedState === channel) {
                button.removeClass('btn-outline-gradient')
                    .addClass('btn-gradient active-kvm');
            }
        }
    });
}

// ========== 프로필을 실제 장비에 적용하는 함수 ==========
function applyProfileToDevice(profileData, profileName) {
    const matrixCommands = {};

    // 프로필 데이터를 매트릭스별로 그룹화
    profileData.forEach(function(setting) {
        const matrixId = setting.matrix;

        if (!matrixCommands[matrixId]) {
            matrixCommands[matrixId] = {
                matrixId: matrixId,
                inputs: {},
                kvmValue: null
            };
        }

        const inputKeys = ['input_a', 'input_b', 'input_c', 'input_d',
            'input_e', 'input_f', 'input_g', 'input_h',
            'input_i', 'input_j', 'input_k', 'input_l',
            'input_m', 'input_n', 'input_o', 'input_p'];

        inputKeys.forEach(function(key, index) {
            const inputValue = setting[key];
            const targetNumber = index + 1;

            if (inputValue && inputValue !== '00') {
                matrixCommands[matrixId].inputs[targetNumber] = inputValue;
            }
        });

        const kvmValue = setting.input_kvm;
        if (kvmValue && kvmValue !== '00') {
            matrixCommands[matrixId].kvmValue = kvmValue;
        }
    });

    const matrixIds = Object.keys(matrixCommands);
    let currentMatrixIndex = 0;
    let totalSuccess = 0;
    let totalFail = 0;

    function processNextMatrix() {
        if (currentMatrixIndex >= matrixIds.length) {
            // 모든 매트릭스 처리 완료
            if (totalFail === 0) {
                showToast('success', `"${profileName}" 프로필이 적용되었습니다.`);
            } else {
                showToast('warning', `"${profileName}" 프로필 적용 완료 (${totalFail}개 실패)`);
            }
            return;
        }

        const matrixId = matrixIds[currentMatrixIndex];
        const cmd = matrixCommands[matrixId];
        currentMatrixIndex++;

        const inputValues = Object.values(cmd.inputs);
        const allSame = inputValues.length > 0 && inputValues.every(v => v === inputValues[0]);

        if (allSame && inputValues.length === 16) {
            // ALL 명령 사용 (모든 포트가 동일한 입력)
            const inputValue = inputValues[0];

            $.ajax({
                url: '/api/control_all/',
                type: 'GET',
                data: {
                    id: matrixId,
                    input: inputValue
                },
                success: function(response) {
                    totalSuccess++;
                    $(`select[name="input_select"][id$="-${matrixId}"]`).val(inputValue);

                    if (cmd.kvmValue) {
                        processKVM(matrixId, cmd.kvmValue, processNextMatrix);
                    } else {
                        setTimeout(processNextMatrix, 100);
                    }
                },
                error: function(xhr, status, error) {
                    console.error(`ALL 명령 실패: Matrix ${matrixId}`, error);
                    totalFail++;
                    setTimeout(processNextMatrix, 100);
                }
            });
        } else {
            // 개별 명령
            const targets = Object.keys(cmd.inputs).sort((a, b) => a - b);
            let targetIndex = 0;

            function processNextTarget() {
                if (targetIndex >= targets.length) {
                    if (cmd.kvmValue) {
                        processKVM(matrixId, cmd.kvmValue, processNextMatrix);
                    } else {
                        setTimeout(processNextMatrix, 100);
                    }
                    return;
                }

                const target = targets[targetIndex];
                const inputValue = cmd.inputs[target];
                targetIndex++;

                $.ajax({
                    url: '/control/',
                    type: 'GET',
                    data: {
                        id: matrixId,
                        target: String(target).padStart(2, '0'),
                        input: inputValue
                    },
                    success: function(response) {
                        totalSuccess++;

                        const selectElement = $(`select[name="input_select"][id*="-${String(target).padStart(2, '0')}-${matrixId}"]`);
                        if (selectElement.length > 0) {
                            selectElement.val(inputValue);
                        }

                        setTimeout(processNextTarget, 100);
                    },
                    error: function(xhr, status, error) {
                        console.error(`개별 명령 실패: target=${target}`, error);
                        totalFail++;
                        setTimeout(processNextTarget, 100);
                    }
                });
            }

            processNextTarget();
        }
    }

    function processKVM(matrixId, kvmValue, callback) {
        $.ajax({
            url: '/kvm/',
            type: 'GET',
            data: {
                id: matrixId,
                input: kvmValue
            },
            success: function(response) {
                totalSuccess++;

                const kvmNum = parseInt(kvmValue, 10);

                // 해당 매트릭스의 모든 KVM 버튼 비활성화
                const allKvmButtons = $(`button[name="kvm_button"]`).filter(function() {
                    const val = $(this).val();
                    if (!val) return false;
                    const parts = val.split('-');
                    return parts.length === 2 && parts[0] === String(matrixId);
                });

                allKvmButtons.removeClass('btn-gradient active-kvm')
                    .addClass('btn-outline-gradient');

                // 선택된 KVM 버튼만 활성화
                const targetValue = `${matrixId}-${kvmNum}`;
                const activeButton = $(`button[name="kvm_button"][value="${targetValue}"]`).first();

                if (activeButton.length > 0) {
                    activeButton.removeClass('btn-outline-gradient')
                        .addClass('btn-gradient active-kvm');
                    localStorage.setItem(`kvm_state_${matrixId}`, String(kvmNum));
                }

                setTimeout(callback, 100);
            },
            error: function(xhr, status, error) {
                console.error(`KVM 설정 실패: Matrix ${matrixId}`, error);
                totalFail++;
                setTimeout(callback, 100);
            }
        });
    }

    processNextMatrix();
}

// ========== 토스트 메시지 표시 함수 ==========
function showToast(type, message) {
    const bgColor = type === 'success' ? '#28a745' : (type === 'warning' ? '#ffc107' : '#dc3545');
    const icon = type === 'success' ? 'fa-check-circle' : (type === 'warning' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle');

    const toast = $(`
        <div class="custom-toast" style="
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideInToast 0.3s ease-out;
        ">
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        </div>
    `);

    $('body').append(toast);

    setTimeout(function() {
        toast.fadeOut(300, function() {
            $(this).remove();
        });
    }, 3000);
}

// ========== 애니메이션 스타일 추가 ==========
if (!$('#toast-animation-style').length) {
    $('<style id="toast-animation-style">')
        .text(`
            @keyframes slideInToast {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `)
        .appendTo('head');
}