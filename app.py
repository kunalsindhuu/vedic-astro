from flask import Flask, render_template, request, jsonify, abort, send_file, Response, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import sys
import os
import re
import io
import csv
from datetime import datetime
import json
import time
import smtplib
import hashlib
import hmac
import urllib.parse
import urllib.request
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

_LOCAL_SITE_PACKAGES = '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages'
if os.path.exists(_LOCAL_SITE_PACKAGES):
    sys.path.insert(0, _LOCAL_SITE_PACKAGES)
import swisseph as swe

app = Flask(__name__, static_folder='static', template_folder='templates')

# === LEAD STORAGE ===
LEADS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leads.json')
LEAD_PASSWORD = os.environ.get('LEAD_PASSWORD', 'vedicadmin123')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'supportvedicastro77@gmail.com')

# Gmail SMTP settings (for lead notifications)
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = os.environ.get('SMTP_USER', CONTACT_EMAIL)
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

# === RAZORPAY SETTINGS ===
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
RAZORPAY_API = 'https://api.razorpay.com/v1'

FEEDBACK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback.json')

def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_feedback(item):
    items = load_feedback()
    items.append(item)
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    return len(items)

PRICING = {
    'premium': {'inr': 999, 'usd': 9.99, 'name': 'Premium Kundli', 'inoise': '₹999 or $9.99'},
    'consultation': {'inr': 4999, 'usd': 49.99, 'name': 'Consultation', 'inoise': '₹4999 or $49.99'},
}

PAYMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'payments.json')

def load_payments():
    if not os.path.exists(PAYMENTS_FILE):
        return []
    try:
        with open(PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_payment(payment):
    payments = load_payments()
    payments.append(payment)
    with open(PAYMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(payments, f, indent=2, ensure_ascii=False)
    return len(payments)

def rz_request(method, path, data=None):
    """Low-level Razorpay API helper"""
    url = RAZORPAY_API + path
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    import base64
    auth = base64.b64encode(f'{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}'.encode()).decode()
    req.add_header('Authorization', 'Basic ' + auth)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_lead(lead):
    leads = load_leads()
    leads.append(lead)
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    return len(leads)

def send_lead_email(lead):
    """Email new lead details to the site owner (best-effort)."""
    if not SMTP_PASSWORD:
        app.logger.warning('send_lead_email: SMTP_PASSWORD not set')
        return False
    try:
        b = lead.get('birth', {})
        body = f"""New Kundli Lead!

Name: {lead.get('name', '-')}
Email: {lead.get('email', '-')}
Birth: {b.get('day', '-')}/{b.get('month', '-')}/{b.get('year', '-')} {b.get('hour', '-')}:{b.get('minute', '-')}
City: {b.get('city', '-')}
Ascendant: {lead.get('ascendant', '-')}
Sun Sign: {lead.get('sun_sign', '-')}
Moon Sign: {lead.get('moon_sign', '-')}
Dasha: {lead.get('dasha', '-')}

View all leads at your admin dashboard: /admin
"""
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = CONTACT_EMAIL
        msg['Subject'] = f"New Lead: {lead.get('name', '-')} ({lead.get('email', '-')})"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, CONTACT_EMAIL, msg.as_string())
        server.quit()
        app.logger.info('send_lead_email: sent to %s', CONTACT_EMAIL)
        return True
    except Exception as e:
        app.logger.error('send_lead_email: FAILED %s: %s', type(e).__name__, e)
        return False

# === SECURITY SETTINGS ===
# Rate limiting - prevent abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Security headers - protect visitors
Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
        'font-src': ["'self'", "fonts.gstatic.com"],
        'img-src': "'self'",
    },
    force_https=False  # Set True in production with custom domain
)

# Secret key for sessions (if needed later)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # Max 16KB request size

# === SECURITY HELPERS ===
def sanitize_string(text, max_length=100):
    """Remove dangerous characters and limit length"""
    if not isinstance(text, str):
        return ''
    # Remove HTML tags and special characters
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[<>\"\'%;()&+]', '', text)
    # Limit length
    return text[:max_length].strip()

# === CONSTANTS ===
SIGN_NAMES = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
              'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
SIGN_SHORT = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
SIGN_SYMBOLS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
SIGN_LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']
SIGN_ELEMENTS = ['Fire', 'Earth', 'Air', 'Water', 'Fire', 'Earth', 'Air', 'Water', 'Fire', 'Earth', 'Air', 'Water']

PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN
}

PLANET_SYMBOLS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋'
}

DHASE_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10,
    'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
DHASE_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushy', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]
NAKSHATRA_LORDS = DHASE_ORDER * 3

# City database
CITY_DB = {
    'rohtak': (28.90, 76.57), 'delhi': (28.61, 77.21), 'new delhi': (28.61, 77.21),
    'mumbai': (19.07, 72.87), 'bangalore': (12.97, 77.59), 'chennai': (13.08, 80.27),
    'kolkata': (22.57, 88.36), 'hyderabad': (17.38, 78.48), 'pune': (18.52, 73.85),
    'ahmedabad': (23.02, 72.57), 'jaipur': (26.91, 75.79), 'lucknow': (26.85, 80.95),
    'kanpur': (26.45, 80.33), 'nagpur': (21.14, 79.08), 'indore': (22.71, 75.85),
    'thane': (19.22, 72.98), 'bhopal': (23.25, 77.41), 'visakhapatnam': (17.68, 83.21),
    'patna': (25.61, 85.14), 'vadodara': (22.30, 73.19), 'ghaziabad': (28.67, 77.45),
    'ludhiana': (30.90, 75.85), 'agra': (27.18, 78.02), 'nashik': (20.00, 73.78),
    'ranchi': (23.34, 85.31), 'guwahati': (26.14, 91.73), 'chandigarh': (30.73, 76.78),
    'coimbatore': (11.01, 76.96), 'kochi': (9.93, 76.26), 'dehradun': (30.32, 78.03),
    'varanasi': (25.31, 82.97), 'amritsar': (31.63, 74.87), 'allahabad': (25.44, 81.84),
    'london': (51.51, -0.13), 'new york': (40.71, -74.01), 'dubai': (25.20, 55.27),
    'singapore': (1.35, 103.82), 'sydney': (-33.87, 151.21), 'toronto': (43.65, -79.38),
    'kathmandu': (27.72, 85.32), 'colombo': (6.93, 79.86), 'kuala lumpur': (3.14, 101.69),
    'hong kong': (22.32, 114.17), 'tokyo': (35.68, 139.69), 'paris': (48.86, 2.35),
    'berlin': (52.52, 13.41), 'moscow': (55.76, 37.62), 'los angeles': (34.05, -118.24),
    'chicago': (41.88, -87.63), 'san francisco': (37.77, -122.42), 'seattle': (47.61, -122.33),
    'miami': (25.76, -80.19), 'houston': (29.76, -95.37), 'denver': (39.74, -104.99),
    'phoenix': (33.45, -112.07), 'philadelphia': (39.95, -75.17), 'atlanta': (33.75, -84.39),
    'boston': (42.36, -71.06), 'melbourne': (-37.81, 144.96), 'auckland': (-36.85, 174.76),
    'vancouver': (49.28, -123.12), 'calgary': (51.05, -114.07), 'montreal': (45.50, -73.57),
    'ottawa': (45.42, -75.70), 'dhaka': (23.81, 90.41), 'karachi': (24.86, 67.01),
    'lahore': (31.55, 74.36), 'islamabad': (33.68, 73.05), 'riyadh': (24.71, 46.67),
    'doha': (25.29, 51.53), 'kuwait': (29.38, 47.98), 'muscat': (23.59, 58.55),
    'bangkok': (13.76, 100.50), 'jakarta': (-6.21, 106.85), 'manila': (14.60, 120.98),
    'seoul': (37.57, 126.98), 'taipei': (25.03, 121.56), 'shanghai': (31.23, 121.47),
    'beijing': (39.90, 116.41), 'mexico city': (19.43, -99.13), 'sao paulo': (-23.55, -46.63),
    'buenos aires': (-34.60, -58.38), 'lima': (-12.05, -77.04), 'bogota': (4.71, -74.07),
    'santiago': (-33.45, -70.67)
}

