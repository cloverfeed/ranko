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

    @channels = 2
    @sampleRate = 44100
    @chunkDuration = 30
    bufferSize = @chunkDuration * @sampleRate
    offlineCtx = new OfflineAudioContext @channels, bufferSize, @sampleRate

    source = offlineCtx.createBufferSource()

    getData = ->
      request = new XMLHttpRequest()
      request.open 'GET', url, true
      request.responseType = 'arraybuffer'
      request.onload = ->
        audioData = request.response

        ok = (buffer) ->
          myBuffer = buffer
          source.buffer = myBuffer
          source.connect offlineCtx.destination
          source.start()
          offlineCtx.startRendering()

        offlineCtx.decodeAudioData audioData, ok, (e) ->
          console.log("Error with decoding audio data" + e.err)

      request.send()

    getData()

    offlineCtx.oncomplete = (e) =>
      @drawBuffer e.renderedBuffer

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
    @ctx.clearRect 0, 0, @width, @height
    currentTime = @audio.currentTime
    totalTime = @audio.duration
    size = @height * (currentTime / totalTime)
    @$debug.text size

    wf = (1 - @annZoneRatio) * @width

    @ctx.fillStyle = "lightpink"
    @ctx.fillRect wf, 0, @annZoneRatio * @width, @height

    @ctx.fillStyle = "lightsalmon"
    @ctx.fillRect wf, 0, @annZoneRatio * @width, size

    @ctx.fillStyle = "purple"
    for y in [0 .. @height - 1]
      if y > size
        @ctx.fillStyle = "violet"

      value = 1
      if @waveform? and y < @waveformLimit
        value = @waveform[y]

      lineSize = value * wf
      offset = (wf / 2) * (1 - value)

      @ctx.fillRect offset, y, lineSize, 1

  drawBuffer: (buffer) =>
    secondsToPixels = (seconds) =>
      totalTime = @audio.duration
      return @height * (seconds / totalTime)

    maxPix = secondsToPixels @chunkDuration
    totalSamples = @chunkDuration * @sampleRate
    nSamples = (totalSamples / maxPix) | 0

    sumAt = (y) =>
      start = y * nSamples
      sum = 0
      for channelNum in [0 .. @channels - 1]
        channel = buffer.getChannelData channelNum
        for sample in [start .. start + nSamples - 1]
          s = channel[sample]
          sum += Math.abs s
      return sum

    unnorm = (sumAt y for y in [0 .. maxPix - 1])

    maxi = -1
    for x in unnorm
      if maxi < x
        maxi = x

    @waveformLimit = maxPix
    @waveform = (s / maxi for s in unnorm)
