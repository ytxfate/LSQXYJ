var express = require('express');
var router = express.Router();
var request = require('request');
var session = require('express-session');
var util = require('util');

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('admin_login');
});

router.get('/admin_main', function(req, res, next) {
  res.render('admin_main');
});

// router.get('/centos', function(req, res, next) {
//     res.render('centos');
//   });

module.exports = router;