# Blog posts data
BLOG_POSTS = [
    {
        'id': 'understanding-your-moon-sign',
        'title': 'Understanding Your Moon Sign: The Key to Your Emotions',
        'excerpt': 'Your moon sign reveals your emotional nature, subconscious patterns, and what makes you feel secure...',
        'date': '2026-08-10',
        'category': 'Basics',
        'read_time': '5 min',
        'content': [
            'In Vedic astrology, the Moon holds a place of honour that it never receives in Western astrology. While the Sun represents your conscious identity, career, and outer drive, the Moon governs your mind, your emotions, your habits, and the instinctive patterns that shape how you react when no one is watching.',
            'Your Moon sign is the sign the Moon occupied at your moment of birth. Because the Moon travels through all twelve signs in roughly 27 days, its position is deeply personal and changes almost daily — which is why two people born just days apart can have completely different emotional landscapes.',
            'In the Vimshottari Dasha system, the Moon is one of the most important planets of all. The nakshatra (lunar mansion) that the Moon occupies at birth determines the very first dasha period you are born under, and it anchors your entire life timeline. This is why traditional astrologers always begin a reading by examining the Moon.',
            'To find your Moon sign, you need your exact date, time, and place of birth. Unlike the Sun sign, which only needs your date, the Moon moves fast enough that your birth time and location matter greatly. If you have never checked your Moon sign, try our free kundli calculator and be prepared to be surprised — your emotional self may be very different from your zodiac-sign personality.',
            'Once you know your Moon sign, you can begin to understand why certain situations trigger you, what kind of home life you crave, and how you nurture yourself best. The Moon is the mind, and understanding your Moon sign is the first real step toward self-mastery.'
        ]
    },
    {
        'id': 'vimshottari-dasha-explained',
        'title': 'Vimshottari Dasha: How Planetary Periods Shape Your Life',
        'excerpt': 'Learn how the ancient Vimshottari Dasha system can predict major life events and opportunities...',
        'date': '2026-08-08',
        'category': 'Predictive',
        'read_time': '7 min',
        'content': [
            'The Vimshottari Dasha system is the crown jewel of Vedic predictive astrology. It is a timeline of your life divided into planetary periods, and once you understand it, you understand why some years feel effortless while others feel like an uphill battle.',
            'The word Vimshottari means "120" — the system is based on a total cycle of 120 years, divided among the nine planets (Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury, Ketu, Venus). Each planet rules a specific number of years: the Sun rules 6, the Moon 10, Mars 7, Rahu 18, Jupiter 16, Saturn 19, Mercury 17, Ketu 7, and Venus 20.',
            'At the moment of your birth, the Moon is in a specific nakshatra. The remaining portion of that nakshatra determines which planet\'s period begins your life, and from there the cycle unfolds in a fixed order. The planet that was "running" at birth carries great significance — it shapes your early childhood and the atmosphere of your family.',
            'Each major period (Mahadasha) is further divided into sub-periods (Antardashas) of the other planets. This creates a rich, layered timeline. For example, during your Jupiter Mahadasha, Jupiter-related themes like education, wisdom, children, and expansion will dominate — but the exact flavour depends on which Antardasha is running at any given moment.',
            'Vedic astrologers use the dasha timeline to time major events: marriage, career changes, financial gains, health challenges, and spiritual growth. When a beneficial planet runs its period in a favourable house, doors open. When a difficult planet runs its course, the same doors may close — not as punishment, but as a necessary lesson.',
            'The most empowering way to use dasha knowledge is forewarned is forearmed. If you know Saturn is running its period through your 8th house, you can prepare by slowing down, being disciplined with finances, and focusing on long-term health. Knowledge of your dasha does not change the stars; it changes how you dance with them.'
        ]
    },
    {
        'id': 'raj-yogas-in-vedic-astrology',
        'title': 'Raj Yogas: The Royal Combinations for Success',
        'excerpt': 'Discover the powerful Raj Yogas that can bring wealth, power, and recognition in your life...',
        'date': '2026-08-05',
        'category': 'Yogas',
        'read_time': '6 min',
        'content': [
            'In Vedic astrology, a Yoga is a specific combination of planets, houses, or signs that produces a particular result. Among the most celebrated are the Raj Yogas — the "royal combinations" that are said to elevate a person to positions of authority, wealth, and fame.',
            'The most famous Raj Yoga is the combination of the lord of the 9th house (Bhagyesha, lord of fortune) with the lord of the 10th house (Karmesha, lord of career). When these two planetary lords join together — either by conjunction, exchange, or mutual aspect — the person is promised success in career, fame, and divine grace.',
            'Another important combination involves the lord of the 5th house (the house of intelligence and past good karma) joining the lord of the 9th house. This is called Dharma-Karmadhipati Raj Yoga and is considered one of the most auspicious. Such a person often rises through integrity, talent, and righteous action.',
            'There are also planet-specific Raj Yogas. Jupiter (Guru) is the natural karaka of fortune, and Venus (Shukra) is the natural karaka of luxury and the arts. When Jupiter and Venus conjoin, the Gaja-Kesari-like grace is amplified — a person of learning who also enjoys the finer things in life.',
            'However, a Raj Yoga is only as powerful as its planets. If the yogakaraka planet is weak, debilitated, or combust, the yoga fructifies later in life or in a muted way. Timing matters enormously — a Raj Yoga in your chart is activated only when the relevant planet runs its dasha or is activated by a favourable transit.',
            'The practical lesson: even the most royal chart requires effort, character, and timing. Astrology does not hand you a throne; it tells you which staircase to climb and when the royal elevator will arrive. Our kundli calculator automatically detects major yogas in your chart — check yours today.'
        ]
    },
    {
        'id': 'saturn-transit-2026',
        'title': 'Saturn Transit 2026: What It Means for Each Sign',
        'excerpt': 'Saturn\'s transit through Pisces brings significant changes. Learn how it affects your sign...',
        'date': '2026-08-02',
        'category': 'Transits',
        'read_time': '8 min',
        'content': [
            'Saturn — Shani — is the great teacher of the zodiac. Slow, serious, and relentless, Saturn does not bring shortcuts. It brings discipline, structure, and the hard-won rewards that come from consistent effort. When Saturn changes signs, its lessons move into a new area of your life, and 2026 is one of those significant years.',
            'Saturn\'s transit is a long-term event. It spends roughly 2.5 years in each sign, which means its influence is felt in seasons rather than moments. Saturn also goes retrograde for about 4-5 months each year, reviewing the lessons it has been teaching.',
            'Saturn represents responsibility, career, delays, boundaries, and karma. In a favourable position, it grants stability, authority, and longevity — think of politicians, scientists, and long-lived institutions. In a challenging position, it brings obstacles, depression, and delays, forcing you to rebuild on firmer ground.',
            'For each Moon sign, Saturn\'s transit has a specific meaning. When it passes through your 1st house, it tests your identity and confidence — a time to be humble and work on yourself. Through your 4th house, it brings home and family responsibilities. Through your 10th house, it is the classic Sade Sati-adjacent period for career — demanding but capable of huge professional growth.',
            'The most feared period is the Sade Sati — the seven-and-a-half years when Saturn transits the 12th, 1st, and 2nd houses from your natal Moon. It is not a curse. It is a period of karmic clearing that, handled with patience, humility, and hard work, produces enormous spiritual and material growth.',
            'Whether Saturn\'s transit feels like a weight or a foundation depends largely on you. Respect deadlines, honour elders, stay patient with slow progress, and Saturn rewards you with the most durable success in the zodiac. Check our daily horoscope and transit section for sign-specific updates throughout 2026.'
        ]
    },
    {
        'id': 'navamsha-chart-importance',
        'title': 'Why Your Navamsha Chart Matters More Than You Think',
        'excerpt': 'The Navamsha (D9) chart reveals your true destiny, marriage potential, and spiritual path...',
        'date': '2026-07-28',
        'category': 'Charts',
        'read_time': '6 min',
        'content': [
            'The Navamsha (D9) chart is often called the "fruit of the tree" in Vedic astrology. Your birth chart (D1) is the tree — it shows the circumstances of your life. The Navamsha shows the fruit — the actual results, the inner life, and the strength of your destiny.',
            'The Navamsha is created by dividing each sign into nine equal parts of 3 degrees and 20 minutes each. Each of these parts is then mapped into a new chart. The result is a deeply personal chart that reveals the quality of your relationships, the true strength of your planets, and your spiritual evolution.',
            'In matters of marriage, the Navamsha is indispensable. It is considered the chart of the spouse and of marriage itself. The 7th house of the Navamsha, the position of Venus (for men) or Jupiter (for women), and the 7th lord all describe the nature of your partner and your married life. Matching charts for marriage — the famous Ashtakoota matching — is incomplete without considering the Navamsha.',
            'The Navamsha also reveals the hidden strength of your planets. A planet that appears weak in the birth chart but is strong in the Navamsha often delivers results against the odds. Conversely, a planet that looks strong in the birth chart but is debilitated in the Navamsha frequently disappoints.',
            'When a planet occupies the same sign in both the birth chart and the Navamsha, it is called Vargottama. This is a mark of great strength and purity — the planet\'s energy is focused and unimpeded. Our kundli calculator automatically flags Vargottama planets in your chart, a feature many paid tools lack.',
            'Astrologers of every tradition agree: a reading that ignores the Navamsha is only half a reading. If you want to understand not just what happens to you, but who you are becoming, look to the Navamsha. Your birth chart shows the script; the Navamsha shows the soul.'
        ]
    },
    {
        'id': 'marriage-compatibility-factors',
        'title': 'Marriage Compatibility: Beyond Just Sun Sign Matching',
        'excerpt': 'Real Vedic compatibility analysis considers 8+ factors. Learn what actually matters...',
        'date': '2026-07-25',
        'category': 'Relationships',
        'read_time': '7 min',
        'content': [
            'If you have ever had your kundli "matched" before marriage, you know the process involves a score — the famous 36 gunas. But the Ashtakoota matching system, as it is properly called, is only the first layer of a proper compatibility analysis, and it is widely misunderstood.',
            'The Ashtakoota system compares the Moon positions (and other factors) of the bride and groom across eight categories, awarding points that total to 36. A score of 18 or more is traditionally considered acceptable for marriage. But a good score alone does not guarantee a happy marriage, and a low score is not necessarily a sentence of doom.',
            'Why? Because marriage in Vedic astrology is a much larger story. The 7th house of each chart, the 7th lord, Venus and Jupiter as natural karakas of marriage, the Navamsha chart, and the dasha periods all must be weighed together. Two charts with perfect gunas scores but conflicting 7th houses may still struggle.',
            'The Mangalik (Mangal Dosha) consideration is another layer. Mars in certain houses (1st, 2nd, 4th, 7th, 8th, 12th from lagna, Moon, or Venus) creates Mangal Dosha. A common rule says two Mangliks or two non-Mangliks match well, while mixing them creates friction. But modern astrologers examine the strength of Mars and the overall chart before making any judgment.',
            'Beyond doshas and gunas, what truly matters is practical alignment: similar life goals, financial habits, family values, and communication styles. Astrology can reveal whether two people\'s planetary rhythms will support each other or pull apart, but a marriage is built by two people, not by two charts.',
            'Our compatibility calculator gives you a thoughtful, chart-based view of how two signs interact — by element, ruling planet, and natural affinity. Use it as one thoughtful input to your decision, and remember: the best match is the one where both people choose each other, every day.'
        ]
    },
    {
        'id': 'lagna-the-ascendant-explained',
        'title': 'Your Lagna (Ascendant): The Face You Show the World',
        'excerpt': 'The rising sign shapes your personality, body, and how others perceive you. Learn what it means...',
        'date': '2026-07-20',
        'category': 'Basics',
        'read_time': '5 min',
        'content': [
            'In Vedic astrology, the Lagna — or Ascendant — is the sign rising on the eastern horizon at your exact moment of birth. It is, quite literally, your first impression on the world, and it is the foundation of the entire birth chart.',
            'The Lagna changes approximately every two hours, which is why your birth time is so precious. Two people born the same day but four hours apart can have completely different Ascendants — and therefore completely different life structures, even with the same planets.',
            'Each Lagna gives a distinct flavour. Aries Lagna: bold, direct, pioneering. Taurus Lagna: steady, sensual, patient. Gemini Lagna: curious, quick, communicative. Cancer Lagna: protective, emotional, intuitive. Leo Lagna: proud, warm, magnetic. And so on through all twelve signs.',
            'The Lagna determines which house each planet rules in your chart, and house rulership changes everything. For example, if you are an Aries Lagna, Mars rules your 1st and 8th houses. If you are a Libra Lagna, Mars rules your 4th and 9th houses. Same planet, completely different life areas.',
            'Your Lagna also sets the tone for your physical body and vitality. Vedic texts describe each Lagna\'s characteristic build, complexion, and temperament. The Lagna lord — the planet ruling your Ascendant sign — is among the most important planets in your chart, second only to the Moon.',
            'Find your Lagna with our free kundli calculator. Enter your birth time accurately — even ten minutes can change the Ascendant — and discover the face you show the world, the body you inhabit, and the life-house you are building.'
        ]
    },
    {
        'id': 'gemstones-for-planets',
        'title': 'Gemstones for the Nine Planets: Which Stone Is Right for You?',
        'excerpt': 'Rubies for the Sun, pearls for the Moon, sapphires for Saturn... a practical guide to Vedic gemstones...',
        'date': '2026-07-15',
        'category': 'Remedies',
        'read_time': '6 min',
        'content': [
            'Gemstone therapy is one of the most popular remedies in Vedic astrology. The idea is simple: each planet resonates with a specific gemstone, and wearing the right stone strengthens the planet in your chart, bringing out its beneficial qualities.',
            'The Sun (Surya) resonates with the ruby (Manikya). A strong Sun brings confidence, leadership, and vitality — the ruby is worn to strengthen self-esteem and authority. The Moon resonates with the natural pearl (Moti), which calms the mind, supports emotional balance, and strengthens intuition.',
            'Mars (Mangal) corresponds to the red coral (Moonga), a stone of courage, energy, and protection. Mercury (Budh) resonates with the emerald (Panna), enhancing intellect, communication, and business acumen. Jupiter (Guru) is linked to yellow sapphire (Pukhraj), the great blessing stone for wisdom, fortune, and education.',
            'Venus (Shukra) resonates with the diamond (Heera), which brings beauty, luxury, and harmony to relationships. Saturn (Shani) is associated with blue sapphire (Neelam) — a powerful and demanding stone that grants discipline, patience, and karmic reward. Rahu connects with hessonite (Gomed), and Ketu with cat\'s eye (Lehsunia).',
            'The critical warning: do not wear a gemstone without professional guidance. A stone worn for the wrong planet, or when that planet is already strong or malefic in your chart, can produce the opposite effect. Blue sapphire, in particular, is notoriously unpredictable and can shake a life it does not support.',
            'A qualified astrologer will examine your dasha (which planet is currently running), the planet\'s strength and placement, and the correct metal (gold, silver, or panchdhatu), the correct finger, and the best day to wear the stone. Gemstones are powerful tools — treat them with the respect they deserve.'
        ]
    },
    {
        'id': 'sade-sati-guide',
        'title': 'Sade Sati: Saturn\'s Seven-and-a-Half Years, Demystified',
        'excerpt': 'The most feared period in Indian astrology is actually a powerful opportunity. Here\'s how to thrive...',
        'date': '2026-07-10',
        'category': 'Transits',
        'read_time': '8 min',
        'content': [
            'Sade Sati — "the seven and a half" — refers to the roughly 7.5-year period when Saturn transits the 12th, 1st, and 2nd houses from your natal Moon. It is the most discussed and most feared period in Indian astrology, and it deserves a clearer, more honest explanation.',
            'The three phases each last about 2.5 years. In the first phase (12th house from Moon), Saturn brings losses, expenses, and a feeling of separation — you may feel cut off from the world. In the second phase (1st house from Moon), the most intense, Saturn sits on your Moon, directly pressuring your mind, emotions, and self. In the third phase (2nd house from Moon), the pressure shifts to your finances, family, and speech, and the period winds down.',
            'Why does Sade Sati get such a bad reputation? Because Saturn is the karmic taskmaster, and during Sade Sati it audits your life. Weaknesses surface: poor health habits, financial carelessness, broken relationships, and unfulfilled responsibilities. It is not a punishment — it is an audit, and audits are painful only when the books are in disorder.',
            'Saturn\'s effect depends enormously on its placement and strength in your birth chart. For some, Sade Sati is a time of sudden promotion and public recognition. For others, it is a quiet period of illness, delays, and introspection. The difference lies partly in your chart and partly in how you respond.',
            'How to thrive during Sade Sati: serve others, especially the underprivileged and the elderly (Saturn\'s favourites). Be scrupulous with money and promises. Slow down — Saturn rewards patience, not speed. Maintain a simple routine, honour your parents, and avoid shortcuts. Many astrologers recommend simple Saturn remedies like lighting a sesame oil lamp on Saturdays and chanting the Shani mantra.',
            'Here is the liberating truth: some of the greatest achievements in people\'s lives happen during Sade Sati. Careers are built, debts are cleared, bodies are healed, and characters are forged in that crucible. If you are in your Sade Sati now, or approaching it, do not fear it — prepare for it. Our kundli tool shows your current dasha and transits so you can walk this period with awareness.'
        ]
    },
    {
        'id': 'rise-of-vedic-astrology',
        'title': 'Why Vedic Astrology Is Experiencing a Global Renaissance',
        'excerpt': 'From Silicon Valley to Bollywood, Jyotish is booming. Here\'s why ancient wisdom is trending again...',
        'date': '2026-07-05',
        'category': 'Culture',
        'read_time': '5 min',
        'content': [
            'Vedic astrology — Jyotish, "the science of light" — is one of the oldest continuous intellectual traditions on Earth, with roots stretching back thousands of years in the Indian subcontinent. And right now, it is experiencing an extraordinary global resurgence.',
            'Part of the appeal is precision. Unlike the popular Sun-sign horoscopes of Western columns, Vedic astrology is a deeply technical system. It uses the sidereal zodiac based on the actual, fixed positions of the stars, calculates exact planetary degrees with precision ephemeris data, and builds its predictions on layered systems like the Vimshottari dasha and the Navamsha chart.',
            'The modern world is hungry for meaning. In an age of algorithms and uncertainty, people are turning to systems that offer structure to their stories. Vedic astrology offers a framework that explains not just personality, but timing — when to act, when to wait, which seasons of life favour which efforts.',
            'The pandemic years accelerated this. Confronted with mortality and uncertainty, millions rediscovered practices — meditation, Ayurveda, yoga, and astrology — that treat the person as a whole: body, mind, and destiny. Jyotish is the map-making part of that toolkit.',
            'From celebrity astrologers with millions of followers to data scientists who appreciate its computational rigour, the audience for Vedic astrology is expanding and maturing. The best of the new wave blends the old wisdom with modern precision — exactly what we try to do here at Vedic Astro.',
            'If you are new to this tradition, you are arriving at a beautiful moment. The knowledge is more accessible than ever, and the tools — like the one you are using right now — make a deep and ancient system available to anyone with a date, a time, and a place of birth.'
        ]
    }
]

