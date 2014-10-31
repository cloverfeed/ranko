class Annotation
  constructor: (@$tld, @docid, @page, @text, @annid, @geom, @state) ->
    @$div = jQuery('<div>').addClass 'annotation'
    @$div = jQuery('<div>').addClass ('annotation-' + @state)
    setGeom @$div, @geom
    $closeBtn = jQuery('<a>').text '[X]'
    @$div.append $closeBtn

    $closeBtn.click =>
      delDone = =>
        @$div.remove()
      if @annid
        ANN_URL = '/annotation/' + @annid
        $.ajax
          url: ANN_URL
          type: 'DELETE'
          success: -> delDone()
      else
        delDone()

    $annText = jQuery('<div>').text(@text)
    @$div.append $annText

    $annText.editable (value, settings) =>
      @text = value
      @submitChanges()
      return value
    ,
      onblur: 'submit'
    @$div.draggable
      stop: (ev, ui) =>
        @updateGeom(ev, ui)
        @submitChanges()
    @$div.resizable
      stop: (ev, ui) =>
        @updateGeom(ev, ui)
        @submitChanges()

  updateGeom: (e, ui) ->
    tldOffset = @$tld.offset()
    if e.type == 'dragstop'
      @geom.posx = ui.offset.left - tldOffset.left
      @geom.posy = ui.offset.top - tldOffset.top
    else if e.type == 'resizestop'
      @geom.width = ui.size.width
      @geom.height = ui.size.height

  submitChanges: ->
    if @annid
      type = 'PUT'
      url = '/annotation/' + @annid
    else
      type = 'POST'
      url = '/annotation/new'
    $.ajax
      type: type
      url: url
      data:
        posx: @geom.posx | 0
        posy: @geom.posy | 0
        width: @geom.width | 0
        height: @geom.height | 0
        doc: @docid
        page: @page
        value: @text
      success: (d) =>
        if type == 'POST'
          @annid = d.id
