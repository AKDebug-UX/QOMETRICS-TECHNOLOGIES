# 📝 Blog API – Qometrics Technologies

A production-ready **RESTful Blog API** built with Node.js, Express, MongoDB, and JWT authentication.

## Features

| Feature | Detail |
|---|---|
| 🔐 Auth | JWT access tokens (7d) + refresh token rotation (30d) |
| 🔑 Password security | bcrypt (12 rounds) hashing |
| 📝 Posts | Full CRUD, slugs, tags, full-text search, likes, views |
| 💬 Comments | Nested replies, soft-delete, likes |
| 👤 Users | Public profiles, RBAC (user/admin) |
| 📖 Docs | Swagger UI at `/api-docs` |
| 🛡️ Security | Helmet, CORS, rate limiting, input validation |
| 🚀 Deploy-ready | Procfile + environment config |

## Project Structure

```
blog-api/
├── server.js                    ← Entry point
├── src/
│   ├── app.js                   ← Express app setup
│   ├── config/
│   │   ├── db.js                ← MongoDB connection
│   │   └── swagger.js           ← OpenAPI spec
│   ├── middleware/
│   │   ├── auth.js              ← JWT protect / restrictTo / optionalAuth
│   │   ├── validate.js          ← express-validator middleware factory
│   │   └── errorHandler.js      ← Global error handler
│   ├── models/
│   │   ├── User.js              ← Mongoose User model
│   │   ├── Post.js              ← Mongoose Post model (auto-slug)
│   │   └── Comment.js           ← Mongoose Comment model (soft-delete)
│   ├── controllers/
│   │   ├── auth.controller.js
│   │   ├── post.controller.js
│   │   ├── comment.controller.js
│   │   └── user.controller.js
│   └── routes/
│       ├── auth.routes.js       ← /api/auth/*
│       ├── post.routes.js       ← /api/posts/*
│       ├── comment.routes.js    ← /api/comments/*
│       └── user.routes.js       ← /api/users/*
├── .env                         ← Local env (not committed)
├── .env.example                 ← Template
├── .gitignore
├── package.json
└── README.md
```

## Getting Started

### Prerequisites
- Node.js ≥ 18
- MongoDB (local or [Atlas](https://www.mongodb.com/atlas))

### Installation

```bash
# 1. Navigate to the project
cd "e:\QOMETRICS TECHNOLOGIES\blog-api"

# 2. Install dependencies
npm install

# 3. Copy env template and fill in values
copy .env.example .env

# 4. Start development server (with auto-reload)
npm run dev
```

Visit:
- **API**: `http://localhost:5000`
- **Swagger UI**: `http://localhost:5000/api-docs`
- **Health**: `http://localhost:5000/health`

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/register` | Public | Register new user |
| POST | `/login` | Public | Login & get tokens |
| POST | `/refresh` | Public | Refresh access token |
| POST | `/logout` | Private | Logout (invalidate refresh token) |
| GET | `/me` | Private | Get current user |
| PATCH | `/change-password` | Private | Change password |

### Posts (`/api/posts`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/` | Public | List published posts (paginated) |
| GET | `/my` | Private | My posts (incl. drafts) |
| GET | `/:idOrSlug` | Public | Get post by ID or slug |
| POST | `/` | Private | Create post |
| PUT | `/:id` | Private (owner/admin) | Update post |
| DELETE | `/:id` | Private (owner/admin) | Delete post + comments |
| PATCH | `/:id/like` | Private | Toggle like |
| GET | `/:postId/comments` | Public | Get post's comments |
| POST | `/:postId/comments` | Private | Add comment |

### Comments (`/api/comments`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| PUT | `/:id` | Private (owner) | Update comment |
| DELETE | `/:id` | Private (owner/admin) | Soft-delete comment |
| PATCH | `/:id/like` | Private | Toggle like |

### Users (`/api/users`)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/` | Admin only | List all users |
| GET | `/:id` | Public | Public profile |
| PATCH | `/me` | Private | Update own profile |
| DELETE | `/me` | Private | Deactivate account |

## Authentication Flow

```
1. POST /api/auth/register  →  { accessToken, refreshToken }
2. Use accessToken in header:  Authorization: Bearer <token>
3. When expired, POST /api/auth/refresh with { refreshToken }
4. Logout:  POST /api/auth/logout  (invalidates refresh token)
```

## Query Parameters (GET /api/posts)

| Param | Type | Description |
|-------|------|-------------|
| `page` | number | Page number (default: 1) |
| `limit` | number | Items per page (max: 50, default: 10) |
| `tag` | string | Filter by tag |
| `search` | string | Full-text search |
| `author` | string | Filter by author ID |

## Deploying to Render

1. Push to GitHub
2. New Web Service on [render.com](https://render.com)
3. Build command: `npm install`
4. Start command: `node server.js`
5. Add environment variables (from `.env.example`)
6. Add a **MongoDB Atlas** connection string as `MONGO_URI`

## Deploying to Railway

1. Push to GitHub → [railway.app](https://railway.app) → New from GitHub
2. Add **MongoDB** plugin or use Atlas
3. Set environment variables in Railway dashboard
4. Railway auto-detects `npm start`
