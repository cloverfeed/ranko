describe 'RestClient', ->
  rest = null
  newId = 54

  beforeEach ->
    spyOn($, 'ajax').and.callFake (options) ->
      options.success
        id: newId

    base = '/base/'
    rest = new RestClient base

  it 'should POST a new object', ->
    obj =
      id: null

    rest.post_or_put obj,
      x: 1
      y: 2

    expect($.ajax).toHaveBeenCalledWith
      type: 'POST'
      url: '/base/new'
      data:
        x: 1
        y: 2
      success: jasmine.any(Function)
      error: jasmine.any(Function)
    expect(obj.id).toBe(newId)

  it 'should PUT an existing object', ->
    obj =
      id: 3

    rest.post_or_put obj,
      x: 1
      y: 2

    expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
      type: 'PUT'
      url: '/base/3'
      data:
        x: 1
        y: 2

  it 'can delete nonexisting objects', ->
    success = jasmine.createSpy('success')
    obj =
      id: null

    rest.delete(obj, success)

    expect(success).toHaveBeenCalled()

  it 'sends DELETE for existing objects', ->
    success = jasmine.createSpy('success')
    obj =
      id: 32

    rest.delete(obj, success)

    expect($.ajax).toHaveBeenCalledWith jasmine.objectContaining
      type: 'DELETE'
      url: '/base/32'
    expect(success).toHaveBeenCalled()

describe 'A RestClient that hits errors', ->
  errorText = 'An error occurred'
  rest = null
  restWithNoHandler = null
  errorSpy = null

  beforeEach ->
    spyOn($, 'ajax').and.callFake (options) ->
      options.error undefined, undefined, errorText

    base = '/base/'
    errorSpy = jasmine.createSpy 'error spy'
    rest = new RestClient base,
      error: errorSpy
    restWithNoHandler = new RestClient base

  it 'should not throw', ->
    obj =
      id: null

    expect(->
      restWithNoHandler.post_or_put obj,
        x: 1
        y: 2
    ).not.toThrow()

  it 'should call its callback when it exists', ->
    obj =
      id: null

    rest.post_or_put obj,
      x: 1
      y: 2

    expect(errorSpy).toHaveBeenCalledWith(errorText)
