class Page
  constructor: (@docid, @i, params) ->
    annotations = params.annotations or []
    if params.page?
      $canvas = $('<canvas>')
      scale = 1.5
      canvas = $canvas.get 0
      viewport = params.page.getViewport scale
      width = viewport.width
      height = viewport.height
      canvas.width = width
      canvas.height = height
    else if params.image?
      width = params.image.width
      height = params.image.height
    else
      console.log "Page: couldn't set geometry"
    @$div = jQuery('<div>')
      .addClass('docPage')
      .css
        width: width + "px"
        height: height + "px"
    if params.page?
      @$div.append $canvas
      params.page.render
        canvasContext: canvas.getContext '2d'
        viewport: viewport
    @readOnly = false
    if params.readOnly?
      @readOnly = params.readOnly
    @$textLayerDiv = jQuery("<div />")
      .addClass("textLayer")
      .css
        height: height + "px"
        width: width + "px"
    @$div.append @$textLayerDiv

    selection = new Selection @$textLayerDiv, (geom) =>
      @addAnnotation "", null, geom, 'open'
    @$div.append selection.$div

    anns = annotations[@i]
    if anns
      for ann in anns
        @addAnnotation ann.text, ann.id, ann, ann.state

  addAnnotation: (text, id, geom, state) ->
    ann = new Annotation @$textLayerDiv, @docid, @i, text, id, geom, state, @readOnly
    @$div.append ann.$div
