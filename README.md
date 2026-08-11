# 🕉️ Vedic Astro - Authentic Birth Chart Analysis

A global Vedic astrology platform with real planetary calculations using Swiss Ephemeris.

## ✨ Features

- **Real Calculations** - Uses Swiss Ephemeris (NASA-grade precision)
- **Multiple Chart Styles** - North Indian & South Indian Kundli
- **Navamsha (D9)** - Inner self & marriage analysis
- **Vimshottari Dasha** - Complete timeline with current period
- **Yoga Detection** - Automatic identification of astrological combinations
- **Vargottama** - Special planet strength identification
- **Global Coverage** - 100+ cities worldwide
- **Mobile Responsive** - Works on all devices
- **Fast API** - JSON API for integrations

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 run.py
```

Open http://localhost:8080

### Docker
```bash
docker-compose up --build
```

## 📡 API Usage

### Calculate Birth Chart
```bash
POST /api/calculate
Content-Type: application/json

{
    "name": "Your Name",
    "day": 22,
    "month": 1,
    "year": 2005,
    "hour": 3,
    "minute": 50,
    "city": "Delhi"
}
```

### City Autocomplete
```bash
GET /api/cities?q=delhi
```

## 🌍 Deployment

### Deploy to Render/Railway
1. Push to GitHub
2. Connect to Render/Railway
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Deploy to VPS (DigitalOcean, AWS, etc.)
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and run
git clone <your-repo>
cd vedic-astro
docker-compose up -d
```

## 💰 Monetization Ideas

1. **Free Tier** - Basic chart + planet positions
2. **Premium ($9-19)** - Full report with predictions
3. **Pro ($29-49)** + Live consultation
4. **API Access** - For other websites/apps

## 🔧 Tech Stack

- **Backend:** Python + Flask
- **Astrology Engine:** Swiss Ephemeris (pyswisseph)
- **Frontend:** HTML/CSS/JS (vanilla)
- **Deployment:** Docker + Gunicorn
- **Database:** (Add PostgreSQL for user accounts)

## 📝 License

MIT License - Free to use and modify.

---

Made with 🙏 for the global Vedic astrology community
