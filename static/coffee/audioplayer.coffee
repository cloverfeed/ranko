class AudioPlayer
  constructor: (docid) ->
    @$div = $ '<div>'

    url = '/raw/' + docid
    @audio = new Audio url

    $playBtn = $('<button>').addClass('btn btn-default').text('Play')
    $playBtn.click =>
      @audio.play()
    $pauseBtn = $('<button>').addClass('btn btn-default').text('Pause')
    $pauseBtn.click =>
      @audio.pause()

    @$div.append $playBtn
    @$div.append $pauseBtn

    @$debug = $ '<span>'
    @$div.append @$debug

    @annZoneRatio = 0.25

    @width = 200
    @height = 1000
    @$canvas = $('<canvas>').prop
      width: @width
      height: @height
    $canvasDiv = $ '<div>'
    $canvasDiv.append @$canvas
    @$div.append $canvasDiv
    @ctx = @$canvas[0].getContext '2d'

    delay = 250 # ms
    interval = window.setInterval (=> @update()), delay

    @$canvas.mousedown (e) =>
      ec = @eventCoords e
      if ec.x / @width < (1 - @annZoneRatio)
        totalTime = @audio.duration
        newTime = totalTime * (ec.y / @height)
        @audio.currentTime = newTime

  eventCoords: (e) ->
    canOffset = @$canvas.offset()
    return (
      x: e.pageX - canOffset.left
      y: e.pageY - canOffset.top
    )

  update: ->
    currentTime = @audio.currentTime
    totalTime = @audio.duration
    size = @height * (currentTime / totalTime)
    @$debug.text size

    @ctx.fillStyle = "violet"
    @ctx.fillRect 0, 0, (1-@annZoneRatio)*@width, @height

    @ctx.fillStyle = "purple"
    @ctx.fillRect 0, 0, (1-@annZoneRatio)*@width, size

    @ctx.fillStyle = "lightpink"
    @ctx.fillRect (1-@annZoneRatio)*@width, 0, @annZoneRatio*@width, @height

    @ctx.fillStyle = "lightsalmon"
    @ctx.fillRect (1-@annZoneRatio)*@width, 0, @annZoneRatio*@width, size
