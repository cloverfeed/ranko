root = 'http://localhost:5000/'

casper.on 'remote.message', (message) ->
  @echo("Remote message: " + message)

casper.test.begin "Load-page", 1, (test) ->

  casper.start root, ->
    test.assertTitle "Ranko - Home"

  casper.run -> test.done()

casper.test.begin "Upload a document", (test) ->
  casper.start root, ->
    test.assertTitle 'Ranko - Home'
    @fill 'form',
      file: 'fixtures/bitcoin.pdf'
    , true

  casper.run -> test.done()
