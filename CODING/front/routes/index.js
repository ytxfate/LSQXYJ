var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index');
});

router.get('/get_area_weather_detail', function(req, res, next) {
  var area = req.query.area;
  var father = req.query.father;
  if (area) {
    res.render('get_area_weather_detail', { area: area, father: father });
  }
});

// router.get('/socketio', function(req, res, next) {
//   res.render('socketio');
// });
module.exports = router;
