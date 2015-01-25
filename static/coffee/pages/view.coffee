view_init = (docid, filetype, readOnly) ->
  switch filetype
    when 'pdf'
      p = new PdfViewPage docid, readOnly
      p.init()
    when 'audio'
      p = new AudioViewPage docid, readOnly
      p.init()
      audio = new Audio "/raw/#{docid}"
      p.audioPlayer.initAudio audio
    when 'image'
      create_image_view_page docid, readOnly


create_image_view_page = (docid, readOnly) ->
  p = new ImageViewPage docid, readOnly
  $img = $('<img>')
  $img.mousedown (e) ->
    e.preventDefault()
  $img.load ->
    image = this
    $.getJSON "/view/#{docid}/annotations", (annotations) ->
      p.init image, annotations.data
  $img.attr('src', '/raw/' + docid)
