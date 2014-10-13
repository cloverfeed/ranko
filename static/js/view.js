function view_pdf(pv, pdf) {
    pdf.getPage(1).then(function(page) {
        render_page(pv, pdf, 1, page);
    });
}

function render_page(pv, pdf, i, page) {
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    var scale = 1.5;
    var viewport = page.getViewport(scale);
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    var pdfPage = document.createElement('div');
    pdfPage.className = 'pdfPage';
    pdfPage.appendChild(canvas);
    pdfPage.style.width = viewport.width + "px";
    pdfPage.style.height = viewport.height + "px";
    pv.appendChild(pdfPage);
    var renderContext = {
        canvasContext: context,
        viewport: viewport,
    };
    page.render(renderContext);
    var $textLayerDiv = jQuery("<div />")
        .addClass("textLayer")
        .css("height", viewport.height + "px")
        .css("width", viewport.width + "px");
    pdfPage.appendChild($textLayerDiv.get(0));
    page.getTextContent().then(function(textContent) {
        var pageNumber = 1;
        var pageIndex = pageNumber - 1;
        var tlbOptions = {
            textLayerDiv: $textLayerDiv.get(0),
            pageIndex: pageIndex,
            viewport: viewport,
        };
        var textLayer = new TextLayerBuilder(tlbOptions);
        textLayer.setTextContent(textContent);
    }).then(null, function(error){
        pv.innerHTML = "Error while rendering PDF.";
        console.log("Error while rendering PDF: " + error);
    });

    if (i+1 <= pdf.numPages) {
        pdf.getPage(i+1).then(function(page){
            render_page(pv, pdf, i+1, page);
        });
    }
}

function view_fullscreen_enter() {
    $('#subnav').hide();
    $('#exitfullscreen').show();
}

function view_fullscreen_exit() {
    $('#subnav').show();
    $('#exitfullscreen').hide();
}
