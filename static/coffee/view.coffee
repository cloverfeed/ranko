view_pdf = (pv, pdf) ->
    pdf.getPage(1).then (page) ->
        render_page pv, pdf, 1, page

render_page = (pv, pdf, i, page) ->
    canvas = document.createElement 'canvas'
    context = canvas.getContext '2d'
    scale = 1.5
    viewport = page.getViewport scale
    canvas.width = viewport.width
    canvas.height = viewport.height
    pdfPage = document.createElement 'div'
    pdfPage.className = 'pdfPage'
    pdfPage.appendChild canvas
    pdfPage.style.width = viewport.width + "px"
    pdfPage.style.height = viewport.height + "px"
    pv.appendChild pdfPage
    page.render
        canvasContext: context
        viewport: viewport
    $textLayerDiv = jQuery("<div />")
        .addClass("textLayer")
        .css("height", viewport.height + "px")
        .css("width", viewport.width + "px")
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
