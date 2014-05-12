function view_pdf(pv, pdf) {
    pdf.getPage(1).then(function(page) {
        render_page(pv, pdf, 1, page);
    });
}

function render_page(pv, pdf, i, page) {
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    var scale = 1.2;
    var viewport = page.getViewport(scale);
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    page.render({canvasContext: context, viewport: viewport});
    pv.appendChild(canvas);

    if (i+1 <= pdf.numPages) {
        pdf.getPage(i+1).then(function(page){
            render_page(pv, pdf, i+1, page);
        });
    }
}
