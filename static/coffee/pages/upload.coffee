upload_init = ->
  s3u = new S3Uploader
    paramsUrl: '/params'
    $status: $('#status')
    $form: $("#upload_form")
    $uploadBtn: $("#upload_button")
  s3u.start()
