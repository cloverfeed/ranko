root = 'http://localhost:5000/'
casper.test.begin "Load-page", 1, (test) ->

  casper.start root, ->
    test.assertTitle "Ranko - Home"

  casper.run -> test.done()

casper.test.begin "Upload a document", (test) ->
  casper.start root, ->
    @clickLabel 'Upload a PDF', 'a'

  casper.then ->
    test.assertTitle 'Ranko - Upload'
    @fill 'form',
      file: 'bitcoin.pdf'
    , true

  casper.then ->
    test.assertTitle 'Ranko - Document'

  casper.run -> test.done()
