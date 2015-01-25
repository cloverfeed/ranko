module.exports = function(grunt) {
  'use strict';

  // Project configuration.
  grunt.initConfig({
    jasmine : {
      src : 'static/gen/lib.js',
      options : {
        vendor : 'static/gen/vendor_js.js',
        helpers: 'static/vendor/jasmine-jquery.js',
        specs : 'static/gen/coffee_spec.js',
        template : require('grunt-template-jasmine-istanbul'),
        templateOptions: {
          coverage: 'reports/coverage.json',
          report: 'reports/coverage'
        }
      }
    },
  });

  grunt.loadNpmTasks('grunt-contrib-jasmine');

  grunt.registerTask('default', ['jasmine']);
};
