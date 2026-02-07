"""Google Speech-to-Text for Hindi voice notes."""

import os
import logging
import tempfile

logger = logging.getLogger('gitagpt.voice')


def transcribe_voice(file_path: str) -> str | None:
    """Transcribe a voice note file (OGG) to Hindi text using Google STT."""
    try:
        from google.cloud import speech
    except ImportError:
        # Fallback: use Gemini for audio transcription
        return _transcribe_with_gemini(file_path)

    try:
        client = speech.SpeechClient()

        with open(file_path, 'rb') as f:
            audio_content = f.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code='hi-IN',
            alternative_language_codes=['en-IN'],
        )

        response = client.recognize(config=config, audio=audio)

        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            logger.info(f"Voice transcription: {transcript[:100]}")
            return transcript

        logger.warning("No transcription results")
        return None

    except Exception as e:
        logger.error(f"STT error: {e}")
        return _transcribe_with_gemini(file_path)


def _transcribe_with_gemini(file_path: str) -> str | None:
    """Fallback: use Gemini to transcribe audio."""
    try:
        from google import genai

        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return None

        client = genai.Client(api_key=api_key)
        audio_file = client.files.upload(file=file_path)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                "Transcribe this audio to text. The speaker is likely speaking Hindi or Hinglish. "
                "Return ONLY the transcription, nothing else.",
                audio_file,
            ],
        )

        transcript = response.text.strip()
        logger.info(f"Gemini transcription: {transcript[:100]}")
        return transcript

    except Exception as e:
        logger.error(f"Gemini transcription error: {e}")
        return None
