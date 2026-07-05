const mongoose = require('mongoose');

/**
 * Converts a title to a URL-safe slug.
 * e.g. "Hello World!" → "hello-world"
 */
function slugify(title) {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');
}

const postSchema = new mongoose.Schema(
  {
    title: {
      type:     String,
      required: [true, 'Title is required'],
      trim:     true,
      maxlength: [150, 'Title must be 150 characters or fewer'],
    },
    slug: {
      type:   String,
      unique: true,
      index:  true,
    },
    content: {
      type:     String,
      required: [true, 'Content is required'],
    },
    summary: {
      type:     String,
      trim:     true,
      maxlength: [300, 'Summary must be 300 characters or fewer'],
    },
    tags: {
      type:    [String],
      default: [],
    },
    coverImage: {
      type:    String,
      default: '',
    },
    status: {
      type:    String,
      enum:    ['draft', 'published'],
      default: 'published',
    },
    author: {
      type:     mongoose.Schema.Types.ObjectId,
      ref:      'User',
      required: true,
    },
    likes: {
      type:    [mongoose.Schema.Types.ObjectId],
      ref:     'User',
      default: [],
    },
    views: {
      type:    Number,
      default: 0,
    },
  },
  {
    timestamps: true,
    toJSON: { versionKey: false, virtuals: true },
    toObject: { virtuals: true },
  }
);

// Virtuals
postSchema.virtual('likeCount').get(function () {
  return this.likes.length;
});

postSchema.virtual('commentCount', {
  ref:          'Comment',
  localField:   '_id',
  foreignField: 'post',
  count:        true,
});

// Auto-generate unique slug on save
postSchema.pre('save', async function (next) {
  if (!this.isModified('title')) return next();

  let baseSlug = slugify(this.title);
  let slug     = baseSlug;
  let suffix   = 1;

  // Ensure uniqueness
  while (await mongoose.model('Post').exists({ slug, _id: { $ne: this._id } })) {
    slug = `${baseSlug}-${suffix++}`;
  }

  this.slug = slug;

  // Auto-generate summary from content if not provided
  if (!this.summary) {
    this.summary = this.content.replace(/[#*`]/g, '').substring(0, 280);
  }

  next();
});

// Text index for search
postSchema.index({ title: 'text', content: 'text', tags: 'text' });

module.exports = mongoose.model('Post', postSchema);
