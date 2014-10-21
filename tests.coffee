root = 'http://localhost:5000/'

casper.on 'remote.message', (message) ->
  @echo("Remote message: " + message)

casper.on 'resource.received', (resource) ->
  status = resource.status
  if(status >= 400)
    casper.log('Resource ' + resource.url + ' failed to load (' + status + ')', 'error')

    resourceErrors.push
      url: resource.url
      status: resource.status

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

  casper.then ->
    test.assertElementCount '.annotation', 0

  casper.run -> test.done()
