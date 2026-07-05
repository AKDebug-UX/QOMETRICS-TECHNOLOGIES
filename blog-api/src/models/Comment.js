const mongoose = require('mongoose');

const commentSchema = new mongoose.Schema(
  {
    body: {
      type:     String,
      required: [true, 'Comment body is required'],
      trim:     true,
      maxlength: [2000, 'Comment must be 2000 characters or fewer'],
    },
    author: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'User',
      required: true,
    },
    post: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'Post',
      required: true,
      index:    true,
    },
    /** Optional: parent comment ID for threaded replies */
    parentId: {
      type:    mongoose.Schema.Types.ObjectId,
      ref:     'Comment',
      default: null,
    },
    likes: {
      type:    [mongoose.Schema.Types.ObjectId],
      ref:     'User',
      default: [],
    },
    isDeleted: {
      type:    Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
    toJSON: { versionKey: false, virtuals: true },
  }
);

// Virtual: number of likes
commentSchema.virtual('likeCount').get(function () {
  return this.likes.length;
});

// Soft-delete: replace body when deleted
commentSchema.pre('save', function (next) {
  if (this.isDeleted) this.body = '[deleted]';
  next();
});

module.exports = mongoose.model('Comment', commentSchema);
