describe 'ViewPage (common elements)', ->
  p = null

  beforeEach ->
    docid = 5
    p = new ViewPage docid, false
    p.list_view_selector = '#listview'

  describe 'fullscreen mode', ->
    beforeEach ->
      setFixtures '''
      <div id="subnav" />
      <div id="exitfullscreen" />
      <button id="fullscreen_button" />
      <button id="fullscreen_button_exit" />
      '''
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
      setFixtures '''
      <div id="openann" class="annotation annotation-open" />
      <div id="closedann" class="annotation annotation-closed" />

      <button id="seeNone" class="view-states-btn" data-view="nothing" />
      <button id="seeOnlyOpen" class="view-states-btn" data-view="only-open" />
      <button id="seeAll" class="view-states-btn" data-view="everything" />
      '''
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
      setFixtures '''
      <div id="docview" />
      <div id="listview" />
      <button id="docmode_button" />
      <button id="listmode_button" />
      '''
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

  describe 'share dialog', ->

    beforeEach ->
      setFixtures '''
      <form id="share_form">
        <input type="text" name="name" value="Michel" />
        <button type="submit">Submit</submit>
      </form>
      '''
      spyOn($, 'ajax').and.callFake (options) ->
        options.success
          data: 'FAKECODE'
      p.init()

    it 'displays a share url', ->
      $('#share_form').submit()
      expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
        type: 'POST'
        url: '/view/5/share'
        data: 'name=Michel'
      contents = $('input[type=text]').last().val()
      expect(contents).toContain('/view/shared/FAKECODE')

  describe 'comment form', ->
    beforeEach ->
      setFixtures '''
        <form id="post_comment_form">
          <input type="text" name="comment" value="my comment" />
          <button type="submit">Submit</submit>
        </form>
        <div id="comments" />
      '''
      p.init()
      spyOn($, 'ajax').and.callFake (options) ->
        options.success {}

    it 'creates a comment', ->
      expect($('#post_comment_form')).toHaveLength(1)
      $('#post_comment_form').submit()

      expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
        url: '/comment/new'
        type: 'POST'
        data: 'comment=my+comment'

      expect($('#comments li')).toHaveLength(1)


describe 'ImageViewPage', ->
  docid = 5
  p = null

  beforeEach ->
    setFixtures '''
    <div id="docview">
    </div>
    '''
    p = new ImageViewPage docid, false
    image = $('<img>')
    annotations = []
    p.init image, annotations

  it 'should create an image', ->
    expect($('img')).toHaveLength(1)

describe 'AudioViewPage', ->
  docid = 5
  p = null

  beforeEach ->
    setFixtures '''
    <div id="docview">
    </div>
    '''
    p = new AudioViewPage docid, false
    p.init()

  it 'should create a canvas', ->
    expect($('canvas')).toHaveLength(1)

  it 'has annotations', ->
    ann1 =
      start: 1
    ann2 =
      start: 10
    p.addAnnotations [ann1, ann2]

    expect($('.audioAnnotation')).toHaveLength(2)

describe 'PDFViewPage', ->
  $div = null
  docid = 5

  beforeEach ->
    setFixtures '<div id="pdf" />'
    $div = $('#pdf')

  it 'renders pages', ->
    p = new PdfViewPage docid, false

    pdf =
      numPages: 3
      getPage: (n) ->
        then: (f) ->
          f
            render: ->
              then: ->
                undefined
            getViewport: ->
              height: 400
              width: 300

    anns = []
    p.init $div, pdf, anns

    expect($div.find('canvas')).toHaveLength(3)
