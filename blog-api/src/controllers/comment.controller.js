const Comment = require('../models/Comment');
const Post    = require('../models/Post');

exports.getComments = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.postId);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    const comments = await Comment.find({ post: req.params.postId, isDeleted: false })
      .populate('author', 'name avatar')
      .sort({ createdAt: 1 })
      .lean({ virtuals: true });

    res.json({ success: true, count: comments.length, data: comments });
  } catch (err) {
    next(err);
  }
};

exports.addComment = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.postId);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found.' });

    const { body, parentId } = req.body;

    if (parentId) {
      const parent = await Comment.findOne({ _id: parentId, post: post._id });
      if (!parent) {
        return res.status(404).json({ success: false, message: 'Parent comment not found.' });
      }
    }

    const comment = await Comment.create({
      body,
      author: req.user._id,
      post: post._id,
      parentId: parentId || null,
    });

    await comment.populate('author', 'name avatar');
    res.status(201).json({ success: true, data: comment });
  } catch (err) {
    next(err);
  }
};

exports.updateComment = async (req, res, next) => {
  try {
    const comment = await Comment.findById(req.params.id);
    if (!comment || comment.isDeleted) {
      return res.status(404).json({ success: false, message: 'Comment not found.' });
    }

    if (comment.author.toString() !== req.user._id.toString()) {
      return res.status(403).json({ success: false, message: 'You can only edit your own comments.' });
    }

    comment.body = req.body.body;
    await comment.save();
    await comment.populate('author', 'name avatar');

    res.json({ success: true, data: comment });
  } catch (err) {
    next(err);
  }
};

exports.deleteComment = async (req, res, next) => {
  try {
    const comment = await Comment.findById(req.params.id);
    if (!comment) return res.status(404).json({ success: false, message: 'Comment not found.' });

    const isOwner = comment.author.toString() === req.user._id.toString();
    if (!isOwner && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'You can only delete your own comments.' });
    }

    comment.isDeleted = true;
    await comment.save();

    res.json({ success: true, message: 'Comment deleted.' });
  } catch (err) {
    next(err);
  }
};

exports.toggleLike = async (req, res, next) => {
  try {
    const comment = await Comment.findById(req.params.id);
    if (!comment) return res.status(404).json({ success: false, message: 'Comment not found.' });

    const userId = req.user._id;
    const liked = comment.likes.some((id) => id.equals(userId));
    const update = liked
      ? { $pull: { likes: userId } }
      : { $addToSet: { likes: userId } };

    const updated = await Comment.findByIdAndUpdate(comment._id, update, { new: true });

    res.json({ success: true, liked: !liked, likeCount: updated.likes.length });
  } catch (err) {
    next(err);
  }
};
