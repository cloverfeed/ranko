upload_form_init = ->
  $('#upload_dialog').dialog
    autoOpen: false
    modal: true
  $('#upload_link').click ->
    $('#upload_dialog').dialog "open"
