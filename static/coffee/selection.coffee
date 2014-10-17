class Selection
  constructor: (@$tld, @create) ->
    @x1 = 0
    @y1 = 0
    @x2 = 0
    @y2 = 0
    @$div = jQuery('<div>').addClass 'selectionDiv'
    @$tld.mousedown (e) => @mousedown e
    @$tld.mousemove (e) => @mousemove e
    @$tld.mouseup (e) => @mouseup e

  computeGeom: ->
    posx: Math.min @x1, @x2
    posy: Math.min @y1, @y2
    width: Math.abs(@x2 - @x1)
    height: Math.abs(@y2 - @y1)

  eventCoords: (e) ->
    tldOffset = @$tld.offset()
    return (
      x: e.pageX - tldOffset.left
      y: e.pageY - tldOffset.top
    )

  mousedown: (e) ->
    ec = @eventCoords e
    @x1 = ec.x
    @y1 = ec.y
    @$div.show()

  bigEnough: ->
    geom = @computeGeom()
    geom.width > 30 && geom.height > 30

  mouseup: ->
    @$div.hide()
    if @bigEnough()
      geom = @computeGeom()
      @create geom

  mousemove: (e) ->
    ec = @eventCoords e
    @x2 = ec.x
    @y2 = ec.y
    geom = @computeGeom()
    setGeom @$div, geom
