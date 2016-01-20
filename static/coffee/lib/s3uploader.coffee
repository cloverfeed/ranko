init = ->

class S3Uploader
  constructor: (params) ->
    @paramsUrl = params.paramsUrl
    @$status = params.$status
    @$form = params.$form
    @$uploadBtn = params.$uploadBtn

  log: (status) ->
    @$status.html status

  start: ->
    @$upload_button.click ->
        @$form.find("input[type=file]").click()
    @$form.fileupload
        autoUpload: true
        dataType: "xml"
        add: (event, data) ->
            log "fetching params"
            $.get(@paramsUrl).done (params) =>
                @$form.find('input[name=key]').val(params.key)
                @$form.find('input[name=policy]').val(params.policy)
                @$form.find('input[name=signature]').val(params.signature)
                data.submit()
        send: (event, data) ->
            log "sending"
        progress: (event, data) ->
            @$progress_bar.css "width", "#{Math.round((event.loaded / event.total) * 1000) / 10}%"
        fail: (event, data) ->
            log "failure"
        success: (event, data) ->
            log "success"
        done: (event, data) ->
            log "done"
