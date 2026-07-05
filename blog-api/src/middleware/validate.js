const { validationResult } = require('express-validator');

/**
 * validate – runs express-validator checks and short-circuits with 422
 * if any validation errors are found.
 */
const validate = (validations) => async (req, res, next) => {
  // Run all validations
  await Promise.all(validations.map((v) => v.run(req)));

  const errors = validationResult(req);
  if (errors.isEmpty()) return next();

  return res.status(422).json({
    success: false,
    message: 'Validation failed.',
    errors:  errors.array().map(({ path, msg }) => ({ field: path, message: msg })),
  });
};

module.exports = validate;