# Daily horoscope predictions
DAILY_HOROSCOPE = {
    'Aries': {'love': 3, 'career': 4, 'health': 3, 'finance': 3, 'message': 'Today brings fresh energy to your ambitions. Take bold steps in your career.'},
    'Taurus': {'love': 4, 'career': 3, 'health': 4, 'finance': 4, 'message': 'Financial opportunities await your attention. Stay grounded and practical.'},
    'Gemini': {'love': 3, 'career': 4, 'health': 3, 'finance': 3, 'message': 'Communication is your superpower today. Network and share your ideas.'},
    'Cancer': {'love': 5, 'career': 3, 'health': 3, 'finance': 3, 'message': 'Emotions run deep today. Connect with loved ones and nurture relationships.'},
    'Leo': {'love': 4, 'career': 5, 'health': 4, 'finance': 4, 'message': 'Your natural leadership shines today. Take charge and inspire others.'},
    'Virgo': {'love': 3, 'career': 4, 'health': 4, 'finance': 3, 'message': 'Attention to detail pays off. Focus on health and daily routines.'},
    'Libra': {'love': 5, 'career': 3, 'health': 3, 'finance': 4, 'message': 'Balance and harmony guide your day. Relationships bring joy.'},
    'Scorpio': {'love': 4, 'career': 4, 'health': 3, 'finance': 4, 'message': 'Deep transformations are possible. Trust your intuition today.'},
    'Sagittarius': {'love': 4, 'career': 4, 'health': 4, 'finance': 3, 'message': 'Adventure calls! Expand your horizons through learning or travel.'},
    'Capricorn': {'love': 3, 'career': 5, 'health': 3, 'finance': 4, 'message': 'Hard work bears fruit. Your discipline and ambition lead to success.'},
    'Aquarius': {'love': 4, 'career': 4, 'health': 4, 'finance': 4, 'message': 'Innovation and originality set you apart. Embrace your unique vision.'},
    'Pisces': {'love': 4, 'career': 3, 'health': 3, 'finance': 3, 'message': 'Creativity and compassion flow freely. Trust your dreams today.'}
}

