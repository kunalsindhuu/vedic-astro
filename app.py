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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages')
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
        'read_time': '5 min'
    },
    {
        'id': 'vimshottari-dasha-explained',
        'title': 'Vimshottari Dasha: How Planetary Periods Shape Your Life',
        'excerpt': 'Learn how the ancient Vimshottari Dasha system can predict major life events and opportunities...',
        'date': '2026-08-08',
        'category': 'Predictive',
        'read_time': '7 min'
    },
    {
        'id': 'raj-yogas-in-vedic-astrology',
        'title': 'Raj Yogas: The Royal Combinations for Success',
        'excerpt': 'Discover the powerful Raj Yogas that can bring wealth, power, and recognition in your life...',
        'date': '2026-08-05',
        'category': 'Yogas',
        'read_time': '6 min'
    },
    {
        'id': 'saturn-transit-2026',
        'title': 'Saturn Transit 2026: What It Means for Each Sign',
        'excerpt': 'Saturn\'s transit through Pisces brings significant changes. Learn how it affects your sign...',
        'date': '2026-08-02',
        'category': 'Transits',
        'read_time': '8 min'
    },
    {
        'id': 'navamsha-chart-importance',
        'title': 'Why Your Navamsha Chart Matters More Than You Think',
        'excerpt': 'The Navamsha (D9) chart reveals your true destiny, marriage potential, and spiritual path...',
        'date': '2026-07-28',
        'category': 'Charts',
        'read_time': '6 min'
    },
    {
        'id': 'marriage-compatibility-factors',
        'title': 'Marriage Compatibility: Beyond Just Sun Sign Matching',
        'excerpt': 'Real Vedic compatibility analysis considers 8+ factors. Learn what actually matters...',
        'date': '2026-07-25',
        'category': 'Relationships',
        'read_time': '7 min'
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

@app.route('/compatibility')
def compatibility():
    return render_template('compatibility.html')

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

@app.route('/api/compatibility', methods=['POST'])
@limiter.limit("30 per minute")
def compatibility_check():
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    try:
        sign1 = sanitize_string(data.get('sign1', 'Aries'), max_length=20)
        sign2 = sanitize_string(data.get('sign2', 'Leo'), max_length=20)
        
        # Simple compatibility based on elements
        elements = {'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
                   'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
                   'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
                   'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'}
        
        elem1 = elements.get(sign1, 'Fire')
        elem2 = elements.get(sign2, 'Fire')
        
        # Compatibility logic
        same_element = elem1 == elem2
        compatible_pairs = [('Fire', 'Air'), ('Earth', 'Water')]
        is_compatible = (elem1, elem2) in compatible_pairs or (elem2, elem1) in compatible_pairs
        
        if same_element:
            score = 75
            verdict = "Good - Same element creates understanding"
        elif is_compatible:
            score = 85
            verdict = "Excellent - Complementary elements create balance"
        else:
            score = 50
            verdict = "Challenging - Different elements require adjustment"
        
        return jsonify({
            'success': True,
            'sign1': sign1, 'sign2': sign2,
            'score': score, 'verdict': verdict,
            'element1': elem1, 'element2': elem2
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
    return render_template('admin.html', admin_ok=True, leads=leads)

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

if __name__ == '__main__':
    app.run(debug=True, port=8080)
