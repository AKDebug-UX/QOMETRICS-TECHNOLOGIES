const User = require('../models/User');
const Post = require('../models/Post');

exports.getProfile = async (req, res, next) => {
  try {
    const user = await User.findById(req.params.id).select('-refreshTokens -passwordChangedAt');
    if (!user || !user.isActive) {
      return res.status(404).json({ success: false, message: 'User not found.' });
    }

    const postCount = await Post.countDocuments({ author: user._id, status: 'published' });

    res.json({ success: true, data: { ...user.toJSON(), postCount } });
  } catch (err) {
    next(err);
  }
};

exports.updateProfile = async (req, res, next) => {
  try {
    const allowed = ['name', 'bio', 'avatar'];
    const updates = {};
    allowed.forEach((f) => { if (req.body[f] !== undefined) updates[f] = req.body[f]; });

    const user = await User.findByIdAndUpdate(req.user._id, updates, {
      new: true,
      runValidators: true,
    });

    res.json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
};

exports.deactivateAccount = async (req, res, next) => {
  try {
    await User.findByIdAndUpdate(req.user._id, { isActive: false, refreshTokens: [] });
    res.json({ success: true, message: 'Account deactivated.' });
  } catch (err) {
    next(err);
  }
};

exports.getAllUsers = async (req, res, next) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(50, parseInt(req.query.limit) || 20);
    const skip = (page - 1) * limit;

    const [users, total] = await Promise.all([
      User.find().skip(skip).limit(limit).sort({ createdAt: -1 }),
      User.countDocuments(),
    ]);

    res.json({
      success: true,
      pagination: { total, page, limit, totalPages: Math.ceil(total / limit) },
      data: users,
    });
  } catch (err) {
    next(err);
  }
};
