describe 'Selection', ->
  selection = null
  spy = null
  $div = null

  beforeEach ->
    setFixtures """
    <div id="sel">
    </div>
    """

    $div = $('#sel')
    spy = jasmine.createSpy 'selection spy'
    selection = new Selection $div, spy

  it 'is created empty', ->
    geom = selection.computeGeom()
    expect(geom).toEqual
      posx: 0
      posy: 0
      width: 0
      height: 0

  it 'is created hidden', ->
    expect($('.selectionDiv')).toBeHidden()

  it 'reacts to mouse down', ->
    $div.mousedown()
    expect($('.selectionDiv')).toBeVisible()

  it 'reacts to mouse up', ->
    $div.mousedown()
    $div.mouseup()
    expect($('.selectionDiv')).toBeHidden()

  it 'does not run the callback for a small move', ->
    $div.mousedown()
    $div.mouseup()
    expect(spy).not.toHaveBeenCalled()

  it 'runs the callback for a big move', ->
    initial =
      x: 5
      y: 7

    final =
      x: 45
      y: 57

    makeEvent = (t, c) ->
      $.Event t,
        pageX: c.x
        pageY: c.y

    evDown = makeEvent 'mousedown', initial
    $div.trigger evDown

    evMove = makeEvent 'mousemove', final
    $div.trigger evMove

    evUp = makeEvent 'mouseup', final
    $div.trigger evUp

    expect(spy).toHaveBeenCalled()
