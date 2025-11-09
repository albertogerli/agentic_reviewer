# 🎨 Gamma API Integration

Automatically generate professional slide presentations from document review results using Gamma AI.

## 📊 Features

- **Auto-Generated Slides**: 10-12 slides created from review results
- **Professional Themes**: Multiple theme options (Oasis, Prism, Chisel, etc.)
- **AI-Generated Images**: Powered by Imagen-4-Pro
- **Export Options**: PDF or PPTX format
- **Smart Formatting**: Structured content with risk heatmaps, issue breakdowns, recommendations

## 🎬 Generated Presentation Structure

1. **Title Slide**: Document name + review summary
2. **Executive Summary**: Key metrics, issue counts, overall assessment
3. **Risk Heatmap**: Visual breakdown of risks by category
4. **Critical Issues** (2 slides): Detailed breakdown of critical problems
5. **High Priority Issues** (2 slides): Important improvements needed
6. **Proposed Changes**: Summary of suggested modifications
7. **Key Strengths**: Positive aspects of the document
8. **Agent Analysis**: Overview of AI agents used
9. **Recommendations**: Priority actions
10. **Next Steps**: Implementation roadmap

## 🚀 Setup

### 1. Get Gamma API Key

1. Go to https://gamma.app
2. Sign up / Log in
3. Navigate to Settings → API
4. Generate an API key (starts with `sk-gamma-...`)

### 2. Configure API Key

**Option A: Environment Variable** (Recommended)
```bash
export GAMMA_API_KEY="sk-gamma-xxxxxxxx"
```

**Option B: config.yaml**
```yaml
gamma_api_key: "sk-gamma-xxxxxxxx"
```

### 3. Install Dependencies

```bash
pip install -r requirements_gamma.txt
```

## 💻 Usage

### Via Backend API

**After a review is complete**, call the presentation endpoint:

```bash
# Create PDF presentation
curl -X POST "http://localhost:8000/api/review/{review_id}/create-presentation" \
  -H "Content-Type: application/json" \
  -d '{"export_format": "pdf"}'

# Create PPTX presentation
curl -X POST "http://localhost:8000/api/review/{review_id}/create-presentation" \
  -H "Content-Type: application/json" \
  -d '{"export_format": "pptx"}'

# Use custom theme
curl -X POST "http://localhost:8000/api/review/{review_id}/create-presentation" \
  -H "Content-Type: application/json" \
  -d '{"theme_id": "Prism", "export_format": "pdf"}'
```

**Response**:
```json
{
  "success": true,
  "generation_id": "abc123def456",
  "gamma_url": "https://gamma.app/docs/...",
  "export_url": "https://cdn.gamma.app/...",
  "local_file": "/path/to/presentation.pdf",
  "message": "Presentation created successfully!"
}
```

### Via Python

```python
from gamma_integration import create_presentation_from_review
import json

# Load review results
with open('outputs/my_review/review_results.json') as f:
    results = json.load(f)

# Create presentation
presentation_info = create_presentation_from_review(
    review_results=results,
    gamma_api_key="sk-gamma-xxxxxxxx",
    output_dir="./outputs/my_review",
    theme_id="Oasis",  # Optional
    export_format="pdf"  # or "pptx"
)

print(f"View at: {presentation_info['gamma_url']}")
print(f"Download: {presentation_info['local_path']}")
```

## 🎨 Available Themes

Get list of available themes:

```bash
curl -X GET "https://public-api.gamma.app/v1.0/themes" \
  -H "X-API-KEY: sk-gamma-xxxxxxxx"
```

**Popular Themes**:
- `Oasis` - Clean, professional (default)
- `Prism` - Colorful, gradient, vibrant
- `Chisel` - Minimal, modern
- `Standard Dark` - Dark mode
- Many more available in your workspace

## 📝 Customization

### Modify Slide Count

Edit `gamma_integration.py`:

```python
config = GammaConfig(
    api_key=gamma_api_key,
    num_cards=15,  # Change to 15 slides
    # ...
)
```

### Custom Instructions

```python
generator = GammaPresentationGenerator(api_key)

result = generator.create_presentation(
    review_results,
    config,
    additional_instructions="Make the titles catchy and use bullet points"
)
```

### Image Style

Modify in `gamma_integration.py`:

```python
"imageOptions": {
    "source": "aiGenerated",
    "model": "imagen-4-pro",
    "style": "minimal, black and white, line art"  # Customize here
}
```

**Style Options**:
- `"photorealistic, high quality"`
- `"minimal, modern, clean"`
- `"illustration, colorful, flat design"`
- `"corporate, professional, business"`
- `"hand-drawn, sketchy, artistic"`

## 🔍 Frontend Integration (TODO)

Add a button to `frontend/src/components/ReviewResults.tsx`:

```tsx
const [generating, setGenerating] = useState(false);

const handleCreatePresentation = async () => {
  setGenerating(true);
  try {
    const response = await fetch(
      `/api/review/${reviewId}/create-presentation`,
      {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({export_format: 'pdf'})
      }
    );
    
    const data = await response.json();
    
    // Open Gamma URL
    window.open(data.gamma_url, '_blank');
    
    // Download file
    if (data.export_url) {
      window.open(data.export_url, '_blank');
    }
  } catch (error) {
    console.error('Failed to create presentation:', error);
  } finally {
    setGenerating(false);
  }
};

// In JSX
<button onClick={handleCreatePresentation} disabled={generating}>
  {generating ? '⏳ Generating...' : '🎨 Create Presentation'}
</button>
```

## 💰 Pricing

Gamma API uses credits:
- **1 Generation** ≈ 1-3 credits (depends on complexity)
- Check your credit balance at https://gamma.app/settings/api

**Tip**: Use `textMode: "preserve"` to reduce AI processing and save credits.

## 🐛 Troubleshooting

### "No API key configured"
- Set `GAMMA_API_KEY` environment variable
- Or add `gamma_api_key` to `config.yaml`

### "Generation failed"
- Check Gamma API credits balance
- Verify API key is valid (starts with `sk-gamma-`)
- Check rate limits (max 100 requests/minute)

### "Review results not found"
- Ensure the review has completed successfully
- Check that `review_results.json` exists in output directory

### Images not generating
- Verify `imageOptions.model` is valid (e.g., `imagen-4-pro`, `flux-1-pro`)
- Check that `imageOptions.style` is descriptive enough
- Try different image styles if results aren't satisfactory

## 📚 Resources

- [Gamma API Docs](https://gamma.app/docs/api)
- [Get Gamma API Key](https://gamma.app/settings/api)
- [Available Themes](https://gamma.app/docs/api/themes)
- [Image Models](https://gamma.app/docs/api/models)

## 🎯 Roadmap

- [ ] Add button to React UI for one-click generation
- [ ] Support custom templates
- [ ] Batch presentation generation for multiple reviews
- [ ] Theme selection UI
- [ ] Preview before finalizing
- [ ] Automatic sharing with stakeholders

---

**Made with ❤️ for professional document review presentations**

