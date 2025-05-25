# ASR-NeMo-FastAPI

A FastAPI-based Automatic Speech Recognition (ASR) service using NVIDIA NeMo's Hindi Conformer CTC model, optimized with ONNX for efficient inference.

## Features

- **Hindi Speech Recognition**: Uses NVIDIA NeMo's `stt_hi_conformer_ctc_medium` model
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
   docker build -t asr-fastapi .
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

2. **Start the server**
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
  "transcription": "अपना आधा सफर पूरा कर लिया है इस दौरान हमने अनेक विषयों पर बात की स्वाभाविक है कि जो वैश्विक मामारी आ मानव जाति पर संकट आया उस पर हमारी बातचीत कुछ ज्यादा ही रही लेकिन इन दिनों में देख रहा हूं लगातार लोगों में एक विषय परा हो रही है कि आखिर यह साल बीतेगा कोई किसी को फोन भी कर रहा है तो बातचीत इसी विषय से शुरू हो रही है यह साल जल्दी क्यों नहीं बीत रहा कोई लिख रहा है दोस्तों से बात कर रहा है कह रहा है कि साल अच्छा नहीं है कोई कह रहा है दो हजार ब शुभ नहीं है बस लोग यही चाहते हैं कि किसी भी तरह से यह साल जल्द से जल्द बीत जाए साथियों कभी कभीै",
  "filename": "sample.wav",
  "duration": "60.00s",
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
- **Sample Rate**: 16kHz (recommended)
- **Channels**: Mono (recommended)

## API Documentation

Once the service is running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
asr-transcription-service/
├── main.py                 # FastAPI application  # Model conversion script  
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── README.md            # This file
├── Description.md       # Development documentation
└── test_audio/          # Sample audio files (optional)
    └── sample.wav
```

## Design Considerations

### Performance Optimization
- **Async Processing**: Non-blocking audio processing using thread pools
- **Resource Management**: Automatic cleanup of temporary files

### Scalability
- **Containerized**: Easy deployment and scaling with Docker
- **Health Checks**: Built-in health monitoring endpoints
- **Error Handling**: Comprehensive error handling and logging

### Security & Validation
- **File Type Validation**: Only accepts .wav files
- **Input Sanitization**: Validates audio properties before processing

## Environment Variables

- `PYTHONUNBUFFERED`: Set to 1 for real-time logging

## Troubleshooting

### Common Issues

1. **Audio format errors**
   - Convert audio to .wav format using ffmpeg: `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`

2. **Container fails to start**
   - Check Docker logs: `docker logs <container-id>`
   - Ensure sufficient memory (recommend 4GB+)

### Performance Tips

- **CPU Usage**: The service uses CPU by default. For GPU acceleration, modify the ONNX Runtime providers in `main.py`
- **Memory**: Allocate at least 4GB RAM for optimal performance
- **Concurrency**: Adjust `ThreadPoolExecutor` workers based on your CPU cores

## Development

### Adding New Features
1. Batch processing support
2. Real-time streaming transcription
3. GPU acceleration support

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