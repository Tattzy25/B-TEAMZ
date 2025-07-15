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
