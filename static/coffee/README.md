How this works
--------------

### `lib/*.coffee`

Generic component code.

### `spec/*.coffee`

Jasmine specs for the above.

### `pages/*.coffee`

Application components. The glue between frontend and backend. Typically,
functions that instanciate a component from `lib` and inject data from an Ajax
call.

Rules
-----

  - no explicit urls or selectors in `lib/`.
  - code from `pages/` is not tested so be careful (integration tests would be a
    nice solution here).
