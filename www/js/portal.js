$(document).ready(function () {
    $.datetimepicker.setLocale('pt');
    $('.datetimepicker').datetimepicker({
        lang: 'pt',
        minDate:'-0',
        format: 'd/m/Y H:i'
    });

    var email_re = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
    var $guest_input = $('textarea[name="guests"]');
    var $cont_email_guest = $('.cont_email_guest');
    var $add_guest = $('#add_guest');
    var $guest = $('#guest');
    var emails = [];
    var _template = '<button value="{{value}}" type="button" class="guest_item btn btn-sm btn-outline-secondary">{{value}} <span class="badge badge-light">x</span></button>';

    (function () {
        if (!$guest_input.val()) return;
        emails = $guest_input.val().split(';');
        for (var i = 0, l = emails.length; i < l; i++) {
            $cont_email_guest.append(_template.replace(/\{\{value\}\}/g, emails[i]));
        }
    })();

    function render_email_list () {
        var _email = $guest.val();
        if (!_email) {
            $guest.focus();
            return window.confirm('Favor inserir um e-mail válido.');
        }
        if (!email_re.test(_email.toLowerCase())){
            $guest.focus();
            return window.confirm('Email inválido.');
        }

        if (emails.indexOf(_email) > -1) {
            $guest.focus();
            return window.confirm('Este e-mail já está na lista.');
        }

        emails.push(_email);
        $guest_input.text(emails.join(';'));
        $cont_email_guest.append(_template.replace(/\{\{value\}\}/g, _email));
        $guest.val(null);
    }

    $guest.keypress(function (e) {
        if(e.which !== 13) return this;
        render_email_list();
        $guest.focus();
    });
    $add_guest.click(render_email_list);

    $(document).on('click', 'button.guest_item', function () {
       if (emails.indexOf(this.value) < 0) {
            return window.confirm('Email não encontrado.');
       }
       emails.splice(emails.indexOf(this.value), 1);
       $guest_input.text(emails.join(';'));
       this.remove();
    });
});
