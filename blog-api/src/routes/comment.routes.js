const router   = require('express').Router();
const { body } = require('express-validator');
const ctrl     = require('../controllers/comment.controller');
const { protect } = require('../middleware/auth');
const validate    = require('../middleware/validate');

/**
 * @swagger
 * tags:
 *   name: Comments
 *   description: Comment management (standalone endpoints)
 */

/**
 * @swagger
 * /api/comments/{id}:
 *   put:
 *     summary: Update a comment (owner only)
 *     tags: [Comments]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [body]
 *             properties:
 *               body:
 *                 type: string
 *                 maxLength: 2000
 *     responses:
 *       200:
 *         description: Comment updated
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       403:
 *         $ref: '#/components/responses/Forbidden'
 *       404:
 *         $ref: '#/components/responses/NotFound'
 */
router.put(
  '/:id',
  protect,
  validate([body('body').trim().notEmpty().isLength({ max: 2000 })]),
  ctrl.updateComment
);

/**
 * @swagger
 * /api/comments/{id}:
 *   delete:
 *     summary: Delete a comment – soft delete (owner or admin)
 *     tags: [Comments]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Comment deleted
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       403:
 *         $ref: '#/components/responses/Forbidden'
 *       404:
 *         $ref: '#/components/responses/NotFound'
 */
router.delete('/:id', protect, ctrl.deleteComment);

/**
 * @swagger
 * /api/comments/{id}/like:
 *   patch:
 *     summary: Toggle like on a comment
 *     tags: [Comments]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Like toggled
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 liked:
 *                   type: boolean
 *                 likeCount:
 *                   type: number
 */
router.patch('/:id/like', protect, ctrl.toggleLike);

module.exports = router;
