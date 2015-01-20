class Page
  # params.$table is the tbody in list view
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
    else if params.width? and params.height?
      width = params.width
      height = params.height
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
    @$table = params.$table

    if !@readOnly
      selection = new Selection @$textLayerDiv, (geom) =>
        @addAnnotation "", null, geom, 'open'
      @$div.append selection.$div

    anns = annotations[@i]
    if anns
      for ann in anns
        @addAnnotation ann.text, ann.id, ann, ann.state

  addAnnotation: (text, id, geom, state) ->
    ann = new Annotation @$textLayerDiv, @docid, @i, text,
                         id, geom, state, @readOnly
    $row = $('<tr>')
    $row.append($('<td>').text(@i))
    $row.append($('<td>').text(text))

    annotation_state = (st) ->
      st == 'closed'

    $checkbox = $ '<input>',
      type: 'checkbox'
    $checkbox.prop 'checked', annotation_state(state)

    $checkbox.click ->
      state = if @checked then 'closed' else 'open'
      ann.state = state
      ann.update()
      ann.submitChanges()

    $row.append($('<td>').append($checkbox))
    @$table.append $row
    @$div.append ann.$div
