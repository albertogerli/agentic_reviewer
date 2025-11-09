# 🎨 Gamma Presentations - Quick Start Guide

Genera presentazioni professionali automaticamente dai tuoi review con **un solo click**!

## 🚀 Setup Veloce (2 minuti)

### 1. Ottieni API Key Gamma

```bash
# Vai su:
https://gamma.app/settings/api

# Crea account (gratuito)
# Genera API key (inizia con "sk-gamma-")
```

### 2. Configura nel `config.yaml`

```yaml
# config.yaml
gamma_api_key: "sk-gamma-xxxxxxxx"  # ← Incolla qui la tua key
```

**Fatto!** ✅

## 💻 Uso da React UI (localhost:3000)

### Workflow Completo

1. **Carica Documento**
   - Drag & drop il tuo PDF/DOCX
   - Configura opzioni (Deep Analysis, Web Research, etc.)

2. **Avvia Analisi**
   - Click su "Analyze My Document"
   - Attendi completamento (vedi progress live)

3. **Genera Presentazione** 🎨
   - Vai nella sezione "Download Cards"
   - Click sul bottone arancione **"🎨 Presentation"**
   - Attendi 30-60 secondi

4. **Risultato**
   - 🌐 **Gamma URL** si apre automaticamente → Visualizza/Edita online
   - 📥 **PDF** si scarica automaticamente → Salva localmente
   - ✅ **Alert** conferma successo con entrambi i link

### Schermata

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  📄 MD      │  📊 JSON    │  📈 HTML    │  🎨 Pres    │
│  Report     │  Results    │  Dashboard  │  [CLICK!]   │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

## 📊 Cosa Ottieni

La presentazione PDF contiene **10-12 slide**:

1. **Title** - Nome documento + summary
2. **Executive Summary** - Metriche chiave, issue counts
3. **Risk Heatmap** - Grafico rischi per categoria
4. **Critical Issues** - Problemi critici dettagliati (2 slide)
5. **High Priority Issues** - Miglioramenti importanti (2 slide)
6. **Proposed Changes** - Modifiche suggerite
7. **Key Strengths** - Punti di forza del documento
8. **Agent Analysis** - Overview degli AI agents usati
9. **Recommendations** - Azioni prioritarie
10. **Next Steps** - Roadmap implementazione

### Esempio Output

**View Online** (Gamma URL):
```
https://gamma.app/docs/abc123def456
```
- ✏️ Edita le slide
- 🎨 Cambia tema/layout
- 🤝 Condividi con team
- 📱 Presenta da qualsiasi device

**Download PDF**:
```
presentation.pdf (in outputs/your_doc_timestamp/)
```
- 📧 Allega via email
- 📊 Usa in meeting
- 🖨️ Stampa per distribuzione
- 💾 Archivia per record

## ⚙️ Opzioni Avanzate

### Cambia Tema

Modifica in `ReviewResults.tsx`:

```tsx
const response = await fetch(`...create-presentation`, {
  method: 'POST',
  body: JSON.stringify({
    export_format: 'pdf',
    theme_id: 'Prism'  // Cambia tema qui!
  })
});
```

**Temi Disponibili**:
- `Oasis` - Pulito, professionale (default)
- `Prism` - Colorato, gradients vibranti
- `Chisel` - Minimale, moderno
- `Standard Dark` - Dark mode elegante

### Esporta PPTX invece di PDF

```tsx
export_format: 'pptx'  // Editabile in PowerPoint
```

## 🔍 Troubleshooting

### ⚠️ "Gamma API key not configured"

**Soluzione**:
```yaml
# config.yaml
gamma_api_key: "sk-gamma-xxxxxxxx"
```

Riavvia backend:
```bash
cd /Users/.../Sassari
python backend/app.py
```

### ⏳ Generazione Lenta (> 2 min)

**Cause possibili**:
- Documento molto complesso
- Primo uso (cold start Gamma API)
- Rate limit raggiunto

**Soluzione**: Attendi. Il sistema mostra spinner animato.

### ❌ "Failed to create presentation"

**Verifica**:
1. ✅ Backend attivo (`http://localhost:8000`)
2. ✅ Review completata con successo
3. ✅ API key valida (`test_gamma_config.py`)
4. ✅ Credits Gamma disponibili

**Debug**:
```bash
# Check backend logs
tail -f backend.log

# Test API key
python test_gamma_config.py
```

### 🌐 PDF Non Scarica Automaticamente

**Browser blocca popup?**
- Clicca sul link nella alert
- O copia/incolla Gamma URL
- Scarica manualmente da Gamma

## 📝 Best Practices

### Quando Usare

✅ **SI - Usa Gamma per**:
- Meeting stakeholder
- Board presentations
- Executive summaries
- Client proposals
- Team reviews

❌ **NO - Non necessario per**:
- Review interna dettagliata (usa MD/JSON)
- Debug tecnico (usa raw data)
- Archiviazione storica (usa JSON)

### Workflow Consigliato

```
1. Review Standard       → Analizza documento
2. Explore Issues        → Three-Panel Layout
3. Accept/Reject Changes → Redline Editor
4. Generate PDF          → 🎨 Presentation (per stakeholder)
5. Apply Changes         → Revised Document
```

## 💰 Costi

**Gamma API**:
- ✅ Free tier: 20 credits/mese
- 📊 1 presentazione = ~2-3 credits
- 🎯 **~6-10 presentazioni gratis/mese**

**Upgrade**:
- Pro: $20/mese (200 credits)
- Ultra: Unlimited

Vedi: https://gamma.app/pricing

## 🎓 Tips & Tricks

### 1. Riutilizza Tema

Se trovi un tema che ti piace, salvalo come default:

```tsx
// frontend/src/components/ReviewResults.tsx
theme_id: 'YOUR_FAVORITE_THEME'  // Line 84
```

### 2. Batch Generation

Per generare presentazioni per review multiple:

```bash
# Script bash
for review_id in review_*; do
  curl -X POST "http://localhost:8000/api/review/$review_id/create-presentation" \
    -H "Content-Type: application/json" \
    -d '{"export_format":"pdf"}'
  sleep 60  # Evita rate limit
done
```

### 3. Custom Branding

Edita su Gamma.app:
- Aggiungi logo aziendale
- Modifica colori brand
- Personalizza footer
- Salva come template

### 4. Integra in CI/CD

```yaml
# .github/workflows/review.yml
- name: Generate Presentation
  run: |
    python -c "
    from gamma_integration import create_presentation_from_review
    import json
    results = json.load(open('review_results.json'))
    create_presentation_from_review(results, '${{ secrets.GAMMA_API_KEY }}', './output')
    "
```

## 📚 Resources

- 📖 [Gamma API Docs](https://gamma.app/docs/api)
- 🎨 [Gamma Templates](https://gamma.app/templates)
- 🔑 [Get API Key](https://gamma.app/settings/api)
- 💬 [Community](https://gamma.app/community)
- 📧 [Support](mailto:support@gamma.app)

## ✨ Next Steps

- [ ] Prova con il tuo primo documento!
- [ ] Esplora diversi temi
- [ ] Condividi con il team
- [ ] Personalizza su gamma.app
- [ ] Integra nel workflow

---

**Made with ❤️ for effortless presentation generation** 🚀

*Ultimo aggiornamento: Nov 2025*

