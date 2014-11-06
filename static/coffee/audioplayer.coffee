class AudioPlayer
  constructor: (docid) ->
    @$div = $ '<div>'

    url = '/raw/' + docid
    @audio = new Audio url

    @channels = 2
    @sampleRate = 44100
    @audio.addEventListener 'loadedmetadata', (=> @startWaveform url), false

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

    @annotations = []

    @audio.addEventListener 'timeupdate', @update, false
    @update()

    @$canvas.mousedown @mousedown
    @$canvas.mouseup @mouseup


  mousedown: (e) =>
    ec = @eventCoords e
    if ec.x / @width < (1 - @annZoneRatio)
      # Seek
      totalTime = @audio.duration
      newTime = totalTime * (ec.y / @height)
      @audio.currentTime = newTime
    else
      # Start annotation
      ec = @eventCoords e
      time = @pixelsToSeconds ec.y
      @selection = new AudioSelection time, (startTime, length) =>
        annotation = new AudioAnnotation startTime, length
        @annotations.push annotation

  mouseup: (e) =>
    if !@selection?
      return
    ec = @eventCoords e
    time = @pixelsToSeconds ec.y
    @selection.mouseup time
    @selection = null

  eventCoords: (e) ->
    canOffset = @$canvas.offset()
    return (
      x: e.pageX - canOffset.left
      y: e.pageY - canOffset.top
    )

  pixelsToSeconds: (pixels) ->
    @audio.duration * pixels / @height

  update: =>
    console.log "update"
    @ctx.clearRect 0, 0, @width, @height
    currentTime = @audio.currentTime
    totalTime = @audio.duration
    size = @height * (currentTime / totalTime)
    @$debug.text size

    aw = @annZoneRatio * @width
    wf = (1 - @annZoneRatio) * @width

    @ctx.fillStyle = "lightpink"
    @ctx.fillRect wf, 0, aw, @height

    @ctx.fillStyle = "lightsalmon"
    @ctx.fillRect wf, 0, aw, size

    for annotation in @annotations
      @ctx.fillStyle = "orange"
      annStart = @secondsToPixels annotation.startTime
      annSize = @secondsToPixels annotation.length
      @ctx.fillRect wf, annStart, aw, annSize

    @ctx.fillStyle = "purple"
    for y in [0 .. @height - 1]
      if y > size
        @ctx.fillStyle = "violet"

      if @waveform?
        value = @waveform[y]
      else
        value = 1

      lineSize = value * wf
      offset = (wf / 2) * (1 - value)

      @ctx.fillRect offset, y, lineSize, 1

  secondsToPixels: (seconds) ->
    totalTime = @audio.duration
    @height * (seconds / totalTime)

  startWaveform: (url) ->
    bufferSize = @audio.duration * @sampleRate
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
      @computeWaveform e.renderedBuffer

  computeWaveform: (buffer) =>
    totalSamples = @audio.duration * @sampleRate
    nSamples = (totalSamples / @height) | 0

    sumAt = (y) =>
      start = y * nSamples
      sum = 0
      for channelNum in [0 .. @channels - 1]
        channel = buffer.getChannelData channelNum
        for sample in [start .. start + nSamples - 1]
          s = channel[sample]
          sum += Math.abs s
      return sum

    unnorm = (sumAt y for y in [0 .. @height - 1])

    maxi = -1
    for x in unnorm
      if maxi < x
        maxi = x

    @waveform = (s / maxi for s in unnorm)
    @update()


class AudioSelection
  constructor: (@down, @success) ->

  mouseup: (up) ->
    length = Math.abs(up - @down)
    start = Math.min(up, @down)
    @success(start, length)


class AudioAnnotation
  constructor: (@startTime, @length) ->
