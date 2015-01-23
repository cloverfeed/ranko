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
      addEventListener: ->

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
