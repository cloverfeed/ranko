class PdfPage
  constructor: (@docid, @i, page, annotations) ->
    $canvas = $('<canvas>')
    scale = 1.5
    viewport = page.getViewport scale
    canvas = $canvas.get 0
    canvas.width = viewport.width
    canvas.height = viewport.height
    @$div = jQuery('<div>')
      .addClass('pdfPage')
      .css
        width: viewport.width + "px"
        height: viewport.height + "px"
    @$div.append $canvas
    page.render
      canvasContext: canvas.getContext '2d'
      viewport: viewport
    @$textLayerDiv = jQuery("<div />")
      .addClass("textLayer")
      .css
        height: viewport.height + "px"
        width: viewport.width + "px"
    @$div.append @$textLayerDiv

    selection = new Selection @$textLayerDiv, (geom) =>
      @addAnnotation "", null, geom
    @$div.append selection.$div

    anns = annotations[@i]
    if anns
      for ann in anns
        @addAnnotation ann.text, ann.id, ann

  addAnnotation: (text, id, geom) ->
    ann = new Annotation @$textLayerDiv, @docid, @i, text, id, geom
    @$div.append ann.$div
