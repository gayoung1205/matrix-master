function profileCreate() {
  var name = $('input[id=inputName]');
  if (name.val().length === 0) {
    name.addClass('is-invalid');
    name[0].scrollIntoView();
    return;
  }

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

  var list = new Array();
  $('input[name=mat_id]').each(function (index, item) {
    list.push($(item).val());
  });
  $('#mat_id_list').val(list);

  select_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'];
  for (const i in select_list) {
    list = new Array();
    $(`select[name=${select_list[i]}] option:selected`).each(function (index, item) {
      list.push($(item).val());
    });
    $(`#input_${select_list[i]}`).val(list);
  }

  list = new Array();
  $('select[name=inputKvm] option:selected').each(function (index, item) {
    list.push($(item).val());
  });
  $('#input_kvm').val(list);

  $('#profileCreateForm').submit();
}

$('#profileDelete').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget); // Button that triggered the modal
  var delete_id = button.data('whatever'); // Extract info from data-* attributes
  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this);
  modal.find('#deleteId').val(delete_id);
});

function profileExport() {
  var list = new Array();
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

  $('#profileImportForm').submit();
  $('#profileImport').modal('hide');
}
