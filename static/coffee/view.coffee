setGeom = ($div, geom) ->
  $div.css
    left: geom.posx + "px"
    top: geom.posy + "px"
    width: geom.width + "px"
    height: geom.height + "px"

view_init = (docid, filetype, readOnly) ->
  switch filetype
    when "pdf"
      p = new PdfViewPage docid, filetype, readOnly
    when "image"
      p = new ImageViewPage docid, filetype, readOnly
    when "audio"
      p = new AudioViewPage docid, filetype, readOnly
  p.init()

class ViewPage
  constructor: (@docid, @filetype, @readOnly) ->

  init: ->
    form_init '#upload_dialog', '#upload_link'
    form_init '#share_dialog', '#share_link'
    $('#share_form').submit (e) ->
      e.preventDefault()
      $.ajax
        type: 'POST'
        url: "/view/#{@docid}/share"
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
    list_view_init @get_annotations_route

    $('#listview').hide()
    $('#listaudioview').hide()
    $('#docmode_button').hide()
    $('#listmode_button').click (e) =>
      @list_mode
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
  init: ->
    super()
    @$pv = $('#docview')
    PDFJS.getDocument('/raw/' + @docid).then (pdf) =>
      GET_ANN_URL = '/view/' + @docid + '/annotations'
      $.getJSON GET_ANN_URL, (annotations) =>
        pdf.getPage(1).then (page) =>
          @render_page pdf, 1, page, annotations.data
    .then null, ->
      @$pv.text "Error loading the document."

  render_page: (pdf, i, page, annotations) ->
    pp = new Page @docid, i,
      page: page
      annotations: annotations
      readOnly: @readOnly
    @$pv.append pp.$div

    if (i + 1 <= pdf.numPages)
      pdf.getPage(i + 1).then (page) =>
        @render_page pdf, i + 1, page, annotations

  get_annotations_route: '/annotation/'
  list_view_selector: '#listview'


class ImageViewPage extends ViewPage
  init: ->
    super()
    GET_ANN_URL = '/view/' + @docid + '/annotations'
    $img = $('<img>')
    $pv = $('#docview')
    $img.mousedown (e) ->
      e.preventDefault()
    $img.load ->
      image = this
      $.getJSON GET_ANN_URL, (annotations) ->
        page = new Page @docid, 0,
          image: image
          annotations: annotations.data
          readOnly: @readOnly
        page.$div.append $img
        $pv.append page.$div
    $img.attr('src', '/raw/' + @docid)

  get_annotations_route: '/annotation/'
  list_view_selector: '#listview'


class AudioViewPage extends ViewPage
  init: ->
    super()
    $pv = $('#docview')
    audioPlayer = new AudioPlayer @docid,
      readOnly: @readOnly
    $pv.append audioPlayer.$div

  get_annotations_route: '/audioannotation/'
  list_view_selector: '#listaudioview'
