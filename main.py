from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import os
import tempfile
import librosa
import numpy as np
from typing import Dict
import logging
from pathlib import Path
import onnxruntime as ort
from concurrent.futures import ThreadPoolExecutor
import soundfile as sf
import nemo.collections.asr as nemo_asr
from pydub import AudioSegment
from nemo.collections.asr.models import EncDecCTCModelBPE
import io
import torchaudio,torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ASR Transcription Service",
    description="FastAPI application for Hindi speech recognition using NVIDIA NeMo ONNX model",
    version="1.0.0"
)

class ASRModel:
    def __init__(self):
        """Initialize the ONNX ASR model"""
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._load_model()
    
    def _load_model(self):
        """Load the ONNX model"""
        try:
            self.asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="stt_hi_conformer_ctc_medium")
            self.asr_model.eval()
            self.asr_model.preprocessor.featurizer.dither = 0.0
            self.asr_model.preprocessor.featurizer.pad_to = 0
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    
    def preprocess_audio_to_buffer(self,input_path: str):
        try:
            # Load and convert the audio
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            
            # Export to in-memory buffer
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            buffer.seek(0)
        except Exception as e:
            logger.error(f"Failed to preprocess audio: {str(e)}")
            raise
        return buffer
    
    def preprocess_audio(self, audio_path: str) -> np.ndarray:
        """Preprocess audio file for model input"""
        try:
            audio_buffer = self.preprocess_audio_to_buffer(audio_path)
    
            # Load waveform and sample rate from buffer
            waveform, sr = torchaudio.load(audio_buffer)
            duration = len(waveform) / sr
            
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
                waveform = resampler(waveform)
                
            # Move to correct device
            device = self.asr_model.device
            waveform = waveform.to(device)
            
            input_signal_length = torch.tensor([waveform.shape[1]], dtype=torch.int64, device=waveform.device)
            
            logger.info(f"Audio preprocessed: shape {waveform.shape}")#, duration {duration:.2f}s")
            return waveform, input_signal_length
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {str(e)}")
            raise
    
    def decode_prediction(self, logits: np.ndarray) -> str:
        """Decode model output to text"""
        try:
            decoded_text = self.asr_model.decoding.ctc_decoder_predictions_tensor(logits)
            logger.info(f"Decoded text: {decoded_text[0].text}")
            return decoded_text
            
        except Exception as e:
            logger.error(f"Decoding failed: {str(e)}")
            raise
    
    def _inference(self, audio: np.ndarray,input_signal_length: np.ndarray) -> str:
        """Run inference on preprocessed audio"""
        try:
            # # Run model
            logits,_,_ = self.asr_model.forward(input_signal=audio, input_signal_length=input_signal_length)
            
            # Decode to text
            text = self.decode_prediction(logits)
            return text
            
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise
    
    async def transcribe(self, audio_path: str) -> str:
        """Async transcription method"""
        try:
            # Preprocess audio
            audio = self.preprocess_audio(audio_path)
            
            # Run inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor, 
                self._inference, 
                audio[0],audio[1]
            )
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise

# # Initialize model (will be loaded at startup)
# model = None

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    global model
    try:
        model = ASRModel()
        logger.info("ASR model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ASR Transcription Service is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    model_status = "loaded" if model else "not loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "service": "ASR Transcription Service"
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Transcribe uploaded audio file
    
    Args:
        file: Audio file (.wav format, 5-10 seconds, 16kHz)
    
    Returns:
        JSON response with transcribed text
    """
    if not model:
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded. Please check server logs."
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.wav'):
        raise HTTPException(
            status_code=400,
            detail="Only .wav files are supported"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Validate audio file
        try:
            audio, sr = sf.read(temp_file_path)
            duration = len(audio) / sr
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio file: {str(e)}"
            )
        
        # Transcribe audio
        try:
            transcription = await model.transcribe(temp_file_path)
            
            return JSONResponse(
                content={
                    "transcription": transcription[0].text,
                    "filename": file.filename,
                    "duration": f"{duration:.2f}s",
                    "status": "success"
                }
            )
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0", port=8000,reload=False)