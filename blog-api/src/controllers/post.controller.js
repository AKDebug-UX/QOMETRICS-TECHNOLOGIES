const Post    = require('../models/Post');
const Comment = require('../models/Comment');

// ── Helpers ───────────────────────────────────────────────────────────────

/** Build pagination meta from query params */
const getPagination = (query) => {
  const page  = Math.max(1, parseInt(query.page)  || 1);
  const limit = Math.min(50, parseInt(query.limit) || 10);
  const skip  = (page - 1) * limit;
  return { page, limit, skip };
};

// ── Controllers ───────────────────────────────────────────────────────────

/**
 * @desc   Get all published posts (paginated, filterable)
 * @route  GET /api/posts
 * @access Public
 */
exports.getAllPosts = async (req, res, next) => {
  try {
    const { page, limit, skip } = getPagination(req.query);
    const { tag, search, author } = req.query;

    // Build filter
    const filter = { status: 'published' };
    if (tag)    filter.tags   = tag;
    if (author) filter.author = author;
    if (search) filter.$text  = { $search: search };

    const [posts, total] = await Promise.all([
      Post.find(filter)
        .populate('author', 'name email avatar')
        .populate('commentCount')
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .lean({ virtuals: true }),
      Post.countDocuments(filter),
    ]);

    res.json({
      success: true,
      pagination: { total, page, limit, totalPages: Math.ceil(total / limit) },
      data: posts,
    });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Get single post by ID or slug
 * @route  GET /api/posts/:idOrSlug
 * @access Public
 */
exports.getPost = async (req, res, next) => {
  try {
    const { idOrSlug } = req.params;
    const filter = idOrSlug.match(/^[a-f\d]{24}$/i)
      ? { _id: idOrSlug }
      : { slug: idOrSlug };

    const post = await Post.findOne(filter)
      .populate('author', 'name email avatar bio')
      .populate('commentCount')
      .lean({ virtuals: true });

    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    // Increment views (fire-and-forget)
    Post.findByIdAndUpdate(post._id, { $inc: { views: 1 } }).exec();

    res.json({ success: true, data: post });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Create a new post
 * @route  POST /api/posts
 * @access Private
 */
exports.createPost = async (req, res, next) => {
  try {
    const { title, content, tags, status, summary, coverImage } = req.body;

    const post = await Post.create({
      title, content, tags, status, summary, coverImage,
      author: req.user._id,
    });

    await post.populate('author', 'name email avatar');

    res.status(201).json({ success: true, data: post });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Update a post
 * @route  PUT /api/posts/:id
 * @access Private (owner or admin)
 */
exports.updatePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    // Ownership check
    if (post.author.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'You can only edit your own posts.' });
    }

    const allowed = ['title', 'content', 'tags', 'status', 'summary', 'coverImage'];
    allowed.forEach((field) => {
      if (req.body[field] !== undefined) post[field] = req.body[field];
    });

    await post.save();
    await post.populate('author', 'name email avatar');

    res.json({ success: true, data: post });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Delete a post
 * @route  DELETE /api/posts/:id
 * @access Private (owner or admin)
 */
exports.deletePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    if (post.author.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'You can only delete your own posts.' });
    }

    await Promise.all([
      post.deleteOne(),
      Comment.deleteMany({ post: post._id }),
    ]);

    res.json({ success: true, message: 'Post deleted successfully.' });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Toggle like on a post
 * @route  PATCH /api/posts/:id/like
 * @access Private
 */
exports.toggleLike = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    const userId  = req.user._id;
    const liked   = post.likes.some((id) => id.equals(userId));
    const update  = liked
      ? { $pull: { likes: userId } }
      : { $addToSet: { likes: userId } };

    const updated = await Post.findByIdAndUpdate(post._id, update, { new: true });

    res.json({
      success: true,
      liked:   !liked,
      likeCount: updated.likes.length,
    });
  } catch (err) {
    next(err);
  }
};

/**
 * @desc   Get current user's posts (including drafts)
 * @route  GET /api/posts/my
 * @access Private
 */
exports.getMyPosts = async (req, res, next) => {
  try {
    const { page, limit, skip } = getPagination(req.query);

    const [posts, total] = await Promise.all([
      Post.find({ author: req.user._id })
        .populate('commentCount')
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .lean({ virtuals: true }),
      Post.countDocuments({ author: req.user._id }),
    ]);

    res.json({
      success: true,
      pagination: { total, page, limit, totalPages: Math.ceil(total / limit) },
      data: posts,
    });
  } catch (err) {
    next(err);
  }
};
