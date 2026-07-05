const router = require('express').Router();
const { body } = require('express-validator');
const ctrl = require('../controllers/comment.controller');
const { protect } = require('../middleware/auth');
const validate = require('../middleware/validate');

router.put(
  '/:id',
  protect,
  validate([body('body').trim().notEmpty().isLength({ max: 2000 })]),
  ctrl.updateComment
);

router.delete('/:id', protect, ctrl.deleteComment);
router.patch('/:id/like', protect, ctrl.toggleLike);

module.exports = router;
