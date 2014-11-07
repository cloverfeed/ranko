rest_post_or_put = (obj, params) ->
  if obj.id
    type = 'PUT'
    url = params.url_base + obj.id
  else
    type = 'POST'
    url = params.url_base + 'new'
  $.ajax
    type: type
    url: url
    data: params.data
    success: (d) =>
      if type == 'POST'
        obj.id = d.id
