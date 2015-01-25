setGeom = ($div, geom) ->
  $div.css
    left: "#{geom.posx}px"
    top: "#{geom.posy}px"
    width: "#{geom.width}px"
    height: "#{geom.height}px"

class ViewPage
  constructor: (@docid, @readOnly) ->
    undefined

  init: ->
    form_init '#upload_dialog', '#upload_link'
    form_init '#share_dialog', '#share_link'
    docid = @docid
    $('#share_form').submit (e) ->
      e.preventDefault()
      $.ajax
        type: 'POST'
        url: "/view/#{docid}/share"
        data: $(this).serialize()
        success: (data) ->
          share_url = "#{window.location.origin}/view/shared/#{data['data']}"
          input = $('<input>').attr('type', 'text').val(share_url)
          $('#share_form > button[type=submit]').replaceWith input

    $('#post_comment_form').submit (e) ->
      e.preventDefault()
      $.ajax
        type: 'POST'
        url: '/comment/new'
        data: $(this).serialize()
        success: (data) ->
          comm = $('#comment').val()
          $li = $('<li>').text(comm)
          $('#comments').append $li

    @init_list_view()

    $('#fullscreen_button').click (e) ->
      e.preventDefault()
      $('#subnav').hide()
      $('#exitfullscreen').show()

    $('#exitfullscreen').hide()
    $('#fullscreen_button_exit').click (e) ->
      e.preventDefault()
      $('#subnav').show()
      $('#exitfullscreen').hide()

    $('.view-states-btn').click ->
      switch $(this).data 'view'
        when 'everything'
          $('.annotation-open').show()
          $('.annotation-closed').show()
        when 'only-open'
          $('.annotation-open').show()
          $('.annotation-closed').hide()
        when 'nothing'
          $('.annotation-open').hide()
          $('.annotation-closed').hide()

  init_list_view: ->
    $('#listview').hide()
    $('#listaudioview').hide()
    $('#docmode_button').hide()
    $('#listmode_button').click (e) =>
      @list_mode()
    $('#docmode_button').click (e) =>
      @doc_mode()

  list_mode: ->
    $('#docview').hide()
    $(@list_view_selector).show()
    $('#listmode_button').hide()
    $('#docmode_button').show()

  doc_mode: ->
    $('#docview').show()
    $('#listview').hide()
    $('#listaudioview').hide()
    $('#docmode_button').hide()
    $('#listmode_button').show()


class PdfViewPage extends ViewPage
  init: ($pv, pdf, annotations) ->
    super()
    @$pv = $pv
    pdf.getPage(1).then (page) =>
      @render_page pdf, 1, page, annotations

  render_page: (pdf, i, page, annotations) ->
    pp = new Page @docid, i,
      page: page
      annotations: annotations
      readOnly: @readOnly
      $table: $('#listview tbody')
    @$pv.append pp.$div

    if (i + 1 <= pdf.numPages)
      pdf.getPage(i + 1).then (page) =>
        @render_page pdf, i + 1, page, annotations

  list_view_selector: '#listview'


class ImageViewPage extends ViewPage
  init: (image, annotations) ->
    super()
    $pv = $('#docview')
    page = new Page @docid, 0,
      width: image.width
      height: image.height
      annotations: annotations
      readOnly: @readOnly
      $table: $('#listview tbody')
    page.$div.append image
    $pv.append page.$div

  list_view_selector: '#listview'


class AudioViewPage extends ViewPage
  init: ->
    super()
    $pv = $('#docview')
    @audioPlayer = new AudioPlayer @docid,
      readOnly: @readOnly
      $table: $('#listaudioview tbody')
    $pv.append @audioPlayer.$div

  addAnnotations: (annotations) ->
    for ann in annotations
      @audioPlayer.addAudioAnnotation ann

  list_view_selector: '#listaudioview'
