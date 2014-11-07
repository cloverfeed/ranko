list_view_init = (base) ->
  $('.ann-state-checkbox').click ->
    annid = $(this).data 'annid'
    state = if @checked then 'closed' else 'open'
    $.ajax
      url: base + annid
      type: 'PUT'
      data:
        state: state
