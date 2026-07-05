const router   = require('express').Router();
const { body } = require('express-validator');
const ctrl     = require('../controllers/user.controller');
const { protect, restrictTo } = require('../middleware/auth');
const validate  = require('../middleware/validate');

/**
 * @swagger
 * tags:
 *   name: Users
 *   description: User profile management
 */

/**
 * @swagger
 * /api/users:
 *   get:
 *     summary: List all users (admin only)
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: page
 *         schema: { type: integer, default: 1 }
 *       - in: query
 *         name: limit
 *         schema: { type: integer, default: 20 }
 *     responses:
 *       200:
 *         description: List of all users
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       403:
 *         $ref: '#/components/responses/Forbidden'
 */
router.get('/', protect, restrictTo('admin'), ctrl.getAllUsers);

/**
 * @swagger
 * /api/users/me:
 *   patch:
 *     summary: Update current user's profile (name, bio, avatar)
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:   { type: string }
 *               bio:    { type: string }
 *               avatar: { type: string }
 *     responses:
 *       200:
 *         description: Profile updated
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *   delete:
 *     summary: Deactivate (soft-delete) current user's account
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Account deactivated
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 */
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

/**
 * @swagger
 * /api/users/{id}:
 *   get:
 *     summary: Get a public user profile
 *     tags: [Users]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Public user profile
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/UserProfile'
 *       404:
 *         $ref: '#/components/responses/NotFound'
 */
router.get('/:id', ctrl.getProfile);

module.exports = router;
