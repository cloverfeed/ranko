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

    ann = new Annotation $topDiv, docid, page, text, id, geom, state, readOnly
    $topDiv.append ann.$div

  it 'should have the correct class', ->
    expect(ann.$div).toBeInDOM()
    expect(ann.$div).toHaveClass('annotation')

  describe 'when network works', ->
    beforeEach ->
      spyOn($, 'ajax').and.callFake (options) ->
        options.success()

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
      ann.updateOnEvent ev, ui
      expect(ann.geom).toEqual jasmine.objectContaining
        posx: newx
        posy: newy
      expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
        type: 'PUT'
        url: '/annotation/8'
        data: jasmine.objectContaining
          posx: newx
          posy: newy

    it 'is resizable', ->
      new_width = 100
      new_height = 200

      ev = $.Event 'resizestop'
      ui =
        size:
          width: new_width
          height: new_height

      ann.updateOnEvent ev, ui

      expect(ann.geom).toEqual jasmine.objectContaining
        width: new_width
        height: new_height
      expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
        type: 'PUT'
        url: '/annotation/8'
        data: jasmine.objectContaining
          width: new_width
          height: new_height

    it 'updates its class when state changes', ->
      expect(ann.$div).toHaveClass('annotation-open')
      expect(ann.$div).not.toHaveClass('annotation-closed')

      ann.state = 'closed'
      ann.update()

      expect(ann.$div).toHaveClass('annotation-closed')
      expect(ann.$div).not.toHaveClass('annotation-open')

  describe 'when network fails', ->
    beforeEach ->
      spyOn($, 'ajax').and.callFake (options) ->
        options.error null, null, "Fail"
      spyOn(window, 'flash_message')

    it 'flashes an error message', ->
      ann.edit "Value", {}
      expect(window.flash_message).toHaveBeenCalled()
