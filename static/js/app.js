// Constants
const SIGN_NAMES = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
const SIGN_SHORT = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi'];
const SIGN_SYMBOLS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
const PLANET_SYMBOLS = { 'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋' };

// === LANGUAGE TRANSLATIONS ===
const translations = {
    en: {
        home: "Home", kundli: "Free Kundli", horoscope: "Horoscope", numerology: "Numerology",
        services: "Services", pricing: "Pricing", blog: "Blog", about: "About", contact: "Contact",
        hero_title: "Discover Your Destiny",
        hero_subtitle: "Authentic Vedic astrology powered by real planetary calculations. Get your birth chart, Dasha predictions, and personalized insights.",
        hero_btn1: "Get Free Kundli", hero_btn2: "Our Services",
        cities: "Cities", real_calc: "Real Calculations", free_report: "Free Basic Report",
        what_you_get: "What You Get", accurate_calc: "Accurate Calculations",
        accurate_desc: "Powered by Swiss Ephemeris - the same precision engine used by NASA and professional astronomers.",
        complete_chart: "Complete Birth Chart", complete_desc: "North & South Indian Kundli, Navamsha (D9), and all planetary positions with degrees.",
        dasha_pred: "Dasha Predictions", dasha_desc: "Complete Vimshottari Dasha timeline showing your current and future planetary periods.",
        yoga_detection: "Yoga Detection", yoga_desc: "Automatic identification of powerful yogas in your chart like Raj Yogas and Dhana Yogas.",
        numerology_check: "Numerology Calculator", numerology_desc: "Find your Life Path and Destiny numbers, lucky days, and ideal career paths.",
        daily_horoscope: "Daily Horoscope", daily_desc: "Daily predictions based on your moon sign with love, career, health, and finance scores.",
        today_horoscope: "Today's Horoscope", quick_preview: "Quick preview for each zodiac sign",
        how_works: "How It Works", step1: "Enter Birth Details", step1_desc: "Provide your date, time, and place of birth",
        step2: "Precise Calculations", step2_desc: "Our engine calculates planetary positions using Swiss Ephemeris",
        step3: "Get Your Report", step3_desc: "Receive detailed analysis with predictions and insights",
        testimonials: "What People Say",
        ready: "Ready to Discover Your Destiny?",
        lucky_section: "🎨 Your Lucky Color & Number",
        lucky_based: "Based on your Ascendant lord and birth details",
        lucky_color: "Lucky Color", lucky_number: "Lucky Number", lucky_gem: "Lucky Gemstone", lucky_dir: "Lucky Direction",
        based_on: "Based on", birth_details: "birth details",
        astro_yogas: "Astrological Yogas", dasha_timeline: "Vimshottari Dasha Timeline",
        life_analysis: "Life Analysis", life_scores: "Life Scores",
        your_chart: "'s Birth Chart", birth_info: "Birth Information",
        planet: "Planet", sign: "Sign", degree: "Degree", house: "House", retro: "Retrograde",
        name_label: "Full Name", city_label: "City of Birth", email_label: "Email Address",
        enter_name: "Enter your full name", enter_city: "Start typing your birth city...",
        enter_email: "your@email.com",
        fill_all: "Please fill in all fields", calc_running: "Calculating planetary positions...",
        calc_precision: "Using Swiss Ephemeris for precision",
        email_hint: "Your detailed reading will be sent to this email within 24 hours",
        email_success_title: "Your Reading is Being Prepared!",
        email_success_msg: "Your detailed Kundli reading will be sent to",
        email_success_time: "within 24 hours",
        email_note: "Please check your inbox (and spam folder) for your personalized report"
    },
    hi: {
        home: "होम", kundli: "मुफ्त कुंडली", horoscope: "राशिफल", numerology: "अंक ज्योतिष",
        services: "सेवाएं", pricing: "मूल्य", blog: "ब्लॉग", about: "हमारे बारे में", contact: "संपर्क",
        hero_title: "अपना भाग्य जानें",
        hero_subtitle: "वास्तविक ग्रह गणनाओं से संचालित प्रमाणित वैदिक ज्योतिष। अपनी जन्म कुंडली, दशा भविष्यवाणियां और व्यक्तिगत जानकारी प्राप्त करें।",
        hero_btn1: "मुफ्त कुंडली पाएं", hero_btn2: "हमारी सेवाएं",
        cities: "शहर", real_calc: "वास्तविक गणना", free_report: "मुफ्त बेसिक रिपोर्ट",
        what_you_get: "आपको क्या मिलेगा", accurate_calc: "सटीक गणना",
        accurate_desc: "स्विस एफीमेरिस द्वारा संचालित - नासा और पेशेवर खगोलविदों द्वारा उपयोग किया जाने वाला वही सटीकता इंजन।",
        complete_chart: "पूर्ण जन्म कुंडली", complete_desc: "उत्तर और दक्षिण भारतीय कुंडली, नवांश (D9), और डिग्री के साथ सभी ग्रह स्थितियां।",
        dasha_pred: "दशा भविष्यवाणियां", dasha_desc: "आपकी वर्तमान और भावी ग्रह अवधियों को दर्शाने वाली पूर्ण विंशोत्तरी दशा समयरेखा।",
        yoga_detection: "योग पहचान", yoga_desc: "राज योग और धन योग जैसे आपकी कुंडली में शक्तिशाली योगों की स्वचालित पहचान।",
        numerology_check: "अंक ज्योतिष कैलकुलेटर", numerology_desc: "अपना लाइफ पाथ और डेस्टिनी नंबर, भाग्यशाली दिन और आदर्श करियर खोजें।",
        daily_horoscope: "दैनिक राशिफल", daily_desc: "प्रेम, करियर, स्वास्थ्य और वित्त स्कोर के साथ आपकी चंद्र राशि के आधार पर दैनिक भविष्यवाणियां।",
        today_horoscope: "आज का राशिफल", quick_preview: "प्रत्येक राशि का त्वरित पूर्वावलोकन",
        how_works: "यह कैसे काम करता है", step1: "जन्म विवरण दर्ज करें", step1_desc: "अपनी तिथि, समय और जन्म स्थान प्रदान करें",
        step2: "सटीक गणना", step2_desc: "हमारा इंजन स्विस एफीमेरिस का उपयोग करके ग्रहों की स्थिति की गणना करता है",
        step3: "अपनी रिपोर्ट प्राप्त करें", step3_desc: "भविष्यवाणियों और अंतर्दृष्टि के साथ विस्तृत विश्लेषण प्राप्त करें",
        testimonials: "लोग क्या कहते हैं",
        ready: "अपना भाग्य जानने के लिए तैयार हैं?",
        lucky_section: "🎨 आपका भाग्यशाली रंग और संख्या",
        lucky_based: "आपकी लग्न देवता और जन्म विवरण के आधार पर",
        lucky_color: "भाग्यशाली रंग", lucky_number: "भाग्�yशाली संख्या", lucky_gem: "भाग्यशाली रत्न", lucky_dir: "भाग्यशाली दिशा",
        based_on: "आधारित", birth_details: "जन्म विवरण",
        astro_yogas: "ज्योतिषीय योग", dasha_timeline: "विंशोत्तरी दशा समयरेखा",
        life_analysis: "जीवन विश्लेषण", life_scores: "जीवन स्कोर",
        your_chart: " की जन्म कुंडली", birth_info: "जन्म जानकारी",
        planet: "ग्रह", sign: "राशि", degree: "डिग्री", house: "भाव", retro: "वक्री",
        name_label: "पूरा नाम", city_label: "जन्म शहर", email_label: "ईमेल पता",
        enter_name: "अपना पूरा नाम दर्ज करें", enter_city: "अपना जन्म शहर टाइप करना शुरू करें...",
        enter_email: "your@email.com",
        fill_all: "कृपया सभी फ़ील्ड भरें", calc_running: "ग्रहों की स्थिति की गणना हो रही है...",
        calc_precision: "सटीकता के लिए स्विस एफीमेरिस का उपयोग",
        email_hint: "आपकी विस्तृत रीडिंग 24 घंटे के भीतर इस ईमेल पर भेजी जाएगी",
        email_success_title: "आपकी रीडिंग तैयार की जा रही है!",
        email_success_msg: "आपकी विस्तृत कुंडली रीडिंग भेजी जाएगी",
        email_success_time: "24 घंटे के भीतर",
        email_note: "कृपया अपने इनबॉक्स (और स्पैम फ़ोल्डर) में अपनी व्यक्तिगत रिपोर्ट देखें"
    }
};