def get_coordinates(city):
    city_lower = city.lower().strip()
    for key, val in CITY_DB.items():
        if key in city_lower or city_lower in key:
            return val
    return (28.61, 77.21)

def calc_julday(year, month, day, hour, minute):
    return swe.julday(year, month, day, hour + minute / 60.0)

def calc_planet_positions(julday, ayanamsa):
    positions = {}
    for name, pid in PLANET_IDS.items():
        result = swe.calc_ut(julday, pid)
        tropical_lon = result[0][0]
        sidereal_lon = (tropical_lon - ayanamsa) % 360
        speed = result[0][3] if len(result[0]) > 3 else 0
        sign_num = int(sidereal_lon / 30)
        positions[name] = {
            'lon': sidereal_lon, 'sign': sign_num,
            'sign_name': SIGN_NAMES[sign_num], 'sign_deg': sidereal_lon % 30,
            'retro': speed < 0, 'speed': speed
        }
    rahu_result = swe.calc_ut(julday, swe.MEAN_NODE)
    rahu_lon = (rahu_result[0][0] - ayanamsa) % 360
    positions['Rahu'] = {'lon': rahu_lon, 'sign': int(rahu_lon / 30),
        'sign_name': SIGN_NAMES[int(rahu_lon / 30)], 'sign_deg': rahu_lon % 30, 'retro': True}
    ketu_lon = (rahu_lon + 180) % 360
    positions['Ketu'] = {'lon': ketu_lon, 'sign': int(ketu_lon / 30),
        'sign_name': SIGN_NAMES[int(ketu_lon / 30)], 'sign_deg': ketu_lon % 30, 'retro': True}
    return positions

