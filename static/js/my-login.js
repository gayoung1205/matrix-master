/******************************************
 * My Login
 *
 * Bootstrap 4 Login Page
 *
 * @author          Muhamad Nauval Azhar
 * @uri 			https://nauval.in
 * @copyright       Copyright (c) 2018 Muhamad Nauval Azhar
 * @license         My Login is licensed under the MIT license.
 * @github          https://github.com/nauvalazhar/my-login
 * @version         1.2.0
 *
 * Help me to keep this project alive
 * https://www.buymeacoffee.com/mhdnauvalazhar
 *
 ******************************************/

'use strict';

$(function () {
  $("input[type='password'][data-eye]").each(function (i) {
    var $this = $(this),
      id = 'eye-password-' + i,
      el = $('#' + id);

    $this.wrap(
      $('<div/>', {
        style: 'position:relative',
        id: id,
      })
    );

    $this.css({
      paddingRight: 60,
    });
    $this.after(
      $('<div/>', {
        html: 'Show',
        class: 'btn btn-primary btn-sm',
        id: 'passeye-toggle-' + i,
      }).css({
        position: 'absolute',
        right: 10,
        top: $this.outerHeight() / 2 - 12,
        padding: '2px 7px',
        fontSize: 12,
        cursor: 'pointer',
      })
    );

    $this.after(
      $('<input/>', {
        type: 'hidden',
        id: 'passeye-' + i,
      })
    );

    var invalid_feedback = $this.parent().parent().find('.invalid-feedback');

    if (invalid_feedback.length) {
      $this.after(invalid_feedback.clone());
    }

    $this.on('keyup paste', function () {
      $('#passeye-' + i).val($(this).val());
    });
    $('#passeye-toggle-' + i).on('click', function () {
      if ($this.hasClass('show')) {
        $('#passeye-toggle-' + i).text('Show');
        $this.attr('type', 'password');
        $this.removeClass('show');
      } else {
        $('#passeye-toggle-' + i).text('Hide');
        $this.attr('type', 'text');
        $this.val($('#passeye-' + i).val());
        $this.addClass('show');
      }
    });
  });

  $('#submit-button').on('click', function () {
    var name = $('input[id=username]');
    if (name.val().length === 0) {
      name.addClass('is-invalid');
      $('div[id=usernameFeedback]').text('ID를 입력해주세요.');
      name[0].scrollIntoView();
    } else {
      name.removeClass('is-invalid');
    }

    var password = $('input[id=password]');
    if (password.val().length === 0) {
      password.addClass('is-invalid');
      $('div[id=passwordFeedback]').text('PW를 입력해주세요.');
      password[0].scrollIntoView();
    } else {
      password.removeClass('is-invalid');
    }

    if (!name.hasClass('is-invalid') && !password.hasClass('is-invalid')) $('.my-login-validation').submit();
  });

  $('.my-login-validation').submit(function () {
    var form = $(this);
    if (form[0].checkValidity() === false) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.addClass('was-validated');
  });
});

function enterKey() {
  if (window.event.keyCode == 13) {
    $('.my-login-validation').submit();
  }
}
