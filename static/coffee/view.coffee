view_pdf = (docid, pv, pdf) ->
  GET_ANN_URL = '/view/' + docid + '/annotations'
  $.getJSON GET_ANN_URL, (annotations) ->
    pdf.getPage(1).then (page) ->
      render_page docid, pv, pdf, 1, page, annotations.data

setGeom = ($div, geom) ->
  $div.css
    left: geom.posx + "px"
    top: geom.posy + "px"
    width: geom.width + "px"
    height: geom.height + "px"

render_page = (docid, pv, pdf, i, page, annotations) ->
  canvas = document.createElement 'canvas'
  context = canvas.getContext '2d'
  scale = 1.5
  viewport = page.getViewport scale
  canvas.width = viewport.width
  canvas.height = viewport.height
  $pdfPage = jQuery('<div>')
    .addClass('pdfPage')
    .css
      width: viewport.width + "px"
      height: viewport.height + "px"
  pdfPage = $pdfPage.get 0
  pdfPage.appendChild canvas
  pv.appendChild pdfPage
  page.render
    canvasContext: context
    viewport: viewport
  $textLayerDiv = jQuery("<div />")
    .addClass("textLayer")
    .css
      height: viewport.height + "px"
      width: viewport.width + "px"
  selection = new Selection $textLayerDiv, (geom) ->
    ann = new Annotation $textLayerDiv, docid, i, "", null, geom
    $pdfPage.append ann.$div
  $selectionDiv = selection.$div
  $pdfPage.append($selectionDiv)
  pdfPage.appendChild($textLayerDiv.get 0)
  page.getTextContent().then (textContent) ->
    pageNumber = i
    pageIndex = pageNumber - 1
    textLayer = new TextLayerBuilder
      textLayerDiv: $textLayerDiv.get(0)
      pageIndex: pageIndex
      viewport: viewport
    textLayer.setTextContent textContent
  .then null, (error) ->
    pv.innerHTML = "Error while rendering PDF."
    console.log ("Error while rendering PDF: " + error)
  anns = annotations[i]
  if anns
    for ann in anns
      annotation = new Annotation $textLayerDiv, docid, i, ann.text, ann.id, ann
      $pdfPage.append annotation.$div

  if (i + 1 <= pdf.numPages)
    pdf.getPage(i + 1).then (page) ->
      render_page docid, pv, pdf, i + 1, page, annotations

view_fullscreen_enter = ->
  $('#subnav').hide()
  $('#exitfullscreen').show()

view_fullscreen_exit = ->
  $('#subnav').show()
  $('#exitfullscreen').hide()

view_init = (src, docid, url_post_comment) ->
  pv = document.getElementById "pdfview"
  PDFJS.getDocument(src).then (pdf) ->
    view_pdf(docid, pv, pdf)
  .then null, ->
    pv.innerHTML = "Error loading the document."
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
    view_fullscreen_enter()
  $('#fullscreen_button_exit').click (e) ->
    e.preventDefault()
    view_fullscreen_exit()
  $('#toggle_annotations_button').click (e) ->
    $('.annotation').toggle()
