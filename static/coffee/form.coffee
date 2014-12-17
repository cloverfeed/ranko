form_init = (dialog_selector, link_selector) ->
  $(dialog_selector).dialog
    autoOpen: false
    modal: true
  $(link_selector).click ->
    $(dialog_selector).dialog "open"
