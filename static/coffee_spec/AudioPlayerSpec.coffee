describe 'AudioPlayer', ->
  docid = 5
  player = null
  $table = null

  beforeEach ->
    setFixtures """
    <div id="playertable">
    </div>
    """
    $table = $('#playertable')
    player = new AudioPlayer docid,
      $table: $table

    audio =
      duration: 100
      addEventListener: ->
      play: jasmine.createSpy 'audio play'
      pause: jasmine.createSpy 'audio pause'

    player.initAudio audio

  it 'starts with no annotations', ->
    expect(player.annotations.length).toBe(0)

  it 'can have annotations', ->
    ann =
      start: 2
      length: 5
      state: 'open'

    ann2 =
      start: 18
      length: 2
      state: 'open'

    player.addAudioAnnotation ann
    player.addAudioAnnotation ann2
    $checkboxes = $table.find('input[type=checkbox]')

    expect(player.annotations.length).toBe(2)
    expect($checkboxes).toHaveLength(2)

    expect(player.annotationAt(3)).toEqual jasmine.objectContaining
      start: 2
      length: 5
      state: 'open'
    expect(player.annotationAt(10)).toBeNull()
    expect(player.annotationAt(19)).toEqual jasmine.objectContaining
      start: 18
      length: 2

    $checkbox = $checkboxes.first()

    $checkbox.click()

    ann = player.annotationAt(3)
    expect(ann.state).toBe 'closed'

  it 'can seek', ->
    e = makeEvent player.$canvas, 'mousedown',
      x: 10
      y: 10

    player.$canvas.trigger e

    expect(player.audio.currentTime).toBe(1)

  it 'can create and move annotations', ->
    eventCreateDown = makeEvent player.$canvas, 'mousedown', x: 190, y: 10
    eventCreateUp = makeEvent player.$canvas, 'mouseup', x: 190, y: 30

    player.$canvas.trigger eventCreateDown
    player.$canvas.trigger eventCreateUp

    expect(player.annotations.length).toBe(1)
    annotation = player.annotations[0]
    expect(annotation).toEqual jasmine.objectContaining
      start: 1
      length: 2

    eventMoveDown = makeEvent player.$canvas, 'mousedown', x: 190, y: 20
    eventMoveUp = makeEvent player.$canvas, 'mouseup', x: 190, y: 50

    player.$canvas.trigger eventMoveDown
    player.$canvas.trigger eventMoveUp

    expect(player.annotations.length).toBe(1)
    annotation = player.annotations[0]
    expect(annotation).toEqual jasmine.objectContaining
      start: 4
      length: 2

  it 'has an play button', ->
    $playBtn = player.$div.find('button:contains("Play")')
    expect($playBtn).toHaveLength(1)
    $playBtn.click()
    expect(player.audio.play).toHaveBeenCalled()

  it 'has an pause button', ->
    $pauseBtn = player.$div.find('button:contains("Pause")')
    expect($pauseBtn).toHaveLength(1)
    $pauseBtn.click()
    expect(player.audio.pause).toHaveBeenCalled()

  describe 'waveform', ->
    buffer = null
    samples = null

    beforeEach ->
      size = player.audio.duration * player.sampleRate
      constantval = 0.14
      samples = (constantval for _ in [1..size])
      buffer =
        getChannelData: (channelNum) ->
          samples

    it 'can be computed', ->
      player.computeWaveform buffer

      expect(player.waveform).toEqual((1 for _ in [1..player.height]))


describe 'AudioSelection', ->
  sel = null
  spy = null
  down = 3

  beforeEach ->
    spy = jasmine.createSpy 'audioselection success'
    sel = new AudioSelection down, spy

  it 'can be dragged in increasing order', ->
    sel.mouseup(5)
    expect(spy).toHaveBeenCalledWith(3, 2)

  it 'can be dragged in decreasing order', ->
    sel.mouseup(2)
    expect(spy).toHaveBeenCalledWith(2, 1)


describe 'AudioDrag', ->
  drag = null
  spy = null

  beforeEach ->
    spy = jasmine.createSpy 'audiodrag success'
    drag = new AudioDrag 7, spy

  it 'can be dragged', ->
    drag.mouseup(5)
    expect(spy).toHaveBeenCalledWith(-2)
