import express from 'express';
import multer from 'multer';
import * as pipelineController from '../controllers/pipelineController.js';

const router = express.Router();
const upload = multer({ dest: 'uploads/' });

router.post('/pipeline', upload.single('audio'), pipelineController.pipelineHandler);

router.get('/languages', pipelineController.getLanguagesHandler);
router.get('/voices', pipelineController.getVoicesHandler);

export default router;
