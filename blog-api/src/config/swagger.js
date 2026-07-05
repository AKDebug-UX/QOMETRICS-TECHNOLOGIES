const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: '📝 Blog API',
      version: '1.0.0',
      description: `
A production-ready RESTful Blog API built with **Node.js**, **Express**, and **MongoDB**.

### Features
- 🔐 JWT-based authentication (access + refresh tokens)
- 👤 User registration, login, and profile management
- 📝 Full CRUD for blog posts with pagination & filtering
- 💬 Nested comments on posts
- 🛡️ Rate limiting, input validation, and security headers

### Authentication
All protected routes require a Bearer token in the Authorization header:
\`Authorization: Bearer <your_jwt_token>\`

Get a token by registering at \`POST /api/auth/register\` or logging in at \`POST /api/auth/login\`.
      `,
      contact: {
        name:  'Qometrics Technologies',
        email: 'dev@qometrics.tech',
      },
      license: { name: 'MIT' },
    },
    servers: [
      { url: 'http://localhost:5000', description: 'Development server' },
      { url: 'https://your-app.onrender.com', description: 'Production server' },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type:         'http',
          scheme:       'bearer',
          bearerFormat: 'JWT',
          description:  'Enter your JWT access token',
        },
      },
      schemas: {
        // ── User ──────────────────────────────────────────────────────
        UserRegister: {
          type: 'object',
          required: ['name', 'email', 'password'],
          properties: {
            name:     { type: 'string', example: 'Alice Okafor' },
            email:    { type: 'string', format: 'email', example: 'alice@example.com' },
            password: { type: 'string', minLength: 8, example: 'SecurePass123!' },
            bio:      { type: 'string', example: 'Software engineer at Qometrics.' },
          },
        },
        UserLogin: {
          type: 'object',
          required: ['email', 'password'],
          properties: {
            email:    { type: 'string', format: 'email', example: 'alice@example.com' },
            password: { type: 'string', example: 'SecurePass123!' },
          },
        },
        UserProfile: {
          type: 'object',
          properties: {
            _id:       { type: 'string', example: '6657c1f2e4b09a12345abcde' },
            name:      { type: 'string', example: 'Alice Okafor' },
            email:     { type: 'string', example: 'alice@example.com' },
            bio:       { type: 'string', example: 'Software engineer.' },
            role:      { type: 'string', enum: ['user', 'admin'], example: 'user' },
            createdAt: { type: 'string', format: 'date-time' },
          },
        },
        AuthResponse: {
          type: 'object',
          properties: {
            success:      { type: 'boolean', example: true },
            accessToken:  { type: 'string', example: 'eyJhbGci...' },
            refreshToken: { type: 'string', example: 'eyJhbGci...' },
            user:         { $ref: '#/components/schemas/UserProfile' },
          },
        },
        // ── Post ──────────────────────────────────────────────────────
        PostCreate: {
          type: 'object',
          required: ['title', 'content'],
          properties: {
            title:   { type: 'string', example: 'Getting Started with Node.js' },
            content: { type: 'string', example: 'Node.js is a JavaScript runtime…' },
            tags:    { type: 'array', items: { type: 'string' }, example: ['nodejs', 'backend'] },
            status:  { type: 'string', enum: ['draft', 'published'], example: 'published' },
          },
        },
        Post: {
          type: 'object',
          properties: {
            _id:           { type: 'string' },
            title:         { type: 'string' },
            content:       { type: 'string' },
            slug:          { type: 'string', example: 'getting-started-with-nodejs' },
            tags:          { type: 'array', items: { type: 'string' } },
            status:        { type: 'string', enum: ['draft', 'published'] },
            likes:         { type: 'number', example: 42 },
            author:        { $ref: '#/components/schemas/UserProfile' },
            commentCount:  { type: 'number', example: 7 },
            createdAt:     { type: 'string', format: 'date-time' },
            updatedAt:     { type: 'string', format: 'date-time' },
          },
        },
        // ── Comment ───────────────────────────────────────────────────
        CommentCreate: {
          type: 'object',
          required: ['body'],
          properties: {
            body:     { type: 'string', example: 'Great article, very helpful!' },
            parentId: { type: 'string', description: 'Optional ID of parent comment for replies', example: null },
          },
        },
        Comment: {
          type: 'object',
          properties: {
            _id:       { type: 'string' },
            body:      { type: 'string' },
            author:    { $ref: '#/components/schemas/UserProfile' },
            post:      { type: 'string' },
            parentId:  { type: 'string', nullable: true },
            createdAt: { type: 'string', format: 'date-time' },
          },
        },
        // ── Errors ────────────────────────────────────────────────────
        Error: {
          type: 'object',
          properties: {
            success: { type: 'boolean', example: false },
            message: { type: 'string', example: 'An error occurred.' },
            errors:  { type: 'array', items: { type: 'object' }, description: 'Validation errors array' },
          },
        },
        Pagination: {
          type: 'object',
          properties: {
            total:       { type: 'number', example: 50 },
            page:        { type: 'number', example: 1 },
            limit:       { type: 'number', example: 10 },
            totalPages:  { type: 'number', example: 5 },
          },
        },
      },
      responses: {
        Unauthorized: {
          description: 'Unauthorized – missing or invalid JWT token',
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } },
        },
        Forbidden: {
          description: 'Forbidden – insufficient permissions',
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } },
        },
        NotFound: {
          description: 'Resource not found',
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } },
        },
        ValidationError: {
          description: 'Input validation failed',
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Error' } } },
        },
      },
    },
  },
  apis: ['./src/routes/*.js'],
};

module.exports = swaggerJsdoc(options);
