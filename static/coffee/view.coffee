view_pdf = (pv, pdf) ->
    pdf.getPage(1).then (page) ->
        render_page pv, pdf, 1, page

setCoords = ($div, coords) ->
    $div.css
        left: coords.x1 + "px"
        top: coords.y1 + "px"
        width: coords.x2 - coords.x1 + "px"
        height: coords.y2 - coords.y1 + "px"

makeSelectionDiv = ($pdfp, $tld) ->
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
            $ann = makeAnnotation sdCoords
            $pdfp.append $ann

    $tld.mousemove (e) ->
        ec = eventCoords e
        sdCoords.x2 = ec.x
        sdCoords.y2 = ec.y
        setCoords $sd, sdCoords

    return $sd

makeAnnotation = (coords) ->
    $ad = jQuery('<div>').addClass 'annotation'
    setCoords $ad, coords

    $closeBtn = jQuery('<a>').text '[X]'
    $ad.append $closeBtn

    $closeBtn.click ->
        $ad.remove()

    $annText = jQuery('<div>')
    $ad.append $annText

    console.log "makeann"
    $annText.editable (value, settings) -> return value

    return $ad

render_page = (pv, pdf, i, page) ->
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
    $selectionDiv = makeSelectionDiv $pdfPage, $textLayerDiv
    $pdfPage.append($selectionDiv)
    pdfPage.appendChild($textLayerDiv.get 0)
    page.getTextContent().then (textContent) ->
        pageNumber = 1
        pageIndex = pageNumber - 1
        textLayer = new TextLayerBuilder
            textLayerDiv: $textLayerDiv.get(0)
            pageIndex: pageIndex
            viewport: viewport
        textLayer.setTextContent textContent
    .then null, (error) ->
        pv.innerHTML = "Error while rendering PDF."
        console.log ("Error while rendering PDF: " + error)

    if (i+1 <= pdf.numPages)
        pdf.getPage(i+1).then (page) ->
            render_page pv, pdf, i+1, page

view_fullscreen_enter = () ->
    $('#subnav').hide()
    $('#exitfullscreen').show()

view_fullscreen_exit = () ->
    $('#subnav').show()
    $('#exitfullscreen').hide()