def calc_houses(julday, lat, lon):
    asc_result = swe.houses_ex(julday, lat, lon, b'P')
    ayanamsa = swe.get_ayanamsa(julday)
    asc_sidereal = (asc_result[0][0] - ayanamsa) % 360
    house_cusps = [(asc_result[0][i] - ayanamsa) % 360 for i in range(12)]
    return asc_sidereal, house_cusps

def get_house(longitude, house_cusps):
    for i in range(12):
        next_i = (i + 1) % 12
        if house_cusps[i] < house_cusps[next_i]:
            if house_cusps[i] <= longitude < house_cusps[next_i]: return i + 1
        else:
            if longitude >= house_cusps[i] or longitude < house_cusps[next_i]: return i + 1
    return 1

def calc_navamsha(longitude):
    sign_num = int(longitude / 30)
    deg_in_sign = longitude % 30
    nav_num = int(deg_in_sign * 9 / 30)
    if sign_num in [0, 3, 6, 9]: start = sign_num
    elif sign_num in [1, 4, 7, 10]: start = (sign_num + 8) % 12
    else: start = (sign_num + 4) % 12
    return (start + nav_num) % 12, (deg_in_sign % (30/9)) * 9

def calc_dasha(moon_lon):
    nakshatra_span = 360.0 / 27
    nakshatra_num = int(moon_lon / nakshatra_span)
    lord = NAKSHATRA_LORDS[nakshatra_num]
    pos_in_nak = moon_lon % nakshatra_span
    fraction = 1 - (pos_in_nak / nakshatra_span)
    balance = DHASE_YEARS[lord] * fraction
    return {
        'nakshatra': NAKSHATRA_NAMES[nakshatra_num],
        'lord': lord, 'balance_years': round(balance, 2),
        'nakshatra_num': nakshatra_num
    }

