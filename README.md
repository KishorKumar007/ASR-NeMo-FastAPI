# ASR Transcription Service

A FastAPI-based Automatic Speech Recognition (ASR) service using NVIDIA NeMo's Hindi Conformer CTC model, optimized with ONNX for efficient inference.

## Features

- **Hindi Speech Recognition**: Uses NVIDIA NeMo's `stt_hi_conformer_ctc_medium` model
- **ONNX Optimization**: Model converted to ONNX format for faster inference
- **FastAPI Backend**: RESTful API with automatic documentation
- **Docker Support**: Fully containerized application
- **Async Processing**: Non-blocking audio transcription
- **Input Validation**: Supports .wav files, 5-10 seconds duration, 16kHz sampling rate

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd asr-transcription-service
   ```

2. **Build the Docker image**
   ```bash
   docker build -t asr-service .
   ```

3. **Run the container**
   ```bash
   docker run -p 8000:8000 asr-service
   ```

The service will be available at `http://localhost:8000`

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Convert model to ONNX** (first time only)
   ```bash
   python convert_to_onnx.py
   ```

3. **Start the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Transcribe Audio
```bash
curl -X POST "http://localhost:8000/transcribe" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_audio.wav"
```

**Example Response:**
```json
{
  "transcription": "आपका ऑडियो ट्रांस्क्रिप्शन यहाँ होगा",
  "filename": "your_audio.wav",
  "duration": "7.50s",
  "status": "success"
}
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/transcribe"
files = {"file": open("your_audio.wav", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using Postman
1. Set method to `POST`
2. URL: `http://localhost:8000/transcribe`
3. Body → form-data
4. Key: `file` (type: File)
5. Value: Select your .wav audio file

## Audio Requirements

- **Format**: .wav files only
- **Duration**: 5-10 seconds
- **Sample Rate**: 16kHz (recommended)
- **Channels**: Mono (recommended)

## API Documentation

Once the service is running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
asr-transcription-service/
├── main.py                 # FastAPI application
├── convert_to_onnx.py     # Model conversion script  
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── README.md            # This file
├── Description.md       # Development documentation
├── models/              # ONNX models directory
│   └── stt_hi_conformer_ctc_medium.onnx
└── test_audio/          # Sample audio files (optional)
    └── sample.wav
```

## Design Considerations

### Performance Optimization
- **ONNX Runtime**: Faster inference compared to PyTorch
- **Async Processing**: Non-blocking audio processing using thread pools
- **Resource Management**: Automatic cleanup of temporary files

### Scalability
- **Containerized**: Easy deployment and scaling with Docker
- **Health Checks**: Built-in health monitoring endpoints
- **Error Handling**: Comprehensive error handling and logging

### Security & Validation
- **File Type Validation**: Only accepts .wav files
- **Duration Limits**: Enforces 5-10 second audio duration
- **Input Sanitization**: Validates audio properties before processing

## Environment Variables

- `MODEL_PATH`: Path to ONNX model file (default: `/app/models/stt_hi_conformer_ctc_medium.onnx`)
- `PYTHONUNBUFFERED`: Set to 1 for real-time logging

## Troubleshooting

### Common Issues

1. **Model not found error**
   - Ensure the ONNX model is converted: `python convert_to_onnx.py`
   - Check the `MODEL_PATH` environment variable

2. **Audio format errors**
   - Convert audio to .wav format using ffmpeg: `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`

3. **Duration validation fails**
   - Trim audio to 5-10 seconds: `ffmpeg -i input.wav -t 10 -ss 0 output.wav`

4. **Container fails to start**
   - Check Docker logs: `docker logs <container-id>`
   - Ensure sufficient memory (recommend 4GB+)

### Performance Tips

- **CPU Usage**: The service uses CPU by default. For GPU acceleration, modify the ONNX Runtime providers in `main.py`
- **Memory**: Allocate at least 4GB RAM for optimal performance
- **Concurrency**: Adjust `ThreadPoolExecutor` workers based on your CPU cores

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run tests (when implemented)
pytest tests/
```

### Adding New Features
1. Model optimization for different languages
2. Batch processing support
3. Real-time streaming transcription
4. GPU acceleration support
5. WebSocket support for live audio

## License

This project is licensed under the MIT License. The NVIDIA NeMo model is subject to NVIDIA's license terms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review the [API documentation](#api-documentation)
3. Open an issue on GitHub