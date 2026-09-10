
# HarvestIQ

> AI-assisted crop intelligence for healthier fields and faster agricultural decisions.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Open%20HarvestIQ-16a34a?style=for-the-badge)](https://musical-gelato-47960b.netlify.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Hugging Face](https://img.shields.io/badge/Model-Hugging%20Face-FFD21E?style=flat-square)](https://huggingface.co/)

HarvestIQ is a crop-support platform that combines agricultural recommendations with AI-powered plant-leaf analysis. The linked live deployment provides a soil-input crop recommendation experience, while this repository contains the Flask backend and web interface for image-based crop disease diagnostics and multilingual agronomic guidance.

## Live Demo

**[Open the deployed HarvestIQ application](https://musical-gelato-47960b.netlify.app/)**

The live interface accepts:

- Soil nutrients: Nitrogen (N), Phosphorus (P), and Potassium (K)
- Temperature, humidity, soil pH, and rainfall
- A crop recommendation generated from the supplied conditions

## What This Repository Provides

### Image diagnosis

Upload a clear plant-leaf photograph and the Flask application will:

1. Classify the image with a Vision Transformer image-classification pipeline.
2. Identify a supported crop and likely disease or healthy status.
3. Return the prediction confidence and a coarse attention overlay.
4. Generate a practical treatment and prevention advisory with an LLM.

The current supported crops are **Corn, Potato, Rice, and Wheat**. Predictions below 50% confidence, background images, and unsupported specimens are rejected as non-supported samples.

### HarvestBot assistant

The built-in chat endpoint provides follow-up agricultural guidance. Responses can use the browser's weather context and can be requested in English, Hindi, or Bengali.

### Model training

`Hugging Face Training Script.py` fine-tunes `google/vit-base-patch16-224-in21k` with an ImageFolder dataset and saves a custom classifier that can be loaded by the Flask app.

## Technology Stack

| Area | Technology |
| --- | --- |
| Web server | Flask |
| Image classification | Hugging Face Transformers and Vision Transformer |
| Image processing | Pillow, NumPy, OpenCV |
| AI advisory | Google Gemini through LangChain, with optional Groq support |
| Frontend | HTML, Tailwind CSS, vanilla JavaScript |
| Weather context | Open-Meteo API from the browser |
| Deployment | Docker-compatible Flask container |

## Project Structure

```text
.
├── app.py                         # Flask routes, model inference, advisory, and chat
├── templates/
│   └── index.html                 # HarvestIQ diagnostic workspace
├── Hugging Face Training Script.py # Optional ViT fine-tuning workflow
├── requirements.txt               # Runtime Python dependencies
├── Dockerfile                     # Container image configuration
└── README.md
```

## Run Locally

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

The first run may download the configured Hugging Face model, so startup and inference can take longer on a fresh environment.

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-random-secret
GOOGLE_API_KEY=your-google-api-key
LLM_PROVIDER=google
GOOGLE_MODEL=gemini-1.5-flash
VISION_MODEL_ID=wambugu71/crop_leaf_diseases_vit
```

To use Groq instead of Google Gemini:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

Keep `.env` and API keys out of version control.

### 4. Start the application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

## Docker

Build and run the container with:

```bash
docker build -t harvestiq .
docker run --rm -p 7860:7860 --env-file .env harvestiq
```

The container listens on the `PORT` environment variable and defaults to `7860`.

## API Reference

### `GET /`

Returns the HarvestIQ diagnostic interface.

### `POST /analyze`

Accepts a multipart form request:

| Field | Required | Description |
| --- | --- | --- |
| `file` | Yes | Plant-leaf image |
| `language` | No | Advisory language; defaults to `English` |
| `weather` | No | Weather context; defaults to `Unknown` |

Returns the crop, disease or healthy status, confidence score, treatment advisory, supported crops, and optional attention overlay.

### `POST /chat`

Accepts JSON:

```json
{
	"message": "How can I reduce fungal disease risk after heavy rain?",
	"language": "English",
	"weather": "24C, 78% Humidity"
}
```

The response contains a `response` field. Conversation history is stored in the Flask session.

## Train a Custom Vision Model

The training script expects an ImageFolder-style dataset:

```text
dataset/
├── train/
│   ├── class-one/
│   └── class-two/
└── validation/
		├── class-one/
		└── class-two/
```

Install the training-only packages before running the script:

```bash
pip install datasets evaluate
python "Hugging Face Training Script.py"
```

The resulting model is saved to `custom_vit_crop_model`. To use it in the application, set:

```env
VISION_MODEL_ID=./custom_vit_crop_model
```

## Responsible Use

HarvestIQ provides AI-assisted guidance, not a definitive laboratory diagnosis or a substitute for a qualified agronomist. Use clear images, treat confidence scores as estimates, verify recommendations locally, and follow product labels and local agricultural regulations before applying treatments.

## License

No license file is currently included. Add a license before distributing or deploying the project for third-party use.
