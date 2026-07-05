const router = require('express').Router();
const { body } = require('express-validator');
const ctrl = require('../controllers/user.controller');
const { protect, restrictTo } = require('../middleware/auth');
const validate = require('../middleware/validate');

router.get('/', protect, restrictTo('admin'), ctrl.getAllUsers);

router.patch(
  '/me',
  protect,
  validate([
    body('name').optional().trim().isLength({ max: 60 }),
    body('bio').optional().trim().isLength({ max: 300 }),
    body('avatar').optional().isURL(),
  ]),
  ctrl.updateProfile
);

router.delete('/me', protect, ctrl.deactivateAccount);
router.get('/:id', ctrl.getProfile);

module.exports = router;
