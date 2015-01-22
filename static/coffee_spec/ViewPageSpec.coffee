describe 'ViewPage (common elements)', ->
  p = null

  beforeEach ->
    docid = 5
    p = new ViewPage docid, 'pdf', false
    p.list_view_selector = '#listview'

  describe 'fullscreen mode', ->
    beforeEach ->
      setFixtures """
      <div id="subnav" />
      <div id="exitfullscreen" />
      <button id="fullscreen_button" />
      <button id="fullscreen_button_exit" />
      """
      p.init()

    it 'works', ->
      expect($('#subnav')).toBeVisible()
      expect($('#exitfullscreen')).toBeHidden()

      $('#fullscreen_button').click()

      expect($('#subnav')).toBeHidden()
      expect($('#exitfullscreen')).toBeVisible()

      $('#fullscreen_button_exit').click()

      expect($('#subnav')).toBeVisible()
      expect($('#exitfullscreen')).toBeHidden()

  describe 'state toggle button', ->

    beforeEach ->
      setFixtures """
      <div id="openann" class="annotation annotation-open" />
      <div id="closedann" class="annotation annotation-closed" />

      <button id="seeNone" class="view-states-btn" data-view="nothing" />
      <button id="seeOnlyOpen" class="view-states-btn" data-view="only-open" />
      <button id="seeAll" class="view-states-btn" data-view="everything" />
      """
      p.init()

    it 'selects annotations based on their state', ->
      expect($('#openann')).toBeVisible()
      expect($('#closedann')).toBeVisible()

      $('#seeOnlyOpen').click()

      expect($('#openann')).toBeVisible()
      expect($('#closedann')).toBeHidden()

      $('#seeNone').click()

      expect($('#openann')).toBeHidden()
      expect($('#closedann')).toBeHidden()

      $('#seeAll').click()

      expect($('#openann')).toBeVisible()
      expect($('#closedann')).toBeVisible()

  describe 'list mode', ->

    beforeEach ->
      setFixtures """
      <div id="docview" />
      <div id="listview" />
      <button id="docmode_button" />
      <button id="listmode_button" />
      """
      p.init()

    it 'can be activated and deactivated', ->
      expect($('#docmode_button')).toBeHidden()
      expect($('#docview')).toBeVisible()
      expect($('#listmode_button')).toBeVisible()
      expect($('#listview')).toBeHidden()

      $('#listmode_button').click()

      expect($('#docmode_button')).toBeVisible()
      expect($('#docview')).toBeHidden()
      expect($('#listmode_button')).toBeHidden()
      expect($('#listview')).toBeVisible()

      $('#docmode_button').click()

      expect($('#docmode_button')).toBeHidden()
      expect($('#docview')).toBeVisible()
      expect($('#listmode_button')).toBeVisible()
      expect($('#listview')).toBeHidden()


describe 'PDFViewPage', ->
  docid = 5
  beforeEach ->
    setFixtures """
    <form id="share_form">
      <button type="submit">Submit</button>
    </form>
    """
    view_init docid, 'pdf', false

  it 'should have a share button', ->
    $shareForm = $('#share_form')
    expect($shareForm).toHaveLength(1)

    spyOn($, "ajax").and.callFake (options) ->
      expect(options.url).toContain(docid)

    $shareForm.submit()

describe 'ImageViewPage', ->
  docid = 5
  p = null

  beforeEach ->
    setFixtures """
    <div id="docview">
    </div>
    """
    p = new ImageViewPage docid, 'image', false
    image = $('<img>')
    annotations = []
    p.init image, annotations

  it 'should create an image', ->
    expect($('img')).toHaveLength(1)

describe 'AudioViewPage', ->
  docid = 5

  beforeEach ->
    setFixtures """
    <div id="docview">
    </div>
    """
    p = new AudioViewPage docid, 'audio', false
    p.init()

  it 'should create a canvas', ->
    expect($('canvas')).toHaveLength(1)
