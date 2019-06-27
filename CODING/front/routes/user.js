var express = require('express');
var router = express.Router();

router.get('/register', function(req, res, next) {
    res.render('user_register');
});

router.get('/main', function(req, res, next) {
    res.render('user_main');
});

router.get('/forget_password', function(req, res, next) {
    res.render('user_forget_pwd');
});

module.exports = router;