def get_full_dasha(moon_lon, birth_year):
    dasha_info = calc_dasha(moon_lon)
    lord = dasha_info['lord']
    balance = dasha_info['balance_years']
    start_idx = DHASE_ORDER.index(lord)
    sequence = DHASE_ORDER[start_idx:] + DHASE_ORDER[:start_idx]
    dashas = []
    cumulative = 0
    for i, dlord in enumerate(sequence):
        dur = balance if i == 0 else DHASE_YEARS[dlord]
        dashas.append({
            'lord': dlord, 'start_year': round(birth_year + cumulative, 1),
            'end_year': round(birth_year + cumulative + dur, 1), 'duration': round(dur, 1)
        })
        cumulative += dur
    return dashas

def get_yogas(positions, asc_sign):
    yogas = []
    house_planets = {}
    for name, p in positions.items():
        h = p['house']
        if h not in house_planets: house_planets[h] = []
        house_planets[h].append(name)
    
    for h, plist in house_planets.items():
        if len(plist) > 1:
            yogas.append({
                'name': f'{len(plist)}-Planet Conjunction in House {h}',
                'desc': f'{", ".join(plist)} together amplifies their combined effects',
                'strength': 'strong' if len(plist) >= 3 else 'moderate'
            })
    
    if positions['Sun']['sign'] == positions['Mercury']['sign']:
        yogas.append({'name': 'Budhaditya Yoga', 'desc': 'Sun-Mercury conjunction gives sharp intelligence', 'strength': 'strong'})
    
    if (positions['Jupiter']['sign'] - positions['Moon']['sign']) % 12 in [1, 4, 7, 10]:
        yogas.append({'name': 'Gaja Kesari Yoga', 'desc': 'Jupiter in Kendra from Moon brings wealth and fame', 'strength': 'strong'})
    
    for name, p in positions.items():
        nav_sign, _ = calc_navamsha(p['lon'])
        if nav_sign == p['sign'] and name not in ['Rahu', 'Ketu']:
            yogas.append({'name': f'Vargottama {name}', 'desc': f'{name} in same sign in D9 - extremely powerful', 'strength': 'very strong'})
    
    if positions['Mars']['sign'] == 7 and positions['Mars']['house'] == 10:
        yogas.append({'name': 'Ruchaka Mahapurusha Yoga', 'desc': 'Mars in own sign in 10th - exceptional leadership', 'strength': 'very strong'})
    
    if positions['Jupiter']['house'] == 7:
        yogas.append({'name': 'Jupiter in 7th House', 'desc': 'Blesses marriage with wisdom and harmony', 'strength': 'strong'})
    
    return yogas

def get_predictions(data):
    predictions = {}
    career_score = 0; career_text = []
    mars_planet = next((p for p in data['planets'] if p['name'] == 'Mars'), None)
    if mars_planet and mars_planet['house'] == 10:
        career_score += 30; career_text.append("Mars in 10th house gives exceptional career potential")
    sun_planet = next((p for p in data['planets'] if p['name'] == 'Sun'), None)
    if sun_planet and sun_planet['house'] == 11:
        career_score += 15; career_text.append("Sun in 11th house brings gains through profession")
    predictions['career'] = {'score': min(career_score, 100), 'text': career_text}
    
    finance_score = 0; finance_text = []
    jup_planet = next((p for p in data['planets'] if p['name'] == 'Jupiter'), None)
    if jup_planet and jup_planet['house'] == 7:
        finance_score += 20; finance_text.append("Jupiter in 7th brings wealth through partnerships")
    if sun_planet and sun_planet['house'] == 11:
        finance_score += 20; finance_text.append("Triple conjunction in 11th house is powerful for gains")
    predictions['finance'] = {'score': min(finance_score, 100), 'text': finance_text}
    
    marriage_score = 0; marriage_text = []
    if jup_planet and jup_planet['house'] == 7:
        marriage_score += 25; marriage_text.append("Jupiter in 7th blesses marriage with wisdom")
    venus_planet = next((p for p in data['planets'] if p['name'] == 'Venus'), None)
    if venus_planet and venus_planet.get('navamsha_sign') == 'Libra':
        marriage_score += 20; marriage_text.append("Venus in own sign in Navamsha - excellent for relationships")
    predictions['marriage'] = {'score': min(marriage_score, 100), 'text': marriage_text}
    
    predictions['health'] = {'score': 70, 'text': ["Generally good vitality", "Watch: respiratory system, joints, stress"]}
    
    edu_score = 0; edu_text = []
    sat_planet = next((p for p in data['planets'] if p['name'] == 'Saturn'), None)
    if sat_planet and sat_planet['house'] == 5:
        edu_score += 20; edu_text.append("Saturn in 5th gives deep analytical thinking")
    merc_planet = next((p for p in data['planets'] if p['name'] == 'Mercury'), None)
    if merc_planet and merc_planet['sign'] == 'Sagittarius':
        edu_score += 15; edu_text.append("Mercury in Sagittarius - interest in higher education")
    predictions['education'] = {'score': min(edu_score, 100), 'text': edu_text}
    
    return predictions

# === ROUTES ===

@app.route('/')
def home():
    return render_template('home.html', daily_horoscope=DAILY_HOROSCOPE)

