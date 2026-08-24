// WanderUSVI Tours App
// Load tours from JSON and render with descriptions

// Fallback for tour records with no image. Applied at render time, not just via
// onerror: `src="undefined"` costs a real 404 before onerror can rescue it.
// Local + Pexels-licensed; images/ATTRIBUTION.md records source slug
// "scenic-view-of-st-thomas-harbor-in-summer-34650321",
// which verifies the region from the source URL, not from our own caption.
const FALLBACK_IMAGE = '/images/hero-photo-1.jpg';

let toursData = [];

// Wire the homepage "Verified Tours" stat to the live (non-dead) catalog
// size, replacing the hardcoded value. No-op on pages without the element.
function updateVerifiedToursCount(n) {
    const el = document.getElementById('verified-tours-count');
    if (el) el.textContent = Number(n).toLocaleString();
}

// ===== BOOKING PERFORMANCE OPTIMIZATIONS =====

// 1. URL Caching - Pre-cache FareHarbor URLs for instant clicks
const bookingUrlCache = {};

function cacheBookingUrl(tourId, url) {
    bookingUrlCache[tourId] = {
        url: url,
        cached_at: Date.now()
    };
    try {
        localStorage.setItem('fh_cache_' + tourId, JSON.stringify(bookingUrlCache[tourId]));
    } catch (e) {
        // localStorage full - continue without persistence
    }
}

function getBookingUrl(tourId, fallbackUrl) {
    const cached = bookingUrlCache[tourId];
    if (cached && Date.now() - cached.cached_at < 3600000) {
        return cached.url;
    }
    return fallbackUrl;
}

function preCacheBookingUrls(tours) {
    tours.forEach(tour => {
        if (tour.bookingUrl) {
            cacheBookingUrl(tour.id || tour.name, tour.bookingUrl);
        }
    });
}

// 2. GA4 Tracking Functions
// NOTE: Renamed from trackBookingClick to avoid shadowing the canonical
// 3-string global (defined in index.html <head> and /tracking.js). This
// enriched form fires on tour-grid clicks where company/price are known.
function trackTourBooking(tour) {
    gtag('event', 'booking_click', {
        tour_id: tour.id,
        tour_name: tour.name,
        island: tour.island,
        price: tour.price || 'unknown',
        company: tour.company,
        event_category: 'conversion'
    });
}

function trackFilterChange(filterType, value) {
    gtag('event', 'filter_used', {
        filter_type: filterType,
        value: value,
        event_category: 'engagement'
    });
}

function trackSearchUsed(searchTerm) {
    gtag('event', 'search_used', {
        query: searchTerm,
        event_category: 'engagement'
    });
}

function trackLoadMoreClick() {
    gtag('event', 'load_more_clicked', {
        event_category: 'engagement'
    });
}

// 3. Loading indicator with optimization
function openBookingWithLoader(url, tour) {
    event && event.preventDefault && event.preventDefault();
    
    // Track the booking click
    if (tour) {
        trackTourBooking(tour);
    }
    
    const loader = document.createElement('div');
    loader.id = 'booking-loader';
    loader.className = 'booking-loader';
    loader.innerHTML = `
        <div class="booking-loader-content">
            <div class="spinner"></div>
            <p>Opening booking...</p>
        </div>
    `;
    document.body.appendChild(loader);
    
    setTimeout(() => loader.style.opacity = '1', 10);
    window.open(url, '_blank', 'noopener,noreferrer');
    
    setTimeout(() => {
        loader.style.opacity = '0';
        setTimeout(() => loader.remove(), 300);
    }, 2500);
}
let filteredTours = [];
let displayedCount = 0;
const TOURS_PER_PAGE = 24;

