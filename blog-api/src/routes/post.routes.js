const router = require('express').Router();
const { body, param } = require('express-validator');
const ctrl = require('../controllers/post.controller');
const commentCtrl = require('../controllers/comment.controller');
const { protect, optionalAuth } = require('../middleware/auth');
const validate = require('../middleware/validate');

const postRules = [
  body('title').trim().notEmpty().withMessage('Title is required').isLength({ max: 150 }),
  body('content').trim().notEmpty().withMessage('Content is required'),
  body('tags').optional().isArray(),
  body('status').optional().isIn(['draft', 'published']),
  body('summary').optional().trim().isLength({ max: 300 }),
];

const commentRules = [
  body('body').trim().notEmpty().withMessage('Comment body is required').isLength({ max: 2000 }),
];

router.get('/', optionalAuth, ctrl.getAllPosts);
router.get('/my', protect, ctrl.getMyPosts);
router.get('/:idOrSlug', ctrl.getPost);
router.post('/', protect, validate(postRules), ctrl.createPost);
router.put('/:id', protect, ctrl.updatePost);
router.delete('/:id', protect, ctrl.deletePost);
router.patch('/:id/like', protect, ctrl.toggleLike);

router.get('/:postId/comments', commentCtrl.getComments);
router.post('/:postId/comments', protect, validate(commentRules), commentCtrl.addComment);

module.exports = router;