let currentLang = localStorage.getItem('lang') || 'en';

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    localStorage.setItem('lang', currentLang);
    document.getElementById('lang-text').textContent = currentLang === 'en' ? 'हिन्दी' : 'English';
    updatePageLanguage();
}

function updatePageLanguage() {
    const t = translations[currentLang];
    if (!t) return;
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) {
            el.textContent = t[key];
        }
    });
    
    // Update placeholder texts
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (t[key]) {
            el.placeholder = t[key];
        }
    });
    
    document.documentElement.lang = currentLang === 'hi' ? 'hi' : 'en';
    document.documentElement.dir = 'ltr';
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    setupCityAutocomplete();
    setupNavToggle();
    updatePageLanguage();
});



function setupNavToggle() {
    const toggle = document.querySelector('.nav-toggle');
    const links = document.getElementById('navLinks');
    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('active');
        });
    }
}

function setupCityAutocomplete() {
    const cityInput = document.getElementById('city');
    const datalist = document.getElementById('city-list');
    if (!cityInput || !datalist) return;
    
    cityInput.addEventListener('input', async () => {
        const query = cityInput.value;
        if (query.length < 2) return;
        try {
            const res = await fetch(`/api/cities?q=${query}`);
            const cities = await res.json();
            datalist.innerHTML = '';
            cities.forEach(city => {
                const opt = document.createElement('option');
                opt.value = city;
                datalist.appendChild(opt);
            });
        } catch (e) {}
    });
}

