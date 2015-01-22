describe 'ViewPage (common elements)', ->
  beforeEach ->
    setFixtures """
    <div id="subnav"></div>
    <div id="exitfullscreen"></div>
    <button id="fullscreen_button"></button>
    <button id="fullscreen_button_exit"></button>

    <div id="openann" class="annotation annotation-open"></div>
    <div id="closedann" class="annotation annotation-closed"></div>

    <button id="seeNone" class="view-states-btn" data-view="nothing"></button>
    <button id="seeOnlyOpen" class="view-states-btn" data-view="only-open"></button>
    <button id="seeAll" class="view-states-btn" data-view="everything"></button>
    """
    docid = 5
    p = new ViewPage docid, 'pdf', false
    p.init()

  it 'has a fullscreen button', ->
    expect($('#subnav')).toBeVisible()
    expect($('#exitfullscreen')).toBeHidden()

    $('#fullscreen_button').click()

    expect($('#subnav')).toBeHidden()
    expect($('#exitfullscreen')).toBeVisible()

    $('#fullscreen_button_exit').click()

    expect($('#subnav')).toBeVisible()
    expect($('#exitfullscreen')).toBeHidden()

  it 'has a way to select annotations based on state', ->
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
