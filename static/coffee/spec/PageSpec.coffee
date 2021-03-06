describe 'Page', ->
  docid = 5
  p = null
  $table = null

  beforeEach ->
    setFixtures '''
    <table id="table"></table>
    '''
    $table = $('#table')
    ann =
      text: 'Text'
      id: 54
      state: 'open'
    spyOn($, 'ajax')
    p = new Page docid, 0,
      width: 300
      height: 400
      $table: $table
      annotations: [[ann]]

  it 'has annotations', ->
    expect(p.$div.find('.annotation')).toHaveLength(1)
    expect($table.find('tr')).toHaveLength(1)

  it 'creates a checkbox', ->
    $checkbox = $table.find('input[type=checkbox]')
    expect($checkbox).toHaveLength(1)

    $checkbox.click()

    expect(p.$div.find('.annotation')).toHaveClass('annotation-closed')
    expect($.ajax).toHaveBeenCalled()

  it 'creates an annotation', ->
    startPos = x: 10, y: 10
    endPos = x: 50, y: 50
    ed = makeEvent p.$textLayerDiv, 'mousedown', startPos
    em = makeEvent p.$textLayerDiv, 'mousemove', endPos
    eu = makeEvent p.$textLayerDiv, 'mouseup', endPos

    for event in [ed, em, eu]
      p.$textLayerDiv.trigger event

    expect(p.$div.find('.annotation')).toHaveLength(2)

describe 'Page, initialized from a pdf', ->
  page = null

  beforeEach ->
    docid = 5
    pdfPage =
      getViewport: ->
        width: 100
        height: 200
      render: ->
        'then': (f) ->
          f()
    page = new Page docid, 0,
      page: pdfPage

  it 'has a canvas', ->
    expect(page.$div.find('canvas')).toHaveLength(1)
