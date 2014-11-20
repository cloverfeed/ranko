class Annotation
  constructor: (@$tld, @docid, @page, @text, @id, @geom, @state, readOnly) ->
    @$div = jQuery('<div>').addClass 'annotation'
    @$div = jQuery('<div>').addClass ('annotation-' + @state)
    setGeom @$div, @geom

    @rest = new RestClient '/annotation/',
      error: (msg) ->
        $msg = $ '<div>'
        $msg.text "Error: #{msg}"
        $msg.addClass 'flashMessage'
        $('body').append $msg
        window.setTimeout ->
          $msg.hide()
        , 2000

    $annText = jQuery('<div>').text(@text)
    @$div.append $annText

    if !readOnly
      $closeBtn = jQuery('<a>').text '[X]'
      @$div.prepend $closeBtn
      $closeBtn.click =>
        @rest.delete this, =>
          @$div.remove()

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
    # necessary to keep out of the if because of bug #44
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
    @rest.post_or_put this,
      posx: @geom.posx | 0
      posy: @geom.posy | 0
      width: @geom.width | 0
      height: @geom.height | 0
      doc: @docid
      page: @page
      value: @text
