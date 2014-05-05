function view_pdf(pv, pdf) {
    for(var i = 1; i <= pdf.numPages ; i ++){
        pdf.getPage(i).then(function(page){
            var canvas = document.createElement('canvas');
            var context = canvas.getContext('2d');
            var scale = 1.2;
            var viewport = page.getViewport(scale);
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            page.render({canvasContext: context, viewport: viewport});
            pv.appendChild(canvas);
        });
    }
}
