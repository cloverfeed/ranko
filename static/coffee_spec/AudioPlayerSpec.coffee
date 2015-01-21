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

  it 'starts with no annotations', ->
    expect(player.annotations.length).toBe(0)

  it 'can have annotations', ->
    ann =
      start: 2
      length: 5

    ann2 =
      start: 18
      length: 2

    player.addAudioAnnotation ann
    player.addAudioAnnotation ann2

    expect(player.annotations.length).toBe(2)
    expect($table.find('input[type=checkbox]')).toHaveLength(2)

    expect(player.annotationAt(3)).toEqual jasmine.objectContaining
      start: 2
      length: 5
    expect(player.annotationAt(10)).toBeNull()
    expect(player.annotationAt(19)).toEqual jasmine.objectContaining
      start: 18
      length: 2