@app.route('/kundli')
def kundli():
    return render_template('kundli.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=BLOG_POSTS)

@app.route('/blog/<post_id>')
def blog_post(post_id):
    post = next((p for p in BLOG_POSTS if p['id'] == post_id), None)
    if not post:
        return render_template('blog.html', posts=BLOG_POSTS)
    return render_template('blog_post.html', post=post)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/numerology')
def numerology():
    return render_template('numerology.html')

@app.route('/daily-horoscope')
def daily_horoscope():
    return render_template('daily_horoscope.html', signs=SIGN_NAMES, horoscopes=DAILY_HOROSCOPE)

@app.route('/api/calculate', methods=['POST'])
@limiter.limit("30 per minute")
def calculate():
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    try:
        # Input sanitization
        name = sanitize_string(data.get('name', 'User'), max_length=50)
        city = sanitize_string(data.get('city', 'Delhi'), max_length=100)
        email = sanitize_string(data.get('email', ''), max_length=100)
        
        # Validate date/time inputs
        year = int(data.get('year', 2000))
        month = int(data.get('month', 1))
        day = int(data.get('day', 1))
        hour = int(data.get('hour', 12))
        minute = int(data.get('minute', 0))
        
        # Range validation
        if not (1900 <= year <= 2025): year = 2000
        if not (1 <= month <= 12): month = 1
        if not (1 <= day <= 31): day = 1
        if not (0 <= hour <= 23): hour = 12
        if not (0 <= minute <= 59): minute = 0
        
        lat, lon = get_coordinates(city)
        julday = calc_julday(year, month, day, hour, minute)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(julday)
        
        positions = calc_planet_positions(julday, ayanamsa)
        asc_sidereal, house_cusps = calc_houses(julday, lat, lon)
        asc_sign = int(asc_sidereal / 30); asc_deg = asc_sidereal % 360
        
        for name_p, p in positions.items():
            p['house'] = get_house(p['lon'], house_cusps)
        
        navamsha = {}
        for name_p, p in positions.items():
            ns, nd = calc_navamsha(p['lon'])
            navamsha[name_p] = {'sign': ns, 'deg': nd}
        nav_asc_sign, nav_asc_deg = calc_navamsha(asc_sidereal)
        
        dasha = calc_dasha(positions['Moon']['lon'])
        full_dasha = get_full_dasha(positions['Moon']['lon'], year)
        yogas = get_yogas(positions, asc_sign)
        
        house_lords = {}
        for h in range(1, 13):
            sign_of_house = (asc_sign + h - 1) % 12
            house_lords[h] = SIGN_LORDS[sign_of_house]
        
        house_data = []
        for i in range(12):
            sign_num = int(house_cusps[i] / 30); deg = house_cusps[i] % 30
            house_data.append({'house': i + 1, 'sign': SIGN_NAMES[sign_num],
                'sign_short': SIGN_SHORT[sign_num], 'deg': round(deg, 2), 'lord': house_lords.get(i + 1, '')})
        
        planet_data = []
        for name_p in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu']:
            p = positions[name_p]
            planet_data.append({
                'name': name_p, 'symbol': PLANET_SYMBOLS.get(name_p, ''),
                'sign': p['sign_name'], 'sign_short': SIGN_SHORT[p['sign']],
                'deg': round(p['sign_deg'], 2), 'house': p['house'],
                'retro': p['retro'], 'navamsha_sign': SIGN_NAMES[navamsha[name_p]['sign']],
                'navamsha_deg': round(navamsha[name_p]['deg'], 2),
                'vargottama': navamsha[name_p]['sign'] == p['sign']
            })
        
        current_year = datetime.now().year + datetime.now().timetuple().tm_yday / 365
        current_dasha = None
        for d in full_dasha:
            if d['start_year'] <= current_year < d['end_year']:
                current_dasha = d; break
        
        predictions = get_predictions({'planets': planet_data})

        # Save lead if email provided
        if email and re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            lead_data = {
                'timestamp': datetime.now().isoformat(),
                'status': 'new',
                'email': email,
                'name': name,
                'birth': {'year': year, 'month': month, 'day': day,
                          'hour': hour, 'minute': minute, 'city': city},
                'ascendant': SIGN_NAMES[asc_sign],
                'sun_sign': SIGN_NAMES[positions['Sun']['sign']],
                'moon_sign': SIGN_NAMES[positions['Moon']['sign']],
                'dasha': dasha.get('lord', '') if isinstance(dasha, dict) else ''
            }
            save_lead(lead_data)
            send_lead_email(lead_data)

        result = {
            'success': True, 'name': name,
            'birth': {'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute, 'city': city},
            'ascendant': {'sign': SIGN_NAMES[asc_sign], 'sign_short': SIGN_SHORT[asc_sign], 'deg': round(asc_deg, 2)},
            'ayanamsa': round(ayanamsa, 4),
            'planets': planet_data, 'houses': house_data, 'house_lords': house_lords,
            'dasha': dasha, 'full_dasha': full_dasha, 'current_dasha': current_dasha,
            'yogas': yogas,
            'navamsha_asc': {'sign': SIGN_NAMES[nav_asc_sign], 'deg': round(nav_asc_deg, 2)},
            'vargottama_asc': nav_asc_sign == asc_sign,
            'predictions': predictions
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cities', methods=['GET'])
@limiter.limit("60 per minute")
def cities():
    query = sanitize_string(request.args.get('q', ''), max_length=50).lower()
    if not query:
        return jsonify([])
    matches = [city.title() for city in CITY_DB.keys() if query in city]
    return jsonify(matches[:10])

@app.route('/api/numerology', methods=['POST'])
@limiter.limit("30 per minute")
def numerology_check():
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    try:
        name = sanitize_string(data.get('name', ''), max_length=50)
        year = int(data.get('year', 2000))
        month = int(data.get('month', 1))
        day = int(data.get('day', 1))

        if not (1 <= month <= 12) or not (1 <= day <= 31) or not (1900 <= year <= 2030):
            return jsonify({'success': False, 'error': 'Invalid date'}), 400

        # Life Path = reduce full date to a single digit (or master number 11/22)
        total = sum(int(d) for d in str(year)) + month + day
        life_path = total
        while life_path > 9 and life_path not in (11, 22, 33):
            life_path = sum(int(d) for d in str(life_path))

        # Destiny = sum letters of name (A=1..Z=26 reduced)
        alpha_map = {}
        i = 1
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            alpha_map[c] = i if i <= 9 else (i % 9 if i % 9 else 9)
            i += 1
        name_total = 0
        for ch in name.upper():
            if ch.isalpha():
                name_total += alpha_map[ch]
        destiny = name_total
        while destiny > 9 and destiny not in (11, 22, 33):
            destiny = sum(int(d) for d in str(destiny))

        # Lucky numbers & days based on life path
        life_descriptions = {
            1: ('Independent, ambitious, a natural leader.', ['Sun', 'Aries', 'Leo'], [1, 10, 19, 28], ['Sunday', 'Monday'], 'Leadership, entrepreneurship, pioneering fields.'),
            2: ('Cooperative, diplomatic, sensitive.', ['Moon', 'Cancer'], [2, 11, 20, 29], ['Monday', 'Friday'], 'Partnerships, psychology, arts, diplomacy.'),
            3: ('Creative, expressive, sociable.', ['Jupiter', 'Sagittarius'], [3, 12, 21, 30], ['Thursday', 'Friday'], 'Arts, writing, entertainment, communication.'),
            4: ('Practical, disciplined, hardworking.', ['Rahu', 'Aquarius'], [4, 13, 22, 31], ['Sunday', 'Saturday'], 'Engineering, construction, management, security.'),
            5: ('Adventurous, versatile, freedom-loving.', ['Mercury', 'Gemini'], [5, 14, 23], ['Wednesday', 'Friday'], 'Travel, sales, media, entrepreneurship.'),
            6: ('Nurturing, responsible, family-oriented.', ['Venus', 'Libra'], [6, 15, 24], ['Friday', 'Monday'], 'Healing, teaching, hospitality, design.'),
            7: ('Analytical, spiritual, introspective.', ['Ketu', 'Pisces'], [7, 16, 25], ['Monday', 'Saturday'], 'Research, science, spirituality, analysis.'),
            8: ('Ambitious, powerful, business-minded.', ['Saturn', 'Capricorn'], [8, 17, 26], ['Saturday', 'Tuesday'], 'Business, finance, real estate, leadership.'),
            9: ('Compassionate, humanitarian, artistic.', ['Mars', 'Scorpio'], [9, 18, 27], ['Tuesday', 'Friday'], 'Humanitarian work, arts, counselling, medicine.'),
            11: ('Intuitive, inspired, visionary (Master Number).', ['Moon', 'Pisces'], [11, 22], ['Monday', 'Thursday'], 'Spiritual leadership, innovation, the arts.'),
            22: ('Master builder, practical visionary.', ['Jupiter', 'Capricorn'], [22, 4], ['Saturday', 'Thursday'], 'Large-scale projects, architecture, institutions.'),
            33: ('Master teacher, compassionate healer.', ['Venus', 'Leo'], [33, 6], ['Sunday', 'Friday'], 'Teaching, healing arts, spiritual guidance.'),
        }
        lp = life_descriptions.get(life_path, life_descriptions[1])
        dp = life_descriptions.get(destiny, life_descriptions[1])

        return jsonify({
            'success': True,
            'name': name,
            'life_path': life_path,
            'life_path_desc': lp[0],
            'life_planets': lp[1],
            'life_lucky_numbers': lp[2],
            'life_lucky_days': lp[3],
            'life_careers': lp[4],
            'destiny': destiny,
            'destiny_desc': dp[0],
            'destiny_careers': dp[4],
            'destiny_lucky_numbers': dp[2],
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        submitted = request.form.get('password', '')
        if submitted == LEAD_PASSWORD:
            session['admin_ok'] = True
        else:
            return render_template('admin.html', error='Wrong password')
    elif request.args.get('password') == LEAD_PASSWORD:
        session['admin_ok'] = True

    if not session.get('admin_ok'):
        return render_template('admin.html', error=None)

    leads = load_leads()
    payments = load_payments()
    feedback = load_feedback()
    return render_template('admin.html', admin_ok=True, leads=leads, payments=payments, feedback=feedback)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_ok', None)
    return render_template('admin.html', admin_ok=False)

@app.route('/admin/export')
def export_leads():
    if not session.get('admin_ok'):
        abort(401)
    leads = load_leads()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Email', 'Name', 'Birth Date', 'Time', 'City', 'Ascendant', 'Sun', 'Moon', 'Dasha'])
    for l in leads:
        b = l.get('birth', {})
        writer.writerow([
            l.get('timestamp', ''),
            l.get('email', ''),
            l.get('name', ''),
            f"{b.get('day', '')}/{b.get('month', '')}/{b.get('year', '')}",
            f"{b.get('hour', '')}:{b.get('minute', '')}",
            b.get('city', ''),
            l.get('ascendant', ''),
            l.get('sun_sign', ''),
            l.get('moon_sign', ''),
            l.get('dasha', '')
        ])
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=leads.csv'})

@app.route('/admin/update_lead', methods=['POST'])
def update_lead():
    if not session.get('admin_ok'):
        abort(401)
    data = request.json or {}
    idx = data.get('index')
    status = sanitize_string(data.get('status', ''), max_length=20)
    if idx is None or status not in ('new', 'contacted', 'paid', 'delivered'):
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    leads = load_leads()
    try:
        idx = int(idx)
        if 0 <= idx < len(leads):
            leads[idx]['status'] = status
            with open(LEADS_FILE, 'w', encoding='utf-8') as f:
                json.dump(leads, f, indent=2, ensure_ascii=False)
            return jsonify({'success': True})
    except Exception:
        pass
    return jsonify({'success': False, 'error': 'Lead not found'}), 400

@app.route('/admin/update_payment', methods=['POST'])
def update_payment():
    if not session.get('admin_ok'):
        abort(401)
    data = request.json or {}
    idx = data.get('index')
    status = sanitize_string(data.get('status', ''), max_length=20)
    if idx is None or status not in ('pending', 'paid', 'delivered', 'refunded'):
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    payments = load_payments()
    try:
        idx = int(idx)
        if 0 <= idx < len(payments):
            payments[idx]['status'] = status
            with open(PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(payments, f, indent=2, ensure_ascii=False)
            return jsonify({'success': True})
    except Exception:
        pass
    return jsonify({'success': False, 'error': 'Payment not found'}), 400

@app.route('/admin/export_payments')
def export_payments():
    if not session.get('admin_ok'):
        abort(401)
    payments = load_payments()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Name', 'Email', 'Plan', 'Amount INR', 'Method', 'Status'])
    for p in payments:
        writer.writerow([
            p.get('timestamp', ''),
            p.get('name', ''),
            p.get('email', ''),
            p.get('plan', ''),
            p.get('amount_inr', ''),
            p.get('payment_method', ''),
            p.get('status', '')
        ])
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=payments.csv'})

# === FEEDBACK ROUTES ===
@app.route('/api/feedback', methods=['POST'])
@limiter.limit("20 per minute")
def feedback():
    data = request.json or {}
    ftype = sanitize_string(data.get('type', 'suggestion'), max_length=20)
    if ftype not in ('suggestion', 'complaint'):
        ftype = 'suggestion'
    email = sanitize_string(data.get('email', ''), max_length=100)
    message = sanitize_string(data.get('message', ''), max_length=2000)
    if not message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    if email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jsonify({'success': False, 'error': 'Invalid email'}), 400
    count = save_feedback({
        'timestamp': datetime.now().isoformat(),
        'type': ftype,
        'email': email,
        'message': message,
    })
    return jsonify({'success': True, 'id': count})

@app.route('/admin/export_feedback')
def export_feedback():
    if not session.get('admin_ok'):
        abort(401)
    items = load_feedback()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Type', 'Email', 'Message'])
    for f in items:
        writer.writerow([
            f.get('timestamp', ''),
            f.get('type', ''),
            f.get('email', ''),
            f.get('message', '')
        ])
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=feedback.csv'})

# === PAYMENT ROUTES ===
@app.route('/checkout')
def checkout_page():
    return render_template('checkout.html')

@app.route('/api/payment/request', methods=['POST'])
@limiter.limit("20 per minute")
def payment_request():
    data = request.json or {}
    plan = sanitize_string(data.get('plan', 'premium'), max_length=20)
    if plan not in PRICING:
        plan = 'premium'
    name = sanitize_string(data.get('name', ''), max_length=50)
    email = sanitize_string(data.get('email', ''), max_length=100)
    method = sanitize_string(data.get('method', 'other'), max_length=20)
    if not name or not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jsonify({'success': False, 'error': 'Name and valid email required'}), 400
    plan_data = PRICING[plan]
    count = save_payment({
        'timestamp': datetime.now().isoformat(),
        'status': 'pending',
        'payment_method': method,
        'plan': plan_data['name'],
        'amount_inr': plan_data['inr'],
        'amount_usd': plan_data['usd'],
        'email': email,
        'name': name,
    })
    return jsonify({'success': True, 'plan': plan_data['name'], 'id': count})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
