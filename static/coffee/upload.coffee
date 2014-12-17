upload_form_init = ->
  $('#upload_dialog').dialog
    autoOpen: false
    modal: true
  $('#upload_link').click ->
    $('#upload_dialog').dialog "open"

share_form_init = ->
  $('#share_dialog').dialog
    autoOpen: false
    modal: true
  $('#share_link').click ->
    $('#share_dialog').dialog "open"
