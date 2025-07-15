import axios from 'axios';
import Ably from 'ably';
import fs from 'fs';
import path from 'path';
import FormData from 'form-data';

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
const ABLY_API_KEY = process.env.ABLY_API_KEY;

export const processPipeline = async (req) => {
  const { source_language = 'auto', target_language, voice_id, channel_id } = req.body;
  const audioPath = req.file.path;

  // 1. STT (ElevenLabs)
  const sttForm = new FormData();
  sttForm.append('file', fs.createReadStream(audioPath));
  sttForm.append('model_id', 'scribe_v1_experimentay'); // updated model id as requested

  if (source_language !== 'auto') sttForm.append('language', source_language);

  const sttResp = await axios.post(
    'https://api.elevenlabs.io/v1/audio/transcriptions',
    sttForm,
    {
      headers: {
        ...sttForm.getHeaders(),
        'xi-api-key': ELEVENLABS_API_KEY,
      },
    }
  );
  const transcript = sttResp.data.text;

  // 2. Translation (DeepL)
  const deeplResp = await axios.post(
    'https://api.deepl.com/v2/translate',
    {
      split_sentences: "0",
      preserve_formatting: false,
      formality: "prefer_less",
      outline_detection: true,
      text: [transcript],
      target_lang: target_language,
      source_lang: source_language === 'auto' ? undefined : source_language,
      model_type: "prefer_quality_optimized"
    },
    {
      headers: {
        'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );
  const translatedText = deeplResp.data.translations[0].text;

  // 3. TTS (ElevenLabs)
  const ttsResp = await axios.post(
    'https://api.elevenlabs.io/v1/text-to-speech/' + voice_id,
    {
      text: translatedText,
      model_id: 'eleven_flash_v2_5',
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75
      }
    },
    {
      headers: {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
      },
      responseType: 'arraybuffer'
    }
  );
  const ttsAudioPath = path.join('uploads', `tts_${Date.now()}.mp3`);
  fs.writeFileSync(ttsAudioPath, ttsResp.data);

  // 4. Publish to Ably
  const ably = new Ably.Rest(ABLY_API_KEY);
  const audioBuffer = fs.readFileSync(ttsAudioPath);
  await ably.channels.get(channel_id).publish('audio', {
    audio: audioBuffer.toString('base64'),
    text: translatedText,
    transcript,
    language: target_language
  });

  // 5. Cleanup
  fs.unlinkSync(audioPath);
  fs.unlinkSync(ttsAudioPath);

  return {
    status: 'completed',
    transcript,
    translatedText,
    ably_channel: channel_id
  };
};

export const getSupportedLanguages = () => {
  return [
    { code: "en-GB", name: "English (British)" },
    { code: "en-US", name: "English (American)" },
    { code: "es", name: "Spanish" },
    { code: "fr", name: "French" },
    { code: "de", name: "German" },
    { code: "it", name: "Italian" },
    { code: "nl", name: "Dutch" },
    { code: "pt-PT", name: "Portuguese (European)" },
    { code: "pt-BR", name: "Portuguese (Brazilian)" },
    { code: "ru", name: "Russian" },
    { code: "ja", name: "Japanese" },
    { code: "zh", name: "Chinese (simplified)" },
    { code: "zh-HANS", name: "Chinese (simplified)" },
    { code: "zh-HANT", name: "Chinese (traditional)" },
    // ...add all supported languages
  ];
};

export const getVoices = async () => {
  const resp = await axios.get('https://api.elevenlabs.io/v1/voices', {
    headers: { 'xi-api-key': ELEVENLABS_API_KEY }
  });
  return resp.data.voices;
};