// Form submission - SIMPLIFIED
document.getElementById('birth-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Get values
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var day = document.getElementById('day').value;
    var month = document.getElementById('month').value;
    var year = document.getElementById('year').value;
    var hour = document.getElementById('hour').value;
    var minute = document.getElementById('minute').value;
    var city = document.getElementById('city').value;

    // Simple validation
    if (!name) { alert('Please enter your name'); return; }
    if (!day) { alert('Please select day'); return; }
    if (!month) { alert('Please select month'); return; }
    if (!year) { alert('Please select year'); return; }
    if (hour == '') { alert('Please select hour'); return; }
    if (minute == '') { alert('Please select minute'); return; }
    if (!city) { alert('Please enter city'); return; }

    var data = {
        name: name,
        email: email,
        day: parseInt(day),
        month: parseInt(month),
        year: parseInt(year),
        hour: parseInt(hour),
        minute: parseInt(minute),
        city: city
    };

    // Show loading
    document.getElementById('input-section').style.display = 'none';
    document.getElementById('loading').classList.remove('hidden');

    try {
        var response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        var result = await response.json();
        
        if (result.success) {
            displayResults(result);
            if (email) {
                showEmailConfirmation(email);
            }
        } else {
            alert('Error: ' + result.error);
            document.getElementById('input-section').style.display = 'block';
        }
    } catch (err) {
        alert('Error connecting to server. Please try again.');
        document.getElementById('input-section').style.display = 'block';
    }
    
    document.getElementById('loading').classList.add('hidden');
});

function showEmailConfirmation(email) {
    document.getElementById('email-confirmation-container').innerHTML = 
        '<div class="card email-confirmation">' +
        '<div class="email-confirmation-content">' +
        '<span class="email-icon">📧</span>' +
        '<h3>Your Reading is Being Prepared!</h3>' +
        '<p>Your detailed Kundli reading will be sent to <strong>' + email + '</strong> within <strong>24 hours</strong>.</p>' +
        '</div></div>';
}

