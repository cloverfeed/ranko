makeEvent = ($parent, type, coords) ->
  canvasOffset = $parent.offset()
  $.Event type,
    pageX: canvasOffset.left + coords.x
    pageY: canvasOffset.top + coords.y
