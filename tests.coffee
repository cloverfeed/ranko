casper.test.begin "Load-page", 1, (test) ->

    casper.start 'http://localhost:5000/', ->
        test.assertTitle "Ranko - Home"

    casper.run ->
        test.done()
