# 🧠 BRIDGIT-AI — REAL-TIME MULTILINGUAL VOICE CHAT

## 🤬 READ THIS BEFORE YOU PUSH CODE  
These are the **non-negotiable rules**. Break one, and go f*** yourself.

---

## 1. 🔥 PIPELINES ARE LOCKED

- **Do NOT touch the existing STT → Translate → TTS pipeline.**
- It already works. It’s wired. It’s battle-tested. Don’t be a hero.
- No restructuring. No fancy “I had an idea…” crap.  
  **Only improve if you're told to.**

---

## 2. 🧠 ARCHITECTURE IS MODULAR FOR A REASON

- There are **TWO** backends:
  - `FastAPI` → session control, auth, tokens, user mapping.
  - `Node.js` → voice pipeline only. Audio in → audio out. That’s it.
- Keep them **separate**. Treat them like exes that don’t talk anymore.

---

## 3. 💬 ABLY IS OUR CHAT BACKBONE

- All messages flow through Ably.
- Channel structure is handled by **session logic**.
- **Host creates room**, **Friend joins room**, that's the flow.
- Don’t mess with token logic unless you're fixing a bug.

---

## 4. 🧼 DEFAULTS THAT STAY DEFAULT

- STT model: `scribe_v1` (ElevenLabs)  
- TTS model: `eleven_flash_v2_5`)  
- Default voice ID: `1GvTxqTIRSoKAPZZYJJe`  
- Translation: DeepL with proper source/target + params  
  Don’t “experiment.” This isn’t your playground.

---

## 5. 🔒 MESSAGE PRIVACY = MANDATORY

- Host sets the rules:
  - Playback once → disappears
  - Save for 24h → auto-delete after
  - Or: **solo mode** = no chat, just public playback
- Do not persist messages unless explicitly required.

---

## 6. 🛑 DON'T BE A DUMBASS

- Don’t rename files without a damn good reason.
- Don’t commit dead code or console spam.
- Don’t hardcode keys. We’re not amateurs.
- Don’t break the working pipeline trying to be “clever.”


---

Stay focused. Build like a savage.  
Leave the fluff to other teams.




Break each major section into its own dedicated file or folder — don’t shove 1000+ lines into one file. This codebase needs to be modular and readable. If it’s handling a unique responsibility, it belongs in its own file.




----------------------------------------------------

The current 2 pipelineS already includes language detection from STT and correctly sets both source_lang and target_lang before sending to DeepL TO TTS TO ABLY

✅ 1. HOST / JOIN MODE (Real-time 2-person chat using Ably)

👤 USER 1 (Host)

Clicks Host → then clicks Get Access Code

Ably generates a short access code (real channel)

User sees “Access Room” → joins the live Ably chatroom

Shares code manually with USER 2

👤 USER 2 (Joiner)

Clicks Join → enters code received

App connects both users to same Ably channel

They can now talk back-and-forth in real-time

🎤 VOICE FLOW (Updated with Language Preferences)

📥 USER 1 → USER 2 FLOW:

User 1 speaks in any language

Auto-detect: source_language (via ElevenLabs STT )

🔁 System checks User 2's preferred language

Translation: from detected source_lang → User 2's target_lang (DeepL API)

TTS: ElevenLabs

model_id: eleven_flash_v2_5

voice_id: dynamic per user (fallback = 1GvTxqTIRSoKAPZZYJJe)

Translated message is sent to Ably channel and played for User 2

Automatically or as voice card (based on UI)

Message obeys expiration setting (1-play, 1hr, 24hr)

📥 USER 2 → USER 1 FLOW:

Same exact process in reverse:

User 2 sends voice

Detected language → translated to User 1's preferred language

Playback auto-translated & voiced with User 1's preferred voice

System handles both directions independently but symmetrically

⚙️ REQUIREMENTS:

✅ Both users must have:

preferred_language (e.g. "EN", "FR", "AR")

preferred_voice_id (optional, default provided)

✅ All translation is routed through a middleware that:

Detects input language

Matches it to recipient’s preferred_language

Pipes translated output → TTS → Ably

🕵️ MESSAGE PRIVACY MODES (Snapchat-style)

The host sets message visibility BEFORE session begins:

disappear_after_playback (default Snapchat style)

expire_after_1hr

expire_after_24hr

persist (optional future mode)

⚠️ Note: Session auto-expires after 2 hours of inactivity

🧠 If host selects "ephemeral mode," messages are not saved to DB.

If "24hr mode," they live in-memory or temp store tied to that channel, not user.

🧍‍♂️ SOLO MODE (Tourist / Self-use Mode)

User clicks Solo

Sets source_lang + target_lang

Starts speaking — system runs through pipeline:

🎤 SOLO PIPELINE:

STT: ElevenLabs scribe_v1

Translate: DeepL API (same format)

TTS: ElevenLabs

model_id: eleven_flash_v2_5

Default voice_id: 1GvTxqTIRSoKAPZZYJJe

📢 OUTPUT

Plays back immediately on same device

Loop playback (optional)

No Ably. No DB. No chat history.

Think “talking to yourself” or “translating to a nearby person”

RECAP :

USER 1 DEVICE RECORDS -->

LANGUAGE, MOOD, SOUND, VOICE, ETC. DETECTED -->

STT  model ID  scribe_v1  (ELEVEN LABS ) https://elevenlabs.io/docs/api-reference/speech-to-text/convert

-->

translate ( Deep L ) https://api.deepl.com/v2/translate

HERE ARE THE PERAMS IM NOT SURE IF YOU NEED IT

{"translations":[{"detected_source_language":"EN","text":"HOLA, ¿CÓMO ESTÁS, ANI BANANI?","model_type_used":"quality_optimized"}]}

curl --request POST \

--url https://api.deepl.com/v2/translate \

--header 'Authorization: DeepL-Auth-Key THE REAL API KEY' \

--header 'Content-Type: application/json' \

--data '{

"split_sentences": "0",

"preserve_formatting": false,

"formality": "prefer_less",

"outline_detection": true,

"target_lang": "ES",

"source_lang": "EN",

"model_type": "prefer_quality_optimized",

"text": [

"HI HELLO HOW ARE YOU ANI BANANI "

]

}'

-->

TTS ( eleven labs )  model id   eleven_flash_v2_5  -->

Eleven labs Voice id dynamic but default voice id     1GvTxqTIRSoKAPZZYJJe    until user changes it  -->

user either clicks on re-record or clicks send if its clicked on re-record it clears the recorded file and goes back, if user clicks on SEND -->

SEND TO REAL TIME IN REAL TIME TO ABLY CONNECTED CHANNEL -->

( UNLESS ITS SOLO MODE THERE IS NO ABLY)