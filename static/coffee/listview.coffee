list_view_init = ->
  $('.ann-state-checkbox').click ->
    annid = $(this).data 'annid'
    state = if @checked then 'closed' else 'open'
    $.ajax
      url: '/annotation/' + annid
      type: 'PUT'
      data:
        state: state
