class Annotation
  constructor: (@$tld, @docid, @page, @text, @id, @geom, @state, readOnly) ->
    @$div = jQuery('<div>').addClass 'annotation'
    @addStateClass()
    setGeom @$div, @geom

    @rest = new RestClient '/annotation/',
      error: (msg) ->
        flash_message "Error: #{msg}"

    $annText = jQuery('<div>').text(@text)
    @$div.append $annText

    if !readOnly
      $closeBtn = jQuery('<a>').text '[X]'
      @$div.prepend $closeBtn
      $closeBtn.click =>
        @rest.delete this, =>
          @$div.remove()

      $annText.editable @edit,
        onblur: 'submit'

      @$div.draggable
        stop: @updateOnEvent

    # necessary to keep out of the if because of bug #44
    @$div.resizable
      stop: @updateOnEvent

  edit: (value, settings) =>
    @text = value
    @submitChanges()
    return value

  updateOnEvent: (ev, ui) =>
    @updateGeom(ev, ui)
    @submitChanges()

  addStateClass: ->
    @$div.addClass ('annotation-' + @state)

  updateGeom: (e, ui) ->
    tldOffset = @$tld.offset()
    if e.type == 'dragstop'
      @geom.posx = ui.offset.left - tldOffset.left
      @geom.posy = ui.offset.top - tldOffset.top
    else if e.type == 'resizestop'
      @geom.width = ui.size.width
      @geom.height = ui.size.height

  update: ->
    @$div.removeClass 'annotation-open'
    @$div.removeClass 'annotation-closed'
    @addStateClass()

  submitChanges: ->
    @rest.post_or_put this,
      posx: @geom.posx | 0
      posy: @geom.posy | 0
      width: @geom.width | 0
      height: @geom.height | 0
      doc: @docid
      page: @page
      value: @text
      state: @state
