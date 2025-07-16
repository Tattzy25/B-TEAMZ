import { neon } from '@neondatabase/serverless';

const sql = neon('postgresql://neondb_owner:npg_nyQXU3rBI2kV@ep-rapid-rain-adood2to-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require');

const posts = await sql('SELECT * FROM posts');
import * as pipelineService from '../services/pipelineService.js';

export const pipelineHandler = async (req, res) => {
  try {
    const result = await pipelineService.processPipeline(req);
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Pipeline failed', details: err.message });
  }
};

export const getLanguagesHandler = async (req, res) => {
  try {
    const languages = pipelineService.getSupportedLanguages();
    res.json(languages);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to get languages' });
  }
};

export const getVoicesHandler = async (req, res) => {
  try {
    const voices = await pipelineService.getVoices();
    res.json(voices);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch voices' });
  }
};
