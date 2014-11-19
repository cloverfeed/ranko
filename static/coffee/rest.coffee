class RestClient
  constructor: (@url_base) ->

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
        if type == 'POST'
          obj.id = d.id

  delete: (obj, success) ->
    if obj.id
      $.ajax
        url: @url_base + obj.id
        type: 'DELETE'
        success: success
    else
      success()