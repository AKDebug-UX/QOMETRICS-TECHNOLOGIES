const jwt  = require('jsonwebtoken');
const User = require('../models/User');

const sendTokenResponse = async (user, statusCode, res) => {
  const accessToken  = user.generateAccessToken();
  const refreshToken = user.generateRefreshToken();

  // keep at most 5 active sessions
  await User.findByIdAndUpdate(user._id, {
    $push: { refreshTokens: { $each: [refreshToken], $slice: -5 } },
  });

  res.status(statusCode).json({ success: true, accessToken, refreshToken, user });
};

exports.register = async (req, res, next) => {
  try {
    const { name, email, password, bio } = req.body;

    if (await User.findOne({ email })) {
      return res.status(409).json({ success: false, message: 'Email is already registered.' });
    }

    const user = await User.create({ name, email, password, bio });
    await sendTokenResponse(user, 201, res);
  } catch (err) {
    next(err);
  }
};

exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email }).select('+password');

    if (!user || !(await user.comparePassword(password))) {
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });
    }
    if (!user.isActive) {
      return res.status(403).json({ success: false, message: 'Account deactivated.' });
    }

    await sendTokenResponse(user, 200, res);
  } catch (err) {
    next(err);
  }
};

exports.refresh = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    if (!refreshToken) {
      return res.status(400).json({ success: false, message: 'Refresh token is required.' });
    }

    let decoded;
    try {
      decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    } catch {
      return res.status(401).json({ success: false, message: 'Invalid or expired refresh token.' });
    }

    const user = await User.findById(decoded.id).select('+refreshTokens');
    if (!user || !user.refreshTokens.includes(refreshToken)) {
      return res.status(401).json({ success: false, message: 'Refresh token not recognised.' });
    }

    user.refreshTokens = user.refreshTokens.filter(t => t !== refreshToken);
    await user.save({ validateBeforeSave: false });

    await sendTokenResponse(user, 200, res);
  } catch (err) {
    next(err);
  }
};

exports.logout = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;
    if (refreshToken) {
      await User.findByIdAndUpdate(req.user._id, { $pull: { refreshTokens: refreshToken } });
    }
    res.json({ success: true, message: 'Logged out.' });
  } catch (err) {
    next(err);
  }
};

exports.getMe = (req, res) => {
  res.json({ success: true, user: req.user });
};

exports.changePassword = async (req, res, next) => {
  try {
    const { currentPassword, newPassword } = req.body;
    const user = await User.findById(req.user._id).select('+password');

    if (!(await user.comparePassword(currentPassword))) {
      return res.status(401).json({ success: false, message: 'Current password is incorrect.' });
    }

    user.password = newPassword;
    await user.save();
    await User.findByIdAndUpdate(user._id, { $set: { refreshTokens: [] } });

    res.json({ success: true, message: 'Password changed. Please log in again.' });
  } catch (err) {
    next(err);
  }
};
