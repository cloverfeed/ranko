flash_message = (text) ->
  $msg = $ '<div>'
  $msg.text text
  $msg.addClass 'flashMessage'
  $('body').append $msg
  window.setTimeout ->
    $msg.hide()
  , 2000
