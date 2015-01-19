describe 'Flash', ->

  beforeEach ->
    jasmine.clock().install()

  afterEach ->
    jasmine.clock().uninstall()

  it 'should flash a message', ->
    flash_message "My message"

    expect($('.flashMessage')).toBeVisible()
    jasmine.clock().tick(2001)
    expect($('.flashMessage')).toBeHidden()
