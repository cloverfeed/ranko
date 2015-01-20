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
