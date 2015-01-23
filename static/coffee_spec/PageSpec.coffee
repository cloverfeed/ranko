describe 'Page', ->
  docid = 5
  p = null
  $table = null

  beforeEach ->
    setFixtures """
    <table id="table"></table>
    """
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
