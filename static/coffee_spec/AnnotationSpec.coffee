describe 'Annotation', ->
  ann = null
  docid = 5
  page = 3
  text = 'my text'
  id = 8
  geom =
    posx: 15
    posy: 25
    width: 30
    height: 40
  state = 'open'
  readOnly = false

  beforeEach ->
    setFixtures """
    <div id="top">
    </div>
    """
    topDiv = $('#top')

    ann = new Annotation topDiv, docid, page, text, id, geom, state, readOnly

  it 'should have the correct class', ->
    expect(ann.$div).toHaveClass('annotation')
