setGeom = ($div, geom) ->
  $div.css
    left: geom.posx + "px"
    top: geom.posy + "px"
    width: geom.width + "px"
    height: geom.height + "px"

render_page = (docid, $pv, pdf, i, page, annotations, readOnly) ->
  pp = new Page docid, i,
    page: page
    annotations: annotations
    readOnly: readOnly
  $pv.append pp.$div

  if (i + 1 <= pdf.numPages)
    pdf.getPage(i + 1).then (page) ->
      render_page docid, $pv, pdf, i + 1, page, annotations, readOnly

view_init = (docid, filetype, readOnly) ->
  switch filetype
    when "pdf"
      view_init_pdf docid, readOnly
    when "image"
      view_init_image docid
    when "audio"
      view_init_audio docid
  view_init_common()

view_init_audio = (docid) ->
  $pv = $('#docview')
  audioPlayer = new AudioPlayer docid
  $pv.append audioPlayer.$div

view_init_image = (docid) ->
  GET_ANN_URL = '/view/' + docid + '/annotations'
  $img = $('<img>')
  $pv = $('#docview')
  $img.mousedown (e) ->
    e.preventDefault()
  $img.load ->
    image = this
    $.getJSON GET_ANN_URL, (annotations) ->
      page = new Page docid, 0,
        image: image
        annotations: annotations.data
      page.$div.append $img
      $pv.append page.$div
  $img.attr('src', '/raw/' + docid)

view_init_pdf = (docid, readOnly) ->
  $pv = $('#docview')
  PDFJS.getDocument('/raw/' + docid).then (pdf) ->
    GET_ANN_URL = '/view/' + docid + '/annotations'
    $.getJSON GET_ANN_URL, (annotations) ->
      pdf.getPage(1).then (page) ->
        render_page docid, $pv, pdf, 1, page, annotations.data, readOnly
  .then null, ->
    $pv.text "Error loading the document."

view_init_common = ->
  $('#post_comment_form').submit (e) ->
    e.preventDefault()
    $.ajax
      type: 'POST'
      url: '/comment/new'
      data: $(this).serialize()
      success: (data) ->
        comm = $('#comment').val()
        $li = $('<li>').text(comm)
        $('#comments').append $li

  $('#fullscreen_button').click (e) ->
    e.preventDefault()
    $('#subnav').hide()
    $('#exitfullscreen').show()

  $('#fullscreen_button_exit').click (e) ->
    e.preventDefault()
    $('#subnav').show()
    $('#exitfullscreen').hide()

  $('.view-states-btn').click ->
    switch $(this).data 'view'
      when 'everything'
        $('.annotation-open').show()
        $('.annotation-closed').show()
      when 'only-open'
        $('.annotation-open').show()
        $('.annotation-closed').hide()
      when 'nothing'
        $('.annotation-open').hide()
        $('.annotation-closed').hide()
