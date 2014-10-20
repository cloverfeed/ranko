setGeom = ($div, geom) ->
  $div.css
    left: geom.posx + "px"
    top: geom.posy + "px"
    width: geom.width + "px"
    height: geom.height + "px"

render_page = (docid, $pv, pdf, i, page, annotations) ->
  pp = new PdfPage docid, i, page, annotations
  $pv.append pp.$div

  if (i + 1 <= pdf.numPages)
    pdf.getPage(i + 1).then (page) ->
      render_page docid, $pv, pdf, i + 1, page, annotations

view_init = (src, docid, url_post_comment) ->
  $pv = $('#pdfview')
  PDFJS.getDocument(src).then (pdf) ->
    GET_ANN_URL = '/view/' + docid + '/annotations'
    $.getJSON GET_ANN_URL, (annotations) ->
      pdf.getPage(1).then (page) ->
        render_page docid, $pv, pdf, 1, page, annotations.data
  .then null, ->
    $pv.text "Error loading the document."
  $('#post_comment_form').submit (e) ->
    e.preventDefault()
    $.ajax
      type: 'POST'
      url: url_post_comment
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

  $('#toggle_annotations_button').click (e) ->
    $('.annotation').toggle()
