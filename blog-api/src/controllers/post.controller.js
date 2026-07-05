const Post    = require('../models/Post');
const Comment = require('../models/Comment');

const paginate = (query) => {
  const page  = Math.max(1, parseInt(query.page)  || 1);
  const limit = Math.min(50, parseInt(query.limit) || 10);
  return { page, limit, skip: (page - 1) * limit };
};

exports.getAllPosts = async (req, res, next) => {
  try {
    const { page, limit, skip } = paginate(req.query);
    const { tag, search, author } = req.query;

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

exports.getPost = async (req, res, next) => {
  try {
    const { idOrSlug } = req.params;
    const filter = idOrSlug.match(/^[a-f\d]{24}$/i) ? { _id: idOrSlug } : { slug: idOrSlug };

    const post = await Post.findOne(filter)
      .populate('author', 'name email avatar bio')
      .populate('commentCount')
      .lean({ virtuals: true });

    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    // fire-and-forget view count
    Post.findByIdAndUpdate(post._id, { $inc: { views: 1 } }).exec();

    res.json({ success: true, data: post });
  } catch (err) {
    next(err);
  }
};

exports.createPost = async (req, res, next) => {
  try {
    const { title, content, tags, status, summary, coverImage } = req.body;
    const post = await Post.create({ title, content, tags, status, summary, coverImage, author: req.user._id });
    await post.populate('author', 'name email avatar');
    res.status(201).json({ success: true, data: post });
  } catch (err) {
    next(err);
  }
};

exports.updatePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    if (post.author.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'You can only edit your own posts.' });
    }

    const allowed = ['title', 'content', 'tags', 'status', 'summary', 'coverImage'];
    allowed.forEach(f => { if (req.body[f] !== undefined) post[f] = req.body[f]; });

    await post.save();
    await post.populate('author', 'name email avatar');
    res.json({ success: true, data: post });
  } catch (err) {
    next(err);
  }
};

exports.deletePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    if (post.author.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'You can only delete your own posts.' });
    }

    await Promise.all([post.deleteOne(), Comment.deleteMany({ post: post._id })]);
    res.json({ success: true, message: 'Post deleted.' });
  } catch (err) {
    next(err);
  }
};

exports.toggleLike = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    const userId = req.user._id;
    const liked  = post.likes.some(id => id.equals(userId));
    const update = liked ? { $pull: { likes: userId } } : { $addToSet: { likes: userId } };

    const updated = await Post.findByIdAndUpdate(post._id, update, { new: true });
    res.json({ success: true, liked: !liked, likeCount: updated.likes.length });
  } catch (err) {
    next(err);
  }
};

exports.getMyPosts = async (req, res, next) => {
  try {
    const { page, limit, skip } = paginate(req.query);
    const [posts, total] = await Promise.all([
      Post.find({ author: req.user._id }).populate('commentCount').sort({ createdAt: -1 }).skip(skip).limit(limit).lean({ virtuals: true }),
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
