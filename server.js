import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import multer from 'multer';
import routes from './routes/api.js';

const app = express();
const upload = multer({ dest: 'uploads/' });

const PORT = process.env.PORT || 3000;

// === MIDDLEWARE ===
app.use(express.json());

// === AUTH MIDDLEWARE ===
app.use((req, res, next) => {
  const auth = req.headers.authorization;
  if (!auth || auth !== `Bearer ${process.env.BRIDGIT_AI_API_KEY}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});

// === ROUTES ===
app.use('/api', routes);

app.listen(PORT, () => {
  console.log(`Bridgit AI API running on port ${PORT}`);
});
