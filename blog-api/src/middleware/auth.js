const jwt  = require('jsonwebtoken');
const User = require('../models/User');

/**
 * protect – verifies the JWT in the Authorization header.
 * Sets req.user to the authenticated user document.
 */
const protect = async (req, res, next) => {
  try {
    // 1. Extract token
    let token;
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      token = authHeader.split(' ')[1];
    }

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. No token provided.',
      });
    }

    // 2. Verify token
    let decoded;
    try {
      decoded = jwt.verify(token, process.env.JWT_SECRET);
    } catch (err) {
      const msg = err.name === 'TokenExpiredError'
        ? 'Token has expired. Please log in again.'
        : 'Invalid token. Please log in again.';
      return res.status(401).json({ success: false, message: msg });
    }

    // 3. Check user still exists
    const user = await User.findById(decoded.id).select('+passwordChangedAt');
    if (!user || !user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'The user belonging to this token no longer exists.',
      });
    }

    // 4. Check password hasn't changed since token was issued
    if (user.changedPasswordAfter(decoded.iat)) {
      return res.status(401).json({
        success: false,
        message: 'Password was recently changed. Please log in again.',
      });
    }

    // 5. Attach user to request
    req.user = user;
    next();
  } catch (err) {
    next(err);
  }
};

/**
 * restrictTo – role-based access control.
 * Usage: restrictTo('admin') or restrictTo('admin', 'moderator')
 */
const restrictTo = (...roles) => (req, res, next) => {
  if (!roles.includes(req.user.role)) {
    return res.status(403).json({
      success: false,
      message: 'You do not have permission to perform this action.',
    });
  }
  next();
};

/**
 * optionalAuth – attaches req.user if a valid token is present,
 * but does not block unauthenticated requests.
 */
const optionalAuth = async (req, _res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.split(' ')[1];
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      req.user = await User.findById(decoded.id);
    }
  } catch (_) {
    // silently ignore invalid/expired tokens in optional auth
  }
  next();
};

module.exports = { protect, restrictTo, optionalAuth };
