describe 'Selection', ->
  selection = null

  beforeEach ->
    setFixtures """
    <div id="selectionDiv">
    </div>
    """

    $div = $('#selectionDiv')
    selection = new Selection $div, ->

  it 'is created empty', ->
    geom = selection.computeGeom()
    expect(geom).toEqual
      posx: 0
      posy: 0
      width: 0
      height: 0