function displayResults(data) {
    document.getElementById('results').classList.remove('hidden');
    
    document.getElementById('result-name').textContent = `${data.name}'s Birth Chart`;
    document.getElementById('result-birth-info').textContent = 
        `${data.birth.day}/${data.birth.month}/${data.birth.year} at ${String(data.birth.hour).padStart(2,'0')}:${String(data.birth.minute).padStart(2,'0')} | ${data.birth.city}`;
    
    document.getElementById('asc-info').textContent = `${SIGN_SHORT[SIGN_NAMES.indexOf(data.ascendant.sign)]} ${data.ascendant.sign} ${data.ascendant.deg}°`;
    
    const moonPlanet = data.planets.find(p => p.name === 'Moon');
    document.getElementById('moon-sign').textContent = moonPlanet ? `${moonPlanet.sign_short} ${moonPlanet.sign}` : '-';
    document.getElementById('nakshatra').textContent = data.dasha.nakshatra;
    
    if (data.current_dasha) {
        document.getElementById('current-dasha').textContent = `${data.current_dasha.lord} (${data.current_dasha.start_year.toFixed(0)}-${data.current_dasha.end_year.toFixed(0)})`;
    }

    if (data.vargottama_asc) {
        document.getElementById('vargottama-badge').classList.remove('hidden');
    }

    // Planet Table (if present)
    const planetTbody = document.querySelector('#planet-table tbody');
    if (planetTbody) {
        planetTbody.innerHTML = '';
        data.planets.forEach(p => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${PLANET_SYMBOLS[p.name]} ${p.name}</strong></td>
                <td>${SIGN_SHORT[SIGN_NAMES.indexOf(p.sign)]} ${p.sign}</td>
                <td>${p.deg}°</td>
                <td>${p.house}</td>
                <td class="${p.retro ? 'retro' : ''}">${p.retro ? '◐ Retro' : 'Direct'}</td>
                <td>${SIGN_SHORT[SIGN_NAMES.indexOf(p.navamsha_sign)]}</td>
                <td class="${p.vargotta ? 'vargotta' : ''}">${p.vargotta ? '✓' : ''}</td>
            `;
            planetTbody.appendChild(row);
        });
    }

    renderNorthChart(data);
    renderSouthChart(data);
    renderNavamshaChart(data);

    // Planet Cards Grid
    renderPlanetCards(data);

    // Lucky Color, Number, Gemstone, Direction
    calculateLuckyAttributes(data);

    // Yogas
    const yogasDiv = document.getElementById('yogas-list');
    yogasDiv.innerHTML = '';
    if (!data.yogas || data.yogas.length === 0) {
        yogasDiv.innerHTML = '<p style="color:var(--text-muted)">No major yogas detected.</p>';
    } else {
        data.yogas.forEach(y => {
            const div = document.createElement('div');
            div.className = `yoga-item ${y.strength || ''}`;
            div.innerHTML = `<span class="yoga-name">${y.name}</span><span class="yoga-desc">${y.desc}</span>`;
            yogasDiv.appendChild(div);
        });
    }

    // Dasha
    const dashaBody = document.querySelector('#dasha-table tbody');
    dashaBody.innerHTML = '';
    data.full_dasha.forEach(d => {
        const isCurrent = data.current_dasha && data.current_dasha.lord === d.lord && 
            Math.abs(data.current_dasha.start_year - d.start_year) < 0.1;
        const row = document.createElement('tr');
        row.style.background = isCurrent ? 'rgba(78, 205, 196, 0.1)' : '';
        row.innerHTML = `
            <td><strong>${d.lord}</strong></td>
            <td>${d.start_year.toFixed(1)}</td>
            <td>${d.end_year.toFixed(1)}</td>
            <td>${d.duration.toFixed(1)}y</td>
            <td>${isCurrent ? '<span class="current-badge">NOW</span>' : ''}</td>
        `;
        dashaBody.appendChild(row);
    });

    renderPredictions(data);
    renderScores(data.predictions);
    
    setTimeout(() => {
        document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function renderPlanetCards(data) {
    const container = document.getElementById('planet-cards-grid');
    if (!container) return;
    
    const planetColors = {
        'Sun': '#FFD700', 'Moon': '#C0C0C0', 'Mars': '#FF4500', 'Mercury': '#00FF00',
        'Jupiter': '#FFA500', 'Venus': '#FFB6C1', 'Saturn': '#DAA520', 'Rahu': '#800080', 'Ketu': '#708090'
    };
    
    const planetSVG = {
        'Sun': `<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="12" fill="${planetColors['Sun']}"/><circle cx="20" cy="20" r="8" fill="#FFA500"/><line x1="20" y1="2" x2="20" y2="8" stroke="${planetColors['Sun']}" stroke-width="2"/><line x1="20" y1="32" x2="20" y2="38" stroke="${planetColors['Sun']}" stroke-width="2"/><line x1="2" y1="20" x2="8" y2="20" stroke="${planetColors['Sun']}" stroke-width="2"/><line x1="32" y1="20" x2="38" y2="20" stroke="${planetColors['Sun']}" stroke-width="2"/></svg>`,
        'Moon': `<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="15" fill="${planetColors['Moon']}"/><circle cx="26" cy="20" r="12" fill="#050510"/></svg>`,
        'Mars': `<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="14" fill="${planetColors['Mars']}"/><circle cx="16" cy="16" r="4" fill="#8B0000" opacity="0.4"/></svg>`,
        'Mercury': `<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="13" fill="${planetColors['Mercury']}"/><circle cx="15" cy="15" r="5" fill="#00AA00" opacity="0.4"/></svg>`,
        'Jupiter': `<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="15" fill="${planetColors['Jupiter']}"/><ellipse cx="20" cy="20" rx="15" ry="5" fill="#CD853F" opacity="0.5"/><ellipse cx="20" cy="20" rx="15" ry="2" fill="#8B4513" opacity="0.3"/></svg>`,
        'Venus': `<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="13" fill="${planetColors['Venus']}"/><circle cx="20" cy="20" r="8" fill="#FF69B4" opacity="0.4"/></svg>`,
        'Saturn': `<svg width="50" height="35" viewBox="0 0 50 35"><ellipse cx="25" cy="17" rx="6" ry="6" fill="${planetColors['Saturn']}"/><ellipse cx="25" cy="17" rx="16" ry="3" fill="none" stroke="#B8860B" stroke-width="2"/></svg>`,
        'Rahu': `<svg width="40" height="40" viewBox="0 0 40 40"><path d="M20 5 L25 15 L35 15 L27 22 L30 35 L20 27 L10 35 L13 22 L5 15 L15 15 Z" fill="${planetColors['Rahu']}"/></svg>`,
        'Ketu': `<svg width="40" height="40" viewBox="0 0 40 40"><path d="M20 5 L23 15 L35 15 L25 22 L28 35 L20 27 L12 35 L15 22 L5 15 L17 15 Z" fill="${planetColors['Ketu']}"/><circle cx="20" cy="20" r="5" fill="#050510"/></svg>`
    };
    
    container.innerHTML = '';
    data.planets.forEach(p => {
        const card = document.createElement('div');
        card.className = `planet-card ${p.name.toLowerCase()}`;
        card.innerHTML = `
            <div class="planet-card-icon">${planetSVG[p.name] || '⚪'}</div>
            <div class="planet-card-name">${p.name}</div>
            <div class="planet-card-sign">${p.sign_short} ${p.sign}</div>
            <div class="planet-card-deg">${p.deg}°</div>
            <div class="planet-card-house">House ${p.house}</div>
            ${p.retro ? '<span class="planet-card-retro">◐ Retrograde</span>' : ''}
        `;
        container.appendChild(card);
    });
}

function renderNorthChart(data) {
    const container = document.getElementById('north-chart');
    const ascSign = SIGN_NAMES.indexOf(data.ascendant.sign);
    
    const housePositions = {
        12: {row: 0, col: 0}, 1: {row: 0, col: 1}, 2: {row: 0, col: 2}, 3: {row: 0, col: 3},
        11: {row: 1, col: 0}, 4: {row: 1, col: 3},
        10: {row: 2, col: 0}, 5: {row: 2, col: 3},
        9: {row: 3, col: 0}, 8: {row: 3, col: 1}, 7: {row: 3, col: 2}, 6: {row: 3, col: 3}
    };
    
    const housePlanets = {};
    data.planets.forEach(p => {
        if (!housePlanets[p.house]) housePlanets[p.house] = [];
        const retro = p.retro ? '<span class="retro-marker">◐</span>' : '';
        housePlanets[p.house].push(`${PLANET_SYMBOLS[p.name]}${retro}`);
    });
    
    let html = '<div class="north-chart">';
    for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
            const house = Object.keys(housePositions).find(h => 
                housePositions[h].row === row && housePositions[h].col === col
            );
            if (house) {
                const signNum = (ascSign + parseInt(house) - 1) % 12;
                const planets = housePlanets[house] || [];
                html += `<div class="cell">
                    <span class="sign">${SIGN_SHORT[signNum]}</span>
                    <span class="planets">${planets.join(' ')}</span>
                </div>`;
            } else if (row === 1 && col === 1) {
                html += `<div class="cell center"><span class="sign">LAGNA</span><span class="planets">${SIGN_SHORT[ascSign]} ${data.ascendant.deg}°</span></div>`;
            } else if ((row === 1 && col === 2) || (row === 2 && col === 1) || (row === 2 && col === 2)) {
                html += '<div class="cell center"></div>';
            }
        }
    }
    html += '</div>';
    container.innerHTML = html;
}

function renderSouthChart(data) {
    const container = document.getElementById('south-chart');
    const ascSign = SIGN_NAMES.indexOf(data.ascendant.sign);
    
    const signPositions = {
        0: {row: 0, col: 0}, 1: {row: 0, col: 1}, 2: {row: 0, col: 2}, 3: {row: 0, col: 3},
        4: {row: 1, col: 0}, 5: {row: 1, col: 3},
        6: {row: 2, col: 0}, 7: {row: 2, col: 3},
        8: {row: 3, col: 0}, 9: {row: 3, col: 1}, 10: {row: 3, col: 2}, 11: {row: 3, col: 3}
    };
    
    const signPlanets = {};
    data.planets.forEach(p => {
        const signIdx = SIGN_NAMES.indexOf(p.sign);
        if (!signPlanets[signIdx]) signPlanets[signIdx] = [];
        const retro = p.retro ? '<span class="retro-marker">◐</span>' : '';
        signPlanets[signIdx].push(`${PLANET_SYMBOLS[p.name]}${retro}`);
    });
    
    let html = '<div class="south-chart">';
    for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
            const sign = Object.keys(signPositions).find(s => 
                signPositions[s].row === row && signPositions[s].col === col
            );
            if (sign) {
                const planets = signPlanets[sign] || [];
                html += `<div class="cell">
                    <span class="sign">${SIGN_SHORT[sign]}</span>
                    <span class="planets">${planets.join(' ')}</span>
                </div>`;
            } else {
                html += '<div class="cell empty"></div>';
            }
        }
    }
    html += '</div>';
    container.innerHTML = html;
}

function renderNavamshaChart(data) {
    const container = document.getElementById('navamsha-chart');
    const navAscSign = SIGN_NAMES.indexOf(data.navamsha_asc.sign);
    
    const housePositions = {
        12: {row: 0, col: 0}, 1: {row: 0, col: 1}, 2: {row: 0, col: 2}, 3: {row: 0, col: 3},
        11: {row: 1, col: 0}, 4: {row: 1, col: 3},
        10: {row: 2, col: 0}, 5: {row: 2, col: 3},
        9: {row: 3, col: 0}, 8: {row: 3, col: 1}, 7: {row: 3, col: 2}, 6: {row: 3, col: 3}
    };
    
    const housePlanets = {};
    data.planets.forEach(p => {
        const navSign = SIGN_NAMES.indexOf(p.navamsha_sign);
        const house = ((navSign - navAscSign + 12) % 12) + 1;
        if (!housePlanets[house]) housePlanets[house] = [];
        const retro = p.retro ? '<span class="retro-marker">◐</span>' : '';
        housePlanets[house].push(`${PLANET_SYMBOLS[p.name]}${retro}`);
    });
    
    let html = '<div class="north-chart">';
    for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
            const house = Object.keys(housePositions).find(h => 
                housePositions[h].row === row && housePositions[h].col === col
            );
            if (house) {
                const signNum = (navAscSign + parseInt(house) - 1) % 12;
                const planets = housePlanets[house] || [];
                html += `<div class="cell">
                    <span class="sign">${SIGN_SHORT[signNum]}</span>
                    <span class="planets">${planets.join(' ')}</span>
                </div>`;
            } else if (row === 1 && col === 1) {
                html += `<div class="cell center"><span class="sign">NAVAMSHA</span><span class="planets">${SIGN_SHORT[navAscSign]}</span></div>`;
            } else if ((row === 1 && col === 2) || (row === 2 && col === 1) || (row === 2 && col === 2)) {
                html += '<div class="cell center"></div>';
            }
        }
    }
    html += '</div>';
    container.innerHTML = html;
}

function renderPredictions(data) {
    const container = document.getElementById('predictions');
    let html = '';
    
    if (data.predictions) {
        const p = data.predictions;
        if (p.career) {
            html += `<div class="pred-section"><h3>📊 Career & Profession</h3><ul>`;
            p.career.text.forEach(t => { html += `<li>${t}</li>`; });
            html += `</ul></div>`;
        }
        if (p.finance) {
            html += `<div class="pred-section"><h3>💰 Finance & Wealth</h3><ul>`;
            p.finance.text.forEach(t => { html += `<li>${t}</li>`; });
            html += `</ul></div>`;
        }
        if (p.marriage) {
            html += `<div class="pred-section"><h3>💕 Marriage & Relationships</h3><ul>`;
            p.marriage.text.forEach(t => { html += `<li>${t}</li>`; });
            html += `</ul></div>`;
        }
        if (p.education) {
            html += `<div class="pred-section"><h3>📚 Education & Learning</h3><ul>`;
            p.education.text.forEach(t => { html += `<li>${t}</li>`; });
            html += `</ul></div>`;
        }
        if (p.health) {
            html += `<div class="pred-section"><h3>🏥 Health</h3><ul>`;
            p.health.text.forEach(t => { html += `<li>${t}</li>`; });
            html += `</ul></div>`;
        }
    }
    
    if (data.current_dasha) {
        html += `<div class="pred-section"><h3>⏳ Current Period: ${data.current_dasha.lord} Mahadasha</h3><p>`;
        const dashaInfo = {
            'Jupiter': 'Jupiter Mahadasha brings growth, opportunities, education, and partnerships. This 16-year period favors marriage, higher learning, and spiritual growth.',
            'Rahu': 'Rahu Mahadasha brings unconventional opportunities and rapid changes. Stay grounded, avoid shortcuts. Focus on innovation.',
            'Saturn': 'Saturn Mahadasha brings hard work, discipline, and eventual success. Results come slowly but are long-lasting.',
            'Mars': 'Mars Mahadasha brings energy, courage, and action. Good for career advancement and competitive fields.',
            'Venus': 'Venus Mahadasha brings luxury, relationships, creativity, and artistic pursuits.',
            'Mercury': 'Mercury Mahadasha brings communication skills, learning, and business acumen.',
            'Sun': 'Sun Mahadasha brings authority, recognition, and leadership opportunities.',
            'Moon': 'Moon Mahadasha brings emotional growth, nurturing, and domestic happiness.',
            'Ketu': 'Ketu Mahadasha brings spiritual growth, detachment, and mystical experiences.'
        };
        html += dashaInfo[data.current_dasha.lord] || 'A significant planetary period is active in your life.';
        html += `</p></div>`;
    }
    
    container.innerHTML = html;
}

function renderScores(predictions) {
    const container = document.getElementById('score-grid');
    if (!predictions) { container.innerHTML = ''; return; }
    
    const categories = [
        { key: 'career', label: 'Career', icon: '📊' },
        { key: 'finance', label: 'Finance', icon: '💰' },
        { key: 'marriage', label: 'Marriage', icon: '💕' },
        { key: 'education', label: 'Education', icon: '📚' },
        { key: 'health', label: 'Health', icon: '🏥' }
    ];
    
    let html = '';
    categories.forEach(cat => {
        if (predictions[cat.key]) {
            const score = predictions[cat.key].score;
            html += `<div class="score-card">
                <div class="score-value">${score}</div>
                <div class="score-label">${cat.icon} ${cat.label}</div>
                <div class="score-bar"><div class="score-bar-fill" style="width: ${score}%"></div></div>
            </div>`;
        }
    });
    
    container.innerHTML = html;
}

function showChart(type) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    if (type === 'north') {
        document.getElementById('north-chart').classList.remove('hidden');
        document.getElementById('south-chart').classList.add('hidden');
    } else {
        document.getElementById('north-chart').classList.add('hidden');
        document.getElementById('south-chart').classList.remove('hidden');
    }
}

// === LUCKY ATTRIBUTES CALCULATION ===
function calculateLuckyAttributes(data) {
    const ascSign = data.ascendant.sign;
    const birthDay = data.birth.day;
    
    // Planet ruling each sign
    const signLords = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    };
    
    const lord = signLords[ascSign] || 'Sun';
    
    // Lucky colors based on planet
    const planetColors = {
        'Sun': { name: 'Gold / Orange', color: '#FFA500', hex: '#FFA500' },
        'Moon': { name: 'White / Silver', color: '#C0C0C0', hex: '#E8E8E8' },
        'Mars': { name: 'Red / Crimson', color: '#DC143C', hex: '#DC143C' },
        'Mercury': { name: 'Green / Emerald', color: '#50C878', hex: '#50C878' },
        'Jupiter': { name: 'Yellow / Saffron', color: '#FFD700', hex: '#FFD700' },
        'Venus': { name: 'White / Pink', color: '#FFB6C1', hex: '#FFB6C1' },
        'Saturn': { name: 'Blue / Black', color: '#1E3A5F', hex: '#1E3A5F' },
        'Rahu': { name: 'Purple', color: '#800080', hex: '#800080' },
        'Ketu': { name: 'Grey / Smoke', color: '#708090', hex: '#708090' }
    };
    
    // Lucky numbers based on planet
    const planetNumbers = {
        'Sun': 1, 'Moon': 2, 'Mars': 9, 'Mercury': 5, 'Jupiter': 3,
        'Venus': 6, 'Saturn': 8, 'Rahu': 4, 'Ketu': 7
    };
    
    // Lucky gemstones
    const planetGems = {
        'Sun': { name: 'Ruby (Manik)', icon: '🔴' },
        'Moon': { name: 'Pearl (Moti)', icon: '⚪' },
        'Mars': { name: 'Red Coral (Moonga)', icon: '🔴' },
        'Mercury': { name: 'Emerald (Panna)', icon: '💚' },
        'Jupiter': { name: 'Yellow Sapphire (Pukhraj)', icon: '💛' },
        'Venus': { name: 'Diamond (Heera)', icon: '💎' },
        'Saturn': { name: 'Blue Sapphire (Neelam)', icon: '💙' },
        'Rahu': { name: 'Hessite (Gomed)', icon: '🟤' },
        'Ketu': { name: 'Cat\'s Eye (Lehsunia)', icon: '👁️' }
    };
    
    // Lucky directions
    const planetDirections = {
        'Sun': { name: 'East', icon: '🌅' },
        'Moon': { name: 'North', icon: '⬆️' },
        'Mars': { name: 'South', icon: '⬇️' },
        'Mercury': { name: 'North', icon: '⬆️' },
        'Jupiter': { name: 'North-East', icon: '↗️' },
        'Venus': { name: 'South-East', icon: '↘️' },
        'Saturn': { name: 'West', icon: '⬅️' },
        'Rahu': { name: 'South-West', icon: '↙️' },
        'Ketu': { name: 'North-West', icon: '↖️' }
    };
    
    // Calculate lucky number from birth day + planet
    const planetNum = planetNumbers[lord] || 1;
    const luckyNum = ((birthDay + planetNum) % 9) || 9;
    
    // Display results
    const colorInfo = planetColors[lord] || planetColors['Sun'];
    document.getElementById('lucky-color').style.background = colorInfo.hex;
    document.getElementById('lucky-color').style.boxShadow = `0 0 30px ${colorInfo.hex}80`;
    document.getElementById('lucky-color-name').textContent = colorInfo.name;
    
    document.getElementById('lucky-number').textContent = luckyNum;
    document.getElementById('lucky-number-desc').textContent = `Based on ${lord} (ruling planet)`;
    
    const gemInfo = planetGems[lord] || planetGems['Sun'];
    document.getElementById('lucky-gem-icon').textContent = gemInfo.icon;
    document.getElementById('lucky-gem-name').textContent = gemInfo.name;
    
    const dirInfo = planetDirections[lord] || planetDirections['Sun'];
    document.getElementById('lucky-direction-icon').textContent = dirInfo.icon;
    document.getElementById('lucky-direction-name').textContent = dirInfo.name;
}

// Checkout form - payment request (manual payment)
const checkoutForm = document.getElementById('checkout-form');
if (checkoutForm) {
    checkoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('pay-btn');
        const name = document.getElementById('pay-name').value;
        const email = document.getElementById('pay-email').value;
        const plan = document.getElementById('pay-plan').value;
        const method = document.getElementById('pay-method').value;
        if (!name) { alert('Please enter your name'); return; }
        if (!email) { alert('Please enter your email'); return; }

        btn.disabled = true;
        btn.textContent = 'Submitting...';
        try {
            const res = await fetch('/api/payment/request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, email: email, plan: plan, method: method })
            });
            const result = await res.json();
            if (result.success) {
                document.getElementById('checkout-form').style.display = 'none';
                document.getElementById('payment-result').style.display = 'block';
                document.getElementById('payment-result-msg').textContent =
                    'Thank you ' + name + '! We\'ll email payment instructions for the ' + result.plan +
                    ' to ' + email + ' shortly.';
            } else {
                alert('Error: ' + (result.error || 'Could not submit'));
                btn.disabled = false; btn.textContent = 'Proceed';
            }
        } catch (err) {
            alert('Error connecting to server. Please try again.');
            btn.disabled = false;
            btn.textContent = 'Proceed';
        }
    });
}
// Numerology calculator
const numerologyForm = document.getElementById('numerology-form');
if (numerologyForm) {
    numerologyForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('num-name').value;
        const day = document.getElementById('num-day').value;
        const month = document.getElementById('num-month').value;
        const year = document.getElementById('num-year').value;
        if (!name || !day || !month || !year) {
            alert('Please fill all fields');
            return;
        }
        try {
            const res = await fetch('/api/numerology', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, day: parseInt(day), month: parseInt(month), year: parseInt(year) })
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById('numerology-result').classList.remove('hidden');
                document.getElementById('num-life-path').textContent = data.life_path;
                document.getElementById('num-life-desc').textContent = data.life_path_desc;
                document.getElementById('num-life-planets').textContent = data.life_planets.join(', ');
                document.getElementById('num-lucky-numbers').textContent = data.life_lucky_numbers.join(', ');
                document.getElementById('num-lucky-days').textContent = data.life_lucky_days.join(', ');
                document.getElementById('num-careers').textContent = data.life_careers;
                document.getElementById('num-destiny').textContent = data.destiny;
                document.getElementById('num-destiny-desc').textContent = data.destiny_desc;
                document.getElementById('numerology-result').scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + (data.error || 'Something went wrong'));
            }
        } catch (err) {
            alert('Error connecting to server. Please try again.');
        }
    });
}

// Admin status updates
function updateLeadStatus(el) {
    fetch('/admin/update_lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: el.dataset.index, status: el.value })
    }).then(r => r.json()).then(d => {
        if (d.success) { el.style.borderColor = 'var(--success, #2ecc71)'; }
    });
}
function updatePaymentStatus(el) {
    fetch('/admin/update_payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: el.dataset.index, status: el.value })
    }).then(r => r.json()).then(d => {
        if (d.success) { el.style.borderColor = 'var(--success, #2ecc71)'; }
    });
}

const contactForm = document.getElementById('contact-form');if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('contact-name').value;
        const email = document.getElementById('contact-email').value;
        const subject = document.getElementById('contact-subject').value;
        const message = document.getElementById('contact-message').value;
        const mailTo = 'supportvedicastro77@gmail.com';
        const body = encodeURIComponent('Name: ' + name + '\nEmail: ' + email + '\n\n' + message);
        const url = 'mailto:' + mailTo + '?subject=' + encodeURIComponent(subject) + '&body=' + body;
        window.location.href = url;
        contactForm.reset();
    });
}

// Suggestion & Complaint forms
function submitFeedback(type) {
    const emailId = type === 'suggestion' ? 'suggestion-email' : 'complaint-email';
    const messageId = type === 'suggestion' ? 'suggestion-message' : 'complaint-message';
    const successId = type === 'suggestion' ? 'suggestion-success' : 'complaint-success';
    const email = document.getElementById(emailId).value;
    const message = document.getElementById(messageId).value;

    if (!message.trim()) {
        alert('Please write a message');
        return;
    }

    fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: type, email: email, message: message })
    }).then(r => r.json()).then(d => {
        const el = document.getElementById(successId);
        if (d.success) {
            el.textContent = type === 'suggestion'
                ? '✅ Thank you! Your suggestion has been received.'
                : '✅ Thank you! Your complaint has been received. We will address it within 24 hours.';
            el.classList.remove('hidden');
            document.getElementById(emailId).value = '';
            document.getElementById(messageId).value = '';
        } else {
            alert('Error: ' + (d.error || 'Could not submit'));
        }
    }).catch(() => {
        alert('Error connecting to server. Please try again.');
    });
}

const suggestionForm = document.getElementById('suggestion-form');
if (suggestionForm) {
    suggestionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitFeedback('suggestion');
    });
}

const complaintForm = document.getElementById('complaint-form');
if (complaintForm) {
    complaintForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitFeedback('complaint');
    });
}
