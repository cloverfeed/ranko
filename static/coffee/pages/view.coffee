view_init = (docid, filetype, readOnly) ->
  switch filetype
    when 'pdf'
      p = new PdfViewPage docid, readOnly
      $pv = $('#docview')
      PDFJS.getDocument("/raw/#{docid}").then (pdf) ->
        $.getJSON "/view/#{docid}/annotations", (annotations) ->
          p.init $pv, pdf, annotations.data
    when 'audio'
      p = new AudioViewPage docid, readOnly
      p.init()
      $.getJSON "/view/#{docid}/audioannotations", (annotations) ->
        p.addAnnotations annotations.data
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
