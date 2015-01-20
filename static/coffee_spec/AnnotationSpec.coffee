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
  $topDiv = null

  beforeEach ->
    setFixtures """
    <div id="top">
    </div>
    """
    $topDiv = $('#top')

    spyOn($, 'ajax').and.callFake (options) ->
      options.success()

    ann = new Annotation $topDiv, docid, page, text, id, geom, state, readOnly
    $topDiv.append ann.$div

  it 'should have the correct class', ->
    expect(ann.$div).toBeInDOM()
    expect(ann.$div).toHaveClass('annotation')

  it 'should close itself', ->
    $closeBtn = ann.$div.find('a')
    expect($closeBtn).toHaveText('[X]')

    $closeBtn.click()

    expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
      type: 'DELETE'
      url: '/annotation/8'
    expect(ann.$div).not.toBeInDOM()

  it 'is editable', ->
    ann.edit 'new text', {}
    expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
      type: 'PUT'
      url: '/annotation/8'
      data: jasmine.objectContaining
        value: 'new text'

  it 'is draggable', ->
    newx = 35
    newy = 65
    ev = $.Event 'dragstop'
    offset = $topDiv.offset()
    ui =
      offset:
        left: newx + offset.left
        top: newy + offset.top
    ann.drag ev, ui
    expect(ann.geom).toEqual jasmine.objectContaining
      posx: newx
      posy: newy
    expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
      type: 'PUT'
      url: '/annotation/8'
      data: jasmine.objectContaining
        posx: newx
        posy: newy
