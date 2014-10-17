view_pdf = (docid, pv, pdf) ->
    GET_ANN_URL = '/view/' + docid + '/annotations'
    $.getJSON GET_ANN_URL, (annotations) ->
        pdf.getPage(1).then (page) ->
            render_page docid, pv, pdf, 1, page, annotations.data

setCoords = ($div, coords) ->
    $div.css
        left: coords.x1 + "px"
        top: coords.y1 + "px"
        width: coords.x2 - coords.x1 + "px"
        height: coords.y2 - coords.y1 + "px"

class Selection
    constructor: (@$tld, @create) ->
        @coords =
            x1: 0
            y1: 0
            x2: 0
            y2: 0
        @$div = jQuery('<div>').addClass 'selectionDiv'
        @$tld.mousedown (e) => @mousedown e
        @$tld.mousemove (e) => @mousemove e
        @$tld.mouseup (e) => @mouseup e

    eventCoords: (e) ->
        tldOffset = @$tld.offset()
        return (
            x: e.pageX - tldOffset.left
            y: e.pageY - tldOffset.top
        )

    mousedown: (e) ->
        ec = @eventCoords e
        @coords.x1 = ec.x
        @coords.y1 = ec.y
        @$div.show()

    bigEnough: ->
        width = @coords.x2 - @coords.x1
        height = @coords.y2 - @coords.y1
        width > 30 && height > 30

    mouseup: ->
        @$div.hide()
        if @bigEnough()
            @create(@coords)

    mousemove: (e) ->
        ec = @eventCoords e
        @coords.x2 = ec.x
        @coords.y2 = ec.y
        setCoords @$div, @coords


class Annotation
    constructor: (@docid, @page, text, @annid, @coords) ->
        @$div = jQuery('<div>').addClass 'annotation'
        setCoords @$div, @coords
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

        $annText = jQuery('<div>').text(text)
        @$div.append $annText

        $annText.editable (value, settings) => @submitChanges value, settings

    submitChanges: (value, settings) ->
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
                posx: @coords.x1
                posy: @coords.y1
                width: @coords.x2 - @coords.x1
                height: @coords.y2 - @coords.y1
                doc: @docid
                page: @page
                value: value
        return value


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
    selection = new Selection $textLayerDiv, (coords) ->
        ann = new Annotation docid, i, "", null, coords
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
            annotation = new Annotation docid, i, ann.text, ann.id,
                x1: ann.posx
                y1: ann.posy
                x2: ann.posx + ann.width
                y2: ann.posy + ann.height
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