// Read ?activity=<value> and, when it names a real option on #activity-filter,
// pre-select it and render the filtered grid. This is what makes deep links
// like /index.html?activity=Snorkel#tours-section land on a filtered grid.
//
// Matching is case-insensitive against the option's value but always assigns
// the option's canonical value, so ?activity=snorkel and ?activity=Snorkel
// both resolve to the "Snorkel" tag that tour records actually carry.
// Returns true when a filter was applied — filterTours() renders and updates
// the results count itself, so the caller must not render again.
function applyActivityFromUrl() {
    let requested;
    try {
        requested = new URLSearchParams(window.location.search).get('activity');
    } catch (e) {
        return false;
    }
    if (!requested) return false;

    const select = document.getElementById('activity-filter');
    if (!select) return false;

    const wanted = requested.trim().toLowerCase();
    const match = Array.from(select.options)
        .find(o => o.value && o.value.toLowerCase() === wanted);

    if (!match) {
        console.warn(`⚠️ ?activity=${requested} matches no activity filter option — ignoring`);
        return false;
    }

    select.value = match.value;
    console.log(`🔗 ?activity=${requested} → filtering on "${match.value}"`);
    filterTours();
    return true;
}

// Load tours data
async function loadTours() {
    try {
        console.log('🔄 Fetching tours-data.json...');
        const response = await fetch('tours-data.json');
        console.log(`📥 Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const _raw = await response.json();
        toursData = Array.isArray(_raw) ? _raw : _raw.tours;
        toursData = toursData.filter(t => t.status !== 'inactive' && !t.bookingDead);
        updateVerifiedToursCount(toursData.length);
        console.log(`✅ Loaded ${toursData.length} tours`);

        // Initial shuffle for randomization (per-page-load, non-mutating)
        toursData = shuffleArray(toursData);
        filteredTours = [...toursData];
        
        // Pre-cache booking URLs for instant clicks
        preCacheBookingUrls(toursData);
        
        displayedCount = 0;
        // A ?activity= param pre-selects the activity dropdown and renders the
        // filtered grid instead of the full one. When absent (or unrecognised)
        // this is a no-op and the unfiltered render below runs as before.
        if (!applyActivityFromUrl()) {
            renderTours();
            updateResultsCount();
        }
        console.log('✅ Tours rendered successfully');
    } catch (error) {
        console.error('❌ Error loading tours:', error.message);
        // The grid may be absent — that is one of the ways we get here — so the
        // handler must not repeat the deref that threw. Without this null check
        // the catch itself throws, replacing a logged error with an uncaught one.
        const grid = document.getElementById('tours-grid');
        if (grid) {
            grid.innerHTML = `
            <div class="error-state">
                <p>⚠️ Unable to load tours. Please refresh the page.</p>
                <p style="font-size: 12px; color: #666;">Error: ${error.message}</p>
            </div>
        `;
        }
    }
}

// Helper functions
function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Three ruled branches, plus the unchanged fallback.
//
//   charter (verified)  -> "From $X · private boat"
//   per adult           -> "From $X per adult"
//   no usable price     -> null, and the caller emits NO price element at all.
//                          Not empty text, not a placeholder node — no node.
//
// Every other label (per person unverified, unknown, per group, …) still gets
// the "Price on request" fallback: those units are not adjudicated yet, and
// inventing a basis for them is how a whole-boat fare gets read as a seat price.
function formatPrice(price, confidence, priceLabel) {
    if (!Number.isFinite(price) || price <= 0) return null;
    if (priceLabel === 'private boat' && confidence === 'high') return `From $${price} · private boat`;
    if (priceLabel === 'per adult' && (confidence === 'high' || confidence === 'medium')) return `From $${price} per adult`;
    return 'Price on request';
}

function cleanLocation(location = '') {
    return location
        .replace(/^United States\/U\.?S\.? Virgin Islands\//, '')
        .replace(/^U\.?S\.? Virgin Islands\//, '')
        .trim() || 'U.S. Virgin Islands';
}

function scoreLabel(score) {
    if (score >= 90) return 'Top Rated';
    if (score >= 75) return 'Popular';
    return '';
}

function generateTourSchema(tour) {
    const priceGated = tour.priceLabel === 'per adult' && (tour.priceConfidence === 'high' || tour.priceConfidence === 'medium');
    return {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": tour.name,
        "description": tour.description || "",
        "touristType": tour.tags ? tour.tags.join(", ") : "",
        "offers": {
            "@type": "Offer",
            ...(priceGated ? { "price": tour.price } : {}),
            "priceCurrency": "USD",
            "url": tour.bookingUrl
            // No "availability". It was hardcoded to schema.org/InStock on every
            // card regardless of whether the product could actually be booked;
            // measured 2026-08-17, 120 of the 561 grid-renderable records (21.4%)
            // have no bookable availability, so a mean 5 of the 24 cards rendered
            // per load asserted InStock for something unbookable. schema.org does
            // not require Offer.availability — omitting it is valid, asserting it
            // falsely is not. Restore only from a live liveness signal, never a
            // constant.
        },
        "provider": {
            "@type": "LocalBusiness",
            "name": tour.company
        }
    };
}

// Fisher-Yates shuffle (non-mutating)
function shuffleArray(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// Create tour card HTML
function createTourCard(tour) {
    const tags = tour.tags || [];
    const tagDisplay = tags.slice(0, 3).map(tag =>
        `<span class="tour-tag">${escapeHtml(tag)}</span>`
    ).join('');
    
    const description = tour.description || '';
    const truncatedDesc = description.length > 120 
        ? description.substring(0, 117) + '...' 
        : description;
    
    const score = tour.qualityScore || 0;
    const badge = scoreLabel(score);
    const qualityBadge = badge 
        ? `<span class="quality-badge">⭐ ${badge}</span>` 
        : '';
    
    const cleanLoc = cleanLocation(tour.location);
    const priceDisplay = formatPrice(tour.price, tour.priceConfidence, tour.priceLabel);
    // null => the row has no usable price, so the element itself is omitted.
    const priceHtml = priceDisplay === null ? '' : `<div class="tour-price">${priceDisplay}</div>`;
    
    const schema = generateTourSchema(tour);
    const schemaJson = JSON.stringify(schema).replace(/<\/script/gi, '<\\/script');
    
    let badgesHtml = '<div class="tour-badges">';
    if (tour.freeCancellation) {
        badgesHtml += '<span class="trust-badge free-cancel">Free Cancellation</span>';
    }
    badgesHtml += '</div>';
    
    return `
        <article class="tour-card" data-id="${tour.id}">
            <script type="application/ld+json">${schemaJson}</script>
            <div class="tour-image">
                <img src="${tour.image || FALLBACK_IMAGE}" alt="${escapeHtml(tour.name)}" loading="lazy" width="400" height="300" onerror="this.src='${FALLBACK_IMAGE}'" style="width: 100%; height: auto; object-fit: cover;">
                ${qualityBadge}
            </div>
            <div class="tour-content">
                <div class="tour-meta">
                    <span class="tour-location">📍 ${escapeHtml(cleanLoc)}, ${escapeHtml(capitalizeIsland(tour.island))}</span>
                </div>
                <h3 class="tour-title">${escapeHtml(tour.name)}</h3>
                <p class="tour-description">${escapeHtml(truncatedDesc)}</p>
                <div class="tour-tags">${tagDisplay}</div>
                <div class="tour-footer">
                    ${priceHtml}
                    <a href="${tour.bookingUrl}" target="_blank" rel="noopener" class="book-now-btn tour-book-btn" data-tour-id="${escapeHtml(tour.id)}" data-tour-name="${escapeHtml(tour.name)}" style="text-decoration: none;">Check Availability →</a>
                </div>
            </div>
        </article>
    `;
}

function capitalizeIsland(island) {
    if (!island) return '';
    const lower = island.toLowerCase();
    if (lower === 'big island') return 'Big Island';
    if (lower === 'vi') return 'St. Thomas';
    return island.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
}

// Render tours to grid
function renderTours(append = false) {
    const grid = document.getElementById('tours-grid');
    const toursToShow = filteredTours.slice(
        append ? displayedCount : 0, 
        displayedCount + TOURS_PER_PAGE
    );
    
    const html = toursToShow.map(createTourCard).join('');
    
    if (append) {
        grid.insertAdjacentHTML('beforeend', html);
    } else {
        grid.innerHTML = html;
    }
    
    displayedCount = append 
        ? displayedCount + toursToShow.length 
        : toursToShow.length;
    
    // Show/hide load more button
    const loadMoreBtn = document.getElementById('load-more');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = displayedCount >= filteredTours.length ? 'none' : 'block';
    }
}

// Load more tours
function loadMoreTours() {
    trackLoadMoreClick();
    renderTours(true);
}

// Update results count
function updateResultsCount() {
    const countEl = document.getElementById('results-count');
    if (countEl) {
        countEl.textContent = `Showing ${Math.min(displayedCount, filteredTours.length)} of ${filteredTours.length} adventures`;
    }
}

// Some activity-filter options collapse several data tags into one buyer-facing
// choice. Anything not listed here matches itself, unchanged.
const ACTIVITY_TAG_ALIASES = {
    'Transportation': ['Transportation', 'Transfer', 'Shuttle', 'Bus Tour'],
    'Jet Ski': ['Jet Ski Rental', 'Jet Ski Tour'],
};

// Filter tours
function filterTours() {
    const islandFilter = document.getElementById('island-filter')?.value?.toLowerCase() || '';
    const activityFilter = document.getElementById('activity-filter')?.value || '';
    const sortFilter = document.getElementById('sort-filter')?.value || 'quality';
    const searchInput = document.getElementById('search-input')?.value?.toLowerCase() || '';
    
    // Track filter usage
    if (islandFilter) trackFilterChange('island', islandFilter);
    if (activityFilter) trackFilterChange('activity', activityFilter);
    if (searchInput) trackSearchUsed(searchInput);
    
    filteredTours = toursData.filter(tour => {
        // Island filter
        if (islandFilter && tour.island?.toLowerCase() !== islandFilter) {
            return false;
        }
        
        // Activity filter
        if (activityFilter) {
            const wantedTags = ACTIVITY_TAG_ALIASES[activityFilter] || [activityFilter];
            if (!tour.tags?.some(t => wantedTags.includes(t))) {
                return false;
            }
        }
        
        // Search filter
        if (searchInput) {
            const searchFields = [
                tour.name,
                tour.company,
                tour.location,
                tour.description,
                ...(tour.tags || [])
            ].join(' ').toLowerCase();
            
            if (!searchFields.includes(searchInput)) {
                return false;
            }
        }
        
        return true;
    });
    
    // Sort
    if (sortFilter === 'quality') {
        filteredTours.sort((a, b) => (b.qualityScore || 0) - (a.qualityScore || 0));
    } else if (sortFilter === 'name') {
        filteredTours.sort((a, b) => a.name.localeCompare(b.name));
    }
    
    displayedCount = 0;
    renderTours();
    updateResultsCount();
}

// Shuffle visible tours
function shuffleTours() {
    filteredTours = shuffleArray(filteredTours);
    displayedCount = 0;
    renderTours();
}

// Clear all filters
function clearAllFilters() {
    const islandFilter = document.getElementById('island-filter');
    const activityFilter = document.getElementById('activity-filter');
    const sortFilter = document.getElementById('sort-filter');
    const searchInput = document.getElementById('search-input');
    
    if (islandFilter) islandFilter.value = '';
    if (activityFilter) activityFilter.value = '';
    if (sortFilter) sortFilter.value = 'quality';
    if (searchInput) searchInput.value = '';
    
    filterTours();
}

// Quick filter from tags/buttons
function quickFilter(term) {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = term;
    }
    filterTours();
    
    // Scroll to tours section
    document.getElementById('tours-section')?.scrollIntoView({ behavior: 'smooth' });
}

// Hero search
function executeHeroSearch() {
    const heroSearch = document.getElementById('hero-search');
    if (heroSearch?.value) {
        quickFilter(heroSearch.value);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Pages that load app.js without a grid to draw into (advertise.html) must
    // not pull tours-data.json — it is ~1.9MB fetched only to be thrown away,
    // and renderTours() would then deref a null #tours-grid. Same guard shape
    // as activity-tours.js, which checks its own grid before its fetch.
    if (document.getElementById('tours-grid')) {
        loadTours();
    }

    // The delegated Book Now click handler that used to call
    // openBookingWithLoader was a workaround for the previous <button>
    // markup, which couldn't navigate natively. Now that tour cards
    // render as <a href target="_blank">, navigation happens via the
    // anchor's native click and tracking.js's delegated handler still
    // fires booking_click. No JS handler needed here.

    // Filter change listeners
    document.getElementById('island-filter')?.addEventListener('change', () => {
        const val = document.getElementById('island-filter').value;
        if (val) trackFilterChange('island', val);
        filterTours();
    });
    document.getElementById('activity-filter')?.addEventListener('change', () => {
        const val = document.getElementById('activity-filter').value;
        if (val) trackFilterChange('activity', val);
        filterTours();
    });
    document.getElementById('sort-filter')?.addEventListener('change', () => {
        const val = document.getElementById('sort-filter').value;
        if (val) trackFilterChange('sort', val);
        filterTours();
    });
    
    // Search input with debounce
    let searchTimeout;
    document.getElementById('search-input')?.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(filterTours, 300);
    });
    
    // Hero search enter key
    document.getElementById('hero-search')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            executeHeroSearch();
        }
    });
});

// Mobile menu toggle
document.querySelector('.mobile-menu-btn')?.addEventListener('click', function() {
    document.querySelector('.nav-mobile')?.classList.toggle('active');
    this.classList.toggle('active');
});

// FOMO notifications - DISABLED
// These fake notifications were removed to improve user trust
// Users should see real booking confirmations only

// Weather widget
async function loadWeather() {
    const CACHE_KEY = 'wx-cache-wusvi';
    const TTL_MS = 10 * 60 * 1000;
    const weatherEl = document.getElementById('header-weather');
    if (!weatherEl) return;
    try {
        const cached = JSON.parse(sessionStorage.getItem(CACHE_KEY) || 'null');
        if (cached && Date.now() - cached.ts < TTL_MS) {
            weatherEl.querySelector('.weather-temp').textContent = `${cached.temp}°F`;
            return;
        }
        const response = await fetch('https://api.open-meteo.com/v1/forecast?latitude=18.3419&longitude=-64.9307&current_weather=true&temperature_unit=fahrenheit');
        const data = await response.json();
        const temp = Math.round(data.current_weather.temperature);
        weatherEl.querySelector('.weather-temp').textContent = `${temp}°F`;
        sessionStorage.setItem(CACHE_KEY, JSON.stringify({ temp, ts: Date.now() }));
    } catch (error) {
        // Silent fail
    }
}

loadWeather();

// Promo Banner
function closeBanner() {
    const banner = document.getElementById('promo-banner');
    if (banner) {
        banner.classList.add('hidden');
        sessionStorage.setItem('promoBannerClosed', 'true');
    }
}

// Check if banner was closed this session
if (sessionStorage.getItem('promoBannerClosed') === 'true') {
    document.addEventListener('DOMContentLoaded', () => {
        const banner = document.getElementById('promo-banner');
        if (banner) banner.classList.add('hidden');
    });
}

// ===== STICKY MOBILE CTA BAR =====
document.addEventListener('DOMContentLoaded', () => {
    const stickyBar = document.getElementById('sticky-cta-bar');
    if (!stickyBar) return;
    
    const heroSection = document.querySelector('.hero') || document.querySelector('.tours-section');
    let heroScrolled = false;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY > (heroSection?.offsetHeight || 300);
        
        if (scrolled && !heroScrolled) {
            stickyBar.classList.add('visible');
            heroScrolled = true;
        } else if (!scrolled && heroScrolled) {
            stickyBar.classList.remove('visible');
            heroScrolled = false;
        }
    });
    
    const ctaButton = stickyBar.querySelector('button');
    if (ctaButton) {
        ctaButton.addEventListener('click', () => {
            const toursGrid = document.getElementById('tours-grid');
            if (toursGrid) {
                toursGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
});
