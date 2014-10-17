view_pdf = (docid, pv, pdf) ->
    GET_ANN_URL = '/view/' + docid + '/annotations'
    $.getJSON GET_ANN_URL, (annotations) ->
        pdf.getPage(1).then (page) ->
            render_page docid, pv, pdf, 1, page, annotations.data

setGeom = ($div, geom) ->
    $div.css
        left: geom.posx + "px"
        top: geom.posy + "px"
        width: geom.width + "px"
        height: geom.height + "px"

class Selection
    constructor: (@$tld, @create) ->
        @x1 = 0
        @y1 = 0
        @x2 = 0
        @y2 = 0
        @$div = jQuery('<div>').addClass 'selectionDiv'
        @$tld.mousedown (e) => @mousedown e
        @$tld.mousemove (e) => @mousemove e
        @$tld.mouseup (e) => @mouseup e

    computeGeom: ->
        posx: Math.min @x1, @x2
        posy: Math.min @y1, @y2
        width: Math.abs(@x2 - @x1)
        height: Math.abs(@y2 - @y1)

    eventCoords: (e) ->
        tldOffset = @$tld.offset()
        return (
            x: e.pageX - tldOffset.left
            y: e.pageY - tldOffset.top
        )

    mousedown: (e) ->
        ec = @eventCoords e
        @x1 = ec.x
        @y1 = ec.y
        @$div.show()

    bigEnough: ->
        geom = @computeGeom()
        geom.width > 30 && geom.height > 30

    mouseup: ->
        @$div.hide()
        if @bigEnough()
            geom = @computeGeom()
            @create geom

    mousemove: (e) ->
        ec = @eventCoords e
        @x2 = ec.x
        @y2 = ec.y
        geom = @computeGeom()
        setGeom @$div, geom


class Annotation
    constructor: (@$tld, @docid, @page, @text, @annid, @geom) ->
        @$div = jQuery('<div>').addClass 'annotation'
        setGeom @$div, @geom
        $closeBtn = jQuery('<a>').text '[X]'
        @$div.append $closeBtn

        $closeBtn.click =>
            delDone = =>
                @$div.remove()
            if @annid
                ANN_URL = '/annotation/' + @annid
                $.ajax
                    url: ANN_URL
                    type: 'DELETE'
                    success: -> delDone()
            else
                delDone()

        $annText = jQuery('<div>').text(@text)
        @$div.append $annText

        $annText.editable (value, settings) =>
            @text = value
            @submitChanges()
            return value
        @$div.draggable
            stop: (ev, ui) =>
                @updateGeom(ev, ui)
                @submitChanges()
        @$div.resizable
            stop: (ev, ui) =>
                @updateGeom(ev, ui)
                @submitChanges()

    updateGeom: (e, ui) ->
        tldOffset = @$tld.offset()
        if e.type == 'dragstop'
            @geom.posx = ui.offset.left - tldOffset.left
            @geom.posy = ui.offset.top - tldOffset.top
        else if e.type == 'resizestop'
            @geom.width = ui.size.width
            @geom.height = ui.size.height

    submitChanges: ->
        if @annid
            type = 'PUT'
            url = '/annotation/' + @annid
        else
            type = 'POST'
            url = '/annotation/new'
        $.ajax
            type: type
            url: url
            data:
                posx: @geom.posx
                posy: @geom.posy
                width: @geom.width
                height: @geom.height
                doc: @docid
                page: @page
                value: @text
            success: (d) =>
                if type == 'POST'
                    @annid = d.id


render_page = (docid, pv, pdf, i, page, annotations) ->
    canvas = document.createElement 'canvas'
    context = canvas.getContext '2d'
    scale = 1.5
    viewport = page.getViewport scale
    canvas.width = viewport.width
    canvas.height = viewport.height
    $pdfPage = jQuery('<div>')
        .addClass('pdfPage')
        .css
            width: viewport.width + "px"
            height: viewport.height + "px"
    pdfPage = $pdfPage.get 0
    pdfPage.appendChild canvas
    pv.appendChild pdfPage
    page.render
        canvasContext: context
        viewport: viewport
    $textLayerDiv = jQuery("<div />")
        .addClass("textLayer")
        .css
            height: viewport.height + "px"
            width: viewport.width + "px"
    selection = new Selection $textLayerDiv, (geom) ->
        ann = new Annotation $textLayerDiv, docid, i, "", null, geom
        $pdfPage.append ann.$div
    $selectionDiv = selection.$div
    $pdfPage.append($selectionDiv)
    pdfPage.appendChild($textLayerDiv.get 0)
    page.getTextContent().then (textContent) ->
        pageNumber = i
        pageIndex = pageNumber - 1
        textLayer = new TextLayerBuilder
            textLayerDiv: $textLayerDiv.get(0)
            pageIndex: pageIndex
            viewport: viewport
        textLayer.setTextContent textContent
    .then null, (error) ->
        pv.innerHTML = "Error while rendering PDF."
        console.log ("Error while rendering PDF: " + error)
    anns = annotations[i]
    if anns
        for ann in anns
            annotation = new Annotation $textLayerDiv, docid, i, ann.text, ann.id, ann
            $pdfPage.append annotation.$div

    if (i+1 <= pdf.numPages)
        pdf.getPage(i+1).then (page) ->
            render_page docid, pv, pdf, i+1, page, annotations

view_fullscreen_enter = () ->
    $('#subnav').hide()
    $('#exitfullscreen').show()

view_fullscreen_exit = () ->
    $('#subnav').show()
    $('#exitfullscreen').hide()

view_init = (src, docid, url_post_comment) ->
    pv = document.getElementById "pdfview"
    PDFJS.getDocument(src).then (pdf) ->
        view_pdf(docid, pv, pdf)
    .then null, ->
        pv.innerHTML = "Error loading the document."
    $('#post_comment_form').submit (e) ->
      e.preventDefault()
      $.ajax
        type: 'POST'
        url: url_post_comment
        data: $(this).serialize()
        success: (data) ->
            comm = $('#comment').val()
            $li = $('<li>').text(comm)
            $('#comments').append $li

    $('#fullscreen_button').click (e) ->
        e.preventDefault()
        view_fullscreen_enter()
    $('#fullscreen_button_exit').click (e) ->
        e.preventDefault()
        view_fullscreen_exit()
    $('#toggle_annotations_button').click (e) ->
        $('.annotation').toggle()
