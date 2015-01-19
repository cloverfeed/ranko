describe 'Flash', ->

  beforeEach ->
    jasmine.clock().install()

  afterEach ->
    jasmine.clock().uninstall()

  it 'should flash a message', ->
    flash_message "My message"

    jasmine.clock().tick(2001)
