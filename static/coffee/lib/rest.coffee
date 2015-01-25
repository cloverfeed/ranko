class RestClient
  constructor: (@url_base, params) ->
    if params? and params.error?
      @error = params.error

  post_or_put: (obj, data) ->
    if obj.id
      type = 'PUT'
      url = @url_base + obj.id
    else
      type = 'POST'
      url = @url_base + 'new'
    $.ajax
      type: type
      url: url
      data: data
      success: (d) ->
        if type is 'POST'
          obj.id = d.id
      error: @handle_ajax_error

  delete: (obj, success) ->
    if obj.id
      $.ajax
        url: @url_base + obj.id
        type: 'DELETE'
        success: success
        error: @handle_ajax_error
    else
      success()

  handle_ajax_error: (jq, reason, text) =>
    if @error?
      @error text
