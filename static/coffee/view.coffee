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

makeSelectionDiv = (docid, page, $pdfp, $tld) ->
    sdCoords =
        x1: 0
        y1: 0
        x2: 0
        y2: 0

    $sd = jQuery('<div>').addClass 'selectionDiv'

    eventCoords = (e) ->
        tldOffset = $tld.offset()
        return (
            x: e.pageX - tldOffset.left
            y: e.pageY - tldOffset.top
        )

    $tld.mousedown (e) ->
        ec = eventCoords e
        sdCoords.x1 = ec.x
        sdCoords.y1 = ec.y
        $sd.show()

    bigEnough = ->
        width = sdCoords.x2 - sdCoords.x1
        height = sdCoords.y2 - sdCoords.y1
        width > 30 && height > 30

    $tld.mouseup ->
        $sd.hide()
        if bigEnough()
            $ann = makeAnnotation docid, page, "", null, sdCoords
            $pdfp.append $ann

    $tld.mousemove (e) ->
        ec = eventCoords e
        sdCoords.x2 = ec.x
        sdCoords.y2 = ec.y
        setCoords $sd, sdCoords

    return $sd

makeAnnotation = (docid, page, text, annid, coords) ->
    $ad = jQuery('<div>').addClass 'annotation'
    setCoords $ad, coords

    $closeBtn = jQuery('<a>').text '[X]'
    $ad.append $closeBtn

    $closeBtn.click ->
        delDone = ->
            $ad.remove()
        if annid
            ANN_URL = '/annotation/' + annid
            $.ajax
                url: ANN_URL
                type: 'DELETE'
                success: -> delDone()
        else
            delDone()

    $annText = jQuery('<div>').text(text)
    $ad.append $annText

    POST_URL = '/annotation/new'
    $annText.editable POST_URL,
        submitdata:
            posx: coords.x1
            posy: coords.y1
            width: coords.x2 - coords.x1
            height: coords.y2 - coords.y1
            doc: docid
            page: page

    return $ad

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
    $selectionDiv = makeSelectionDiv docid, i, $pdfPage, $textLayerDiv
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
            $annDiv = makeAnnotation docid, i, ann.text, ann.id,
                x1: ann.posx
                y1: ann.posy
                x2: ann.posx + ann.width
                y2: ann.posy + ann.height
            $pdfPage.append $annDiv

    if (i+1 <= pdf.numPages)
        pdf.getPage(i+1).then (page) ->
            render_page docid, pv, pdf, i+1, page, annotations

view_fullscreen_enter = () ->
    $('#subnav').hide()
    $('#exitfullscreen').show()

view_fullscreen_exit = () ->
    $('#subnav').show()
    $('#exitfullscreen').hide()
