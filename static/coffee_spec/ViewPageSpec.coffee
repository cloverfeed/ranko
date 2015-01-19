describe 'PDFViewPage', ->
  docid = 5
  beforeEach ->
    filetype = 'pdf'
    readOnly = false
    setFixtures """
    <form id="share_form">
      <button type="submit">Submit</button>
    </form>
    """
    p = new PdfViewPage docid, filetype, readOnly
    p.init()

  it 'should have a share button', ->
    $shareForm = $('#share_form')
    expect($shareForm).toHaveLength(1)

    spyOn($, "ajax").and.callFake (options) ->
      expect(options.url).toContain(docid)

    $shareForm.submit()
