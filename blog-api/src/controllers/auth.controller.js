const jwt  = require('jsonwebtoken');
const User = require('../models/User');

// ── Helpers ───────────────────────────────────────────────────────────────

/** Send token response with access + refresh tokens */
const sendTokenResponse = async (user, statusCode, res) => {
  const accessToken  = user.generateAccessToken();
  const refreshToken = user.generateRefreshToken();

  // Persist refresh token on user document (allow up to 5 active sessions)
  await User.findByIdAndUpdate(user._id, {
    $push: {
      refreshTokens: {
        $each:  [refreshToken],
        $slice: -5, // keep only the last 5
      },
    },
  });

  res.status(statusCode).json({
    success: true,
    accessToken,
    refreshToken,
    user,
  });
};

// ── Controllers ───────────────────────────────────────────────────────────

/**
 * @desc   Register a new user
 * @route  POST /api/auth/register
 * @access Public
 */
exports.register = async (req, res, next) => {
  try {
    const { name, email, password, bio } = req.body;

    // Check for existing user
    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(409).json({ success: false, message: 'Email is already registered.' });
    }

    const user = await User.create({ name, email, password, bio });
    await sendTokenResponse(user, 201, res);
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Login user
 * @route  POST /api/auth/login
 * @access Public
 */
exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // Include password field explicitly (it's select: false on the schema)
    const user = await User.findOne({ email }).select('+password');
    if (!user || !(await user.comparePassword(password))) {
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });
    }

    if (!user.isActive) {
      return res.status(403).json({ success: false, message: 'Account has been deactivated.' });
    }

    await sendTokenResponse(user, 200, res);
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Refresh access token
 * @route  POST /api/auth/refresh
 * @access Public (requires valid refresh token)
 */
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

    // Rotate: remove old, issue new
    user.refreshTokens = user.refreshTokens.filter((t) => t !== refreshToken);
    await user.save({ validateBeforeSave: false });

    await sendTokenResponse(user, 200, res);
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Logout (invalidate refresh token)
 * @route  POST /api/auth/logout
 * @access Private
 */
exports.logout = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;

    if (refreshToken) {
      await User.findByIdAndUpdate(req.user._id, {
        $pull: { refreshTokens: refreshToken },
      });
    }

    res.json({ success: true, message: 'Logged out successfully.' });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Get current authenticated user
 * @route  GET /api/auth/me
 * @access Private
 */
exports.getMe = (req, res) => {
  res.json({ success: true, user: req.user });
};

/**
 * @desc   Change current user's password
 * @route  PATCH /api/auth/change-password
 * @access Private
 */
exports.changePassword = async (req, res, next) => {
  try {
    const { currentPassword, newPassword } = req.body;

    const user = await User.findById(req.user._id).select('+password');
    if (!(await user.comparePassword(currentPassword))) {
      return res.status(401).json({ success: false, message: 'Current password is incorrect.' });
    }

    user.password = newPassword;
    await user.save();

    // Invalidate all sessions
    await User.findByIdAndUpdate(user._id, { $set: { refreshTokens: [] } });

    res.json({ success: true, message: 'Password changed. Please log in again.' });
  } catch (err) {
    next(err);
  }
};
