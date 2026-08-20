document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. DATA FROM DATA.JS AND FINDINGS
    // =========================================================================
    
    // Check if AGED_CARE_DATA is loaded
    if (typeof AGED_CARE_DATA === 'undefined') {
        console.error("Aged Care dataset is not loaded. Make sure data.js is loaded before app.js.");
        return;
    }

    const data = AGED_CARE_DATA;
    const facilities = data.facilities;

    // Macro Trends: Matched-Facility Trends (2024 vs 2026)
    const matchedTrends = [
        { label: 'Overall Star Rating', val2024: 3.64, val2026: 3.85, change: +0.21 },
        { label: 'Residents\' Experience', val2024: 3.44, val2026: 3.65, change: +0.21 },
        { label: 'Compliance Audit', val2024: 4.52, val2026: 4.91, change: +0.39 },
        { label: 'Staffing Levels', val2024: 2.83, val2026: 3.24, change: +0.40 },
        { label: 'Quality Measures (Clinical)', val2024: 3.56, val2026: 3.08, change: -0.48 }
    ];

    // Lived Experience: Resident Survey Dimensions (% "Always" Satisfied)
    const residentDimensions = [
        { dimension: 'Feeling Safe', percentage: 78.3, type: 'strength' },
        { dimension: 'I Feel Heard', percentage: 72.2, type: 'strength' },
        { dimension: 'Staff are Caring', percentage: 69.3, type: 'strength' },
        { dimension: 'Clear Communication', percentage: 45.9, type: 'weakness' },
        { dimension: 'Service Operations', percentage: 45.6, type: 'weakness' },
        { dimension: 'Staff Competence', percentage: 43.6, type: 'weakness' },
        { dimension: 'Food Quality', percentage: 28.2, type: 'critical_weakness' }
    ];

    // State Rank Divergence (Official Badge vs Clinical Outcomes)
    const stateDivergence = [
        { state: 'NSW', officialRank: 5, outcomeRank: 2, divergence: +3 },
        { state: 'SA', officialRank: 8, outcomeRank: 6, divergence: +2 },
        { state: 'TAS', officialRank: 2, outcomeRank: 1, divergence: +1 },
        { state: 'ACT', officialRank: 3, outcomeRank: 4, divergence: -1 },
        { state: 'QLD', officialRank: 4, outcomeRank: 5, divergence: -1 },
        { state: 'VIC', officialRank: 6, outcomeRank: 7, divergence: -1 },
        { state: 'WA', officialRank: 7, outcomeRank: 8, divergence: -1 },
        { state: 'NT', officialRank: 1, outcomeRank: 3, divergence: -2 }
    ];

    // Audit Flags & Clinical Disconnects (2026)
    // Counts and percentages are calculated live from the 2,180 facility records
    // actually loaded by this site (the same complete-2026-rating scope used for
    // the README's audit-vs-outcome analysis), so this stays correct if the
    // underlying dataset is ever refreshed.
    const riskFlagDefinitions = [
        { key: 'adequately_staffed_poor_outcomes', flag: 'Adequately Staffed, Poor Outcomes', desc: 'Met target nurse minutes, but holds low clinical quality stars (1-2★).' },
        { key: 'high_compliance_dignity_gap', flag: 'High Compliance, Resident Dignity Gap', desc: 'Passes audit with 5-star compliance, but resident satisfaction of dignity lands in the bottom national quartile.' },
        { key: 'persistent_food_failure', flag: 'Persistent Food Failure', desc: 'Resident satisfaction of food quality sat in the bottom national quartile for two consecutive years (2025 and 2026).' },
        { key: 'understaffed_good_outcomes', flag: 'Understaffed, Good Outcomes', desc: 'Missed target nurse minutes, but manages to secure top-tier clinical quality stars (4-5★).' },
        { key: 'five_star_low_qm', flag: '5-Star Overall, Poor Quality Measures', desc: 'Carries an official 5-star badge, but holds a 1-2 star clinical Quality Measures sub-rating.' }
    ];
    const riskFlags = riskFlagDefinitions.map(r => {
        const count = facilities.filter(f => Boolean(f.flags?.[r.key])).length;
        return { ...r, count, percentage: facilities.length ? (count / facilities.length) * 100 : 0 };
    });

    // Mapping benchmarks to actual records
    const benchmarkNotes = {
        'Anthem': 'Top performer nationally. 16% falls, 0% pressure injuries.',
        'Gibson Street Complex': 'Highest actual clinical outcomes score in Victoria.',
        'Carinity Brownesholme Manor': 'Best actual performer in Queensland.',
        'Romani': 'Highest actual outcomes score in South Australia.',
        'Regents Garden Four Seasons Booragoon': 'Outstanding clinical metrics in Western Australia.',
        'Bishop Davies Court': 'Top performer in Tasmania.',
        'Goodwin Ainslie': 'Highest actual clinical outcomes score in ACT.',
        'Terrace Gardens': 'Best performer in Northern Territory.'
    };

    const hiddenChampionNotes = {
        'Maranatha House': 'Actual outcome composite outranks the vast majority of 4- and 5-star facilities in the country.',
        'Stretton Park': 'Outstanding clinical outcomes despite standard 3★ badge.',
        'Narangba Aged Care': 'Top quartile outcomes on weight loss and restrictive practices.',
        'Largs Bay Aged Care': 'High resident satisfaction and low fall rate.',
        'Agmaroy Nursing Home': 'Excellent medication safety profiles.'
    };

    // =========================================================================
    // 2. FIXED LIGHT THEME
    // Dark-mode toggle removed in v11: the landing page uses a consistent
    // light analytical theme so visitors always see the intended design.
    // =========================================================================
    const htmlElement = document.documentElement;
    const currentTheme = 'light';
    htmlElement.setAttribute('data-theme', currentTheme);

    function getChartThemeColors(theme) {
        const isLight = theme === 'light';
        return {
            text: isLight ? '#0f172a' : '#f8fafc',
            grid: isLight ? 'rgba(15, 23, 42, 0.08)' : 'rgba(248, 250, 252, 0.08)'
        };
    }

    let currentColors = getChartThemeColors(currentTheme);

    function updateChartColors(theme) {
        currentColors = getChartThemeColors(theme);
        
        if (chartMatchedTrend) {
            chartMatchedTrend.options.scales.x.ticks.color = currentColors.text;
            chartMatchedTrend.options.scales.y.ticks.color = currentColors.text;
            chartMatchedTrend.options.scales.y.grid.color = currentColors.grid;
            chartMatchedTrend.options.plugins.legend.labels.color = currentColors.text;
            chartMatchedTrend.update();
        }

        if (chartResDimensions) {
            chartResDimensions.options.scales.x.ticks.color = currentColors.text;
            chartResDimensions.options.scales.x.grid.color = currentColors.grid;
            chartResDimensions.options.scales.y.ticks.color = currentColors.text;
            chartResDimensions.update();
        }

        if (chartStateDivergence) {
            chartStateDivergence.options.scales.x.ticks.color = currentColors.text;
            chartStateDivergence.options.scales.y.ticks.color = currentColors.text;
            chartStateDivergence.options.scales.y.grid.color = currentColors.grid;
            chartStateDivergence.update();
        }

        if (chartRiskFlags) {
            chartRiskFlags.options.plugins.legend.labels.color = currentColors.text;
            chartRiskFlags.update();
        }
    }

    // =========================================================================
    // 3. SCROLL NAVIGATION + MOTION
    // =========================================================================
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (event) => {
            const target = btn.getAttribute('data-tab');
            if (!target) return;
            event.preventDefault();
            document.getElementById(target)?.scrollIntoView({behavior:'smooth', block:'start'});
        });
    });

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {threshold: 0.12});
    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    const progress = document.getElementById('scroll-progress');
    const updateProgress = () => {
        const max = document.documentElement.scrollHeight - window.innerHeight;
        if (progress) progress.style.width = `${max > 0 ? (window.scrollY / max) * 100 : 0}%`;
    };
    window.addEventListener('scroll', updateProgress, {passive:true});
    updateProgress();

    const mobileMenu = document.getElementById('mobile-menu');
    const mobileNav = document.getElementById('mobile-nav');
    mobileMenu?.addEventListener('click', () => mobileNav?.classList.toggle('open'));
    mobileNav?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mobileNav.classList.remove('open')));

    // =========================================================================
    // 4. CHART.JS INITIALIZATIONS
    // =========================================================================

    // --- Chart 1: Matched Trends Bar Chart ---
    const ctxMatched = document.getElementById('chart-matched-trend').getContext('2d');
    const chartMatchedTrend = new Chart(ctxMatched, {
        type: 'bar',
        data: {
            labels: matchedTrends.map(t => t.label),
            datasets: [
                {
                    label: '2024 Stars',
                    data: matchedTrends.map(t => t.val2024),
                    backgroundColor: 'rgba(20, 184, 166, 0.4)',
                    borderColor: '#14b8a6',
                    borderWidth: 1.5,
                    borderRadius: 4
                },
                {
                    label: '2026 Stars',
                    data: matchedTrends.map(t => t.val2026),
                    backgroundColor: '#14b8a6',
                    borderColor: '#0d9488',
                    borderWidth: 1.5,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: currentColors.text, font: { family: 'Plus Jakarta Sans', weight: '500' } }
                },
                tooltip: {
                    callbacks: {
                        afterBody: function(items) {
                            const index = items[0].dataIndex;
                            const change = matchedTrends[index].change;
                            return `Trend Change: ${change >= 0 ? '+' : ''}${change.toFixed(2)}★`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: currentColors.text, font: { family: 'Plus Jakarta Sans', size: 11 } },
                    grid: { display: false }
                },
                y: {
                    min: 0,
                    max: 5,
                    ticks: { color: currentColors.text, stepSize: 1, font: { family: 'Plus Jakarta Sans' } },
                    grid: { color: currentColors.grid }
                }
            }
        }
    });

    // --- Chart 2: Resident Dimensions Horizontal Bar Chart ---
    const ctxRes = document.getElementById('chart-res-dimensions').getContext('2d');
    const chartResDimensions = new Chart(ctxRes, {
        type: 'bar',
        data: {
            labels: residentDimensions.map(d => d.dimension),
            datasets: [{
                label: '% Residents Answering "Always" Satisfied',
                data: residentDimensions.map(d => d.percentage),
                backgroundColor: residentDimensions.map(d => {
                    if (d.type === 'strength') return '#14b8a6';
                    if (d.type === 'weakness') return '#f59e0b';
                    return '#f43f5e';
                }),
                borderRadius: 4,
                borderWidth: 0
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Always Satisfied: ${ctx.raw}%`
                    }
                }
            },
            scales: {
                x: {
                    min: 0,
                    max: 100,
                    ticks: { color: currentColors.text, font: { family: 'Plus Jakarta Sans' } },
                    grid: { color: currentColors.grid }
                },
                y: {
                    ticks: { color: currentColors.text, font: { family: 'Plus Jakarta Sans', weight: '600' } },
                    grid: { display: false }
                }
            }
        }
    });

    // --- Chart 3: State Divergence Bar Chart ---
    const ctxState = document.getElementById('chart-state-divergence').getContext('2d');
    const chartStateDivergence = new Chart(ctxState, {
        type: 'bar',
        data: {
            labels: stateDivergence.map(s => s.state),
            datasets: [{
                label: 'Divergence (Clinical Outcome Rank minus Official Badge Rank)',
                data: stateDivergence.map(s => s.divergence),
                backgroundColor: stateDivergence.map(s => s.divergence >= 0 ? '#14b8a6' : '#f43f5e'),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        afterBody: function(items) {
                            const index = items[0].dataIndex;
                            const d = stateDivergence[index];
                            return `Official Rank: ${d.officialRank}th\nClinical Outcome Rank: ${d.outcomeRank}th`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: currentColors.text, font: { family: 'Plus Jakarta Sans', weight: '600' } },
                    grid: { display: false }
                },
                y: {
                    ticks: { color: currentColors.text, font: { family: 'Plus Jakarta Sans' } },
                    grid: { color: currentColors.grid }
                }
            }
        }
    });

    // --- Chart 4: Risk Flags Doughnut Chart ---
    const ctxRisk = document.getElementById('chart-risk-flags').getContext('2d');
    const chartRiskFlags = new Chart(ctxRisk, {
        type: 'doughnut',
        data: {
            labels: riskFlags.map(r => r.flag),
            datasets: [{
                data: riskFlags.map(r => r.count),
                backgroundColor: [
                    '#f59e0b', // Wattle Gold
                    '#0ea5e9', // Sky Blue
                    '#4f46e5', // Indigo
                    '#14b8a6', // Teal
                    '#f43f5e'  // Coral Red
                ],
                borderWidth: 2,
                borderColor: 'rgba(0,0,0,0.1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: currentColors.text,
                        font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' },
                        boxWidth: 12
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const val = ctx.raw;
                            const pct = riskFlags[ctx.dataIndex].percentage;
                            return ` ${ctx.label}: ${val} records (${pct.toFixed(1)}% of directory)`;
                        }
                    }
                }
            },
            onClick: function(event, elements) {
                if (elements.length) {
                    const idx = elements[0].index;
                    openRiskFacilityModal(riskFlags[idx].key);
                }
            },
            cutout: '65%'
        }
    });

    // =========================================================================
    // 5. RISK EXPLORER + DIRECTORY + REPORT CARD ENGINE
    // =========================================================================
    let activeRiskFilter = null;
    let selectedFacilityKey = null;
    let currentPage = 1;
    const pageSize = 20;

    const searchInput = document.getElementById('directory-search');
    const stateFilter = document.getElementById('directory-state');
    const typeFilter = document.getElementById('directory-type');
    const alignmentFilter = document.getElementById('directory-alignment');
    const ratingFilter = document.getElementById('directory-rating');
    const riskFilter = document.getElementById('directory-risk');
    const sortFilter = document.getElementById('directory-sort');
    const tableBody = document.getElementById('directory-tbody');
    const dirEmptyState = document.getElementById('directory-empty');
    const directoryCount = document.getElementById('directory-count');
    const directoryPagination = document.getElementById('directory-pagination');
    const reportModal = document.getElementById('report-modal');
    const reportModalClose = document.getElementById('report-modal-close');
    const btnClearRisk = document.getElementById('btn-clear-risk');
    const riskCategoryList = document.getElementById('risk-category-list');
    const riskFacilityModal = document.getElementById('risk-facility-modal');
    const riskFacilityClose = document.getElementById('risk-facility-close');
    const riskFacilityTitle = document.getElementById('risk-facility-title');
    const riskFacilitySubtitle = document.getElementById('risk-facility-subtitle');
    const riskFacilitySearch = document.getElementById('risk-facility-search');
    const riskFacilityCount = document.getElementById('risk-facility-count');
    const riskFacilityList = document.getElementById('risk-facility-list');
    let riskModalRecords = [];

    function openRiskFacilityModal(filterKey) {
        const records = filterKey === '__hidden__'
            ? facilities.filter(f => Number(f.is_hidden_champion) === 1)
            : filterKey === '__any__'
            ? facilities.filter(f => f.flags && Object.values(f.flags).some(Boolean))
            : facilities.filter(f => Boolean(f.flags?.[filterKey]));
        riskModalRecords = [...records].sort((a,b) => a.service_name.localeCompare(b.service_name));
        const def = filterKey === '__any__' || filterKey === '__hidden__' ? null : riskFlagDefinitions.find(r => r.key === filterKey);
        if (riskFacilityTitle) riskFacilityTitle.textContent = filterKey === '__hidden__' ? 'Hidden Gems in the Data' : (def ? def.flag : 'Facilities needing a closer look');
        if (riskFacilitySubtitle) riskFacilitySubtitle.textContent = filterKey === '__hidden__' ? `${riskModalRecords.length.toLocaleString()} facilities with a ≤3★ overall badge and top-quartile clinical outcomes in the core 2026 directory.` : (def ? `${riskModalRecords.length.toLocaleString()} records in the interactive 2026 directory. ${def.desc}` : `${riskModalRecords.length.toLocaleString()} records with at least one analyst-defined concern in the interactive 2026 directory.`);
        if (riskFacilitySearch) riskFacilitySearch.value = '';
        renderRiskFacilityList();
        riskFacilityModal?.classList.add('open');
        riskFacilityModal?.setAttribute('aria-hidden','false');
        document.body.classList.add('risk-facility-modal-open');
        window.setTimeout(() => riskFacilitySearch?.focus(), 60);
    }

    function renderRiskFacilityList() {
        if (!riskFacilityList) return;
        const q = String(riskFacilitySearch?.value || '').toLowerCase().trim();
        const rows = riskModalRecords.filter(f => `${f.service_name} ${f.provider_name} ${f.state}`.toLowerCase().includes(q));
        if (riskFacilityCount) riskFacilityCount.textContent = `${rows.length.toLocaleString()} records`;
        riskFacilityList.innerHTML = rows.length ? rows.map(f => {
            const alignment = f.rating_classification || 'Aligned';
            const alignmentClass = alignment.toLowerCase().includes('over') ? 'over' : alignment.toLowerCase().includes('under') ? 'under' : 'aligned';
            return `<div class="risk-facility-row"><div class="risk-facility-main"><strong>${f.service_name}</strong><span>${f.provider_name} · ${f.state}</span></div><span class="star-badge badge-star-${f.overall_stars}">${f.overall_stars}★</span><span class="alignment-pill ${alignmentClass}">${alignment.replace('Potentially ','')}</span><button class="view-btn risk-view-report" data-facility-key="${encodeURIComponent(f.facility_key)}"><i class="fa-solid fa-address-card"></i> View report</button></div>`;
        }).join('') : '<div class="risk-empty">No facility names match this search.</div>';
        riskFacilityList.querySelectorAll('.risk-view-report').forEach(btn => btn.addEventListener('click', () => {
            const key = decodeURIComponent(btn.dataset.facilityKey);
            const facility = facilities.find(f => f.facility_key === key);
            if (facility) { closeRiskFacilityModal(); selectedFacilityKey = facility.facility_key; renderReportCard(facility); openReportModal(); }
        }));
    }
    function closeRiskFacilityModal(){ riskFacilityModal?.classList.remove('open'); riskFacilityModal?.setAttribute('aria-hidden','true'); document.body.classList.remove('risk-facility-modal-open'); }
    riskFacilityClose?.addEventListener('click', closeRiskFacilityModal);
    riskFacilityModal?.querySelector('[data-close-risk]')?.addEventListener('click', closeRiskFacilityModal);
    riskFacilitySearch?.addEventListener('input', renderRiskFacilityList);

    function applyRiskFilter(filterKey) {
        activeRiskFilter = filterKey || null;
        if (riskFilter) riskFilter.value = activeRiskFilter || '';
        currentPage = 1;
        renderDirectory();
    }

    function renderRiskCategoryList() {
        if (!riskCategoryList) return;
        riskCategoryList.innerHTML = riskFlags.map((r, idx) => `
            <button class="risk-category-btn" type="button" data-risk-filter="${r.key}">
                <span class="risk-category-icon risk-icon-${idx}"><i class="fa-solid fa-${idx===0?'triangle-exclamation':idx===1?'shield-heart':idx===2?'utensils':idx===3?'person-circle-exclamation':'star-half-stroke'}"></i></span>
                <span class="risk-category-copy"><strong>${r.flag}</strong><small>${r.count.toLocaleString()} records</small><em>${r.desc}</em></span>
                <i class="fa-solid fa-arrow-right"></i>
            </button>`).join('');
        riskCategoryList.querySelectorAll('[data-risk-filter]').forEach(btn => btn.addEventListener('click', () => openRiskFacilityModal(btn.dataset.riskFilter)));
    }
    renderRiskCategoryList();
    document.querySelectorAll('[data-risk-filter="__any__"]').forEach(btn => btn.addEventListener('click', () => openRiskFacilityModal('__any__')));
document.getElementById('btn-hidden-gems')?.addEventListener('click', () => openRiskFacilityModal('__hidden__'));
document.querySelectorAll('[data-method-tile]').forEach(tile => { tile.addEventListener('click', e => { if (e.target.closest('a')) return; tile.classList.toggle('is-open'); }); tile.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tile.classList.toggle('is-open'); } }); });

    btnClearRisk?.addEventListener('click', () => {
        activeRiskFilter = null; currentPage = 1;
        if (searchInput) searchInput.value=''; if (stateFilter) stateFilter.value=''; if (typeFilter) typeFilter.value='';
        if (alignmentFilter) alignmentFilter.value=''; if (ratingFilter) ratingFilter.value=''; if (riskFilter) riskFilter.value=''; if (sortFilter) sortFilter.value='relevance';
        renderDirectory();
    });
    searchInput?.addEventListener('input', () => { currentPage=1; renderDirectory(); });
    [stateFilter,typeFilter,alignmentFilter,ratingFilter,riskFilter,sortFilter].forEach(el => el?.addEventListener('change', () => { currentPage=1; if(el===riskFilter) activeRiskFilter=riskFilter.value||null; renderDirectory(); }));

    function alignmentInfo(item) {
        const raw = item.rating_classification || 'Aligned';
        const alignment = raw.replace('Potentially ','');
        const cls = raw.toLowerCase().includes('over') ? 'over' : raw.toLowerCase().includes('under') ? 'under' : 'aligned';
        const descriptions = { over:'Badge is stronger than the underlying outcome evidence.', under:'Underlying outcome evidence is stronger than the headline badge.', aligned:'No material badge/outcome divergence identified by this analysis.' };
        return { raw, alignment, cls, desc: descriptions[cls] };
    }

    function keyEvidence(item) {
        const re = item.residents_experience_stars ?? 'N/A';
        const qm = item.quality_measures_stars ?? 'N/A';
        const staffing = item.staffing_stars ?? 'N/A';
        const compliance = item.compliance_stars ?? 'N/A';
        return `RE: ${re}★ · QM: ${qm}★ · Staffing: ${staffing}★ · Compliance: ${compliance}★`;
    }

    function sortFacilities(list) {
        const mode = sortFilter?.value || 'relevance';
        const copy=[...list];
        if(mode==='rating_desc') return copy.sort((a,b)=>(b.overall_stars||0)-(a.overall_stars||0)||a.service_name.localeCompare(b.service_name));
        if(mode==='rating_asc') return copy.sort((a,b)=>(a.overall_stars||0)-(b.overall_stars||0)||a.service_name.localeCompare(b.service_name));
        if(mode==='alignment') { const rank={'Potentially over-rated':0,'Potentially under-rated':1,'Aligned':2}; return copy.sort((a,b)=>(rank[a.rating_classification]??2)-(rank[b.rating_classification]??2)||a.service_name.localeCompare(b.service_name)); }
        if(mode==='resident_desc') return copy.sort((a,b)=>(b.residents_experience_stars||0)-(a.residents_experience_stars||0));
        if(mode==='qm_asc') return copy.sort((a,b)=>(a.quality_measures_stars||0)-(b.quality_measures_stars||0));
        if(mode==='outcome_desc') return copy.sort((a,b)=>(b.outcome_composite||-999)-(a.outcome_composite||-999));
        return copy.sort((a,b)=>a.service_name.localeCompare(b.service_name));
    }

    function renderPagination(total) {
        if (!directoryPagination) return;
        const pages=Math.max(1,Math.ceil(total/pageSize));
        if(currentPage>pages) currentPage=pages;
        let html=`<button type="button" class="page-btn" data-page="prev" ${currentPage===1?'disabled':''}><i class="fa-solid fa-chevron-left"></i></button>`;
        const start=Math.max(1,currentPage-2), end=Math.min(pages,start+4);
        for(let p=start;p<=end;p++) html+=`<button type="button" class="page-btn ${p===currentPage?'active':''}" data-page="${p}">${p}</button>`;
        if(end<pages) html+=`<span class="page-ellipsis">…</span><button type="button" class="page-btn" data-page="${pages}">${pages}</button>`;
        html+=`<button type="button" class="page-btn" data-page="next" ${currentPage===pages?'disabled':''}><i class="fa-solid fa-chevron-right"></i></button>`;
        directoryPagination.innerHTML=html;
        directoryPagination.querySelectorAll('.page-btn:not([disabled])').forEach(btn=>btn.addEventListener('click',()=>{ const p=btn.dataset.page; if(p==='prev') currentPage--; else if(p==='next') currentPage++; else currentPage=Number(p); renderDirectory(); document.getElementById('facility-spotlights')?.scrollIntoView({behavior:'smooth',block:'start'}); }));
    }

    function renderDirectory() {
        const normalize=value=>String(value??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();
        const query=normalize(searchInput?.value); const selectedState=stateFilter?.value||''; const selectedType=typeFilter?.value||''; const selectedAlignment=alignmentFilter?.value||''; const selectedRating=ratingFilter?.value||''; const selectedRisk=riskFilter?.value||'';
        let filtered=facilities;
        filtered=filtered.filter(item=>{
            const haystack=[item.service_name,item.provider_name,item.state,item.provider_type,item.facility_key].map(normalize).join(' | ');
            const matchesQuery=!query||haystack.includes(query); const matchesState=!selectedState||item.state===selectedState; const matchesType=!selectedType||item.provider_type===selectedType; const matchesAlignment=!selectedAlignment||item.rating_classification===selectedAlignment; const matchesRating=!selectedRating||String(item.overall_stars)===selectedRating;
            const matchesRisk=!selectedRisk || (selectedRisk==='__any__' ? Object.values(item.flags||{}).some(Boolean) : Boolean(item.flags?.[selectedRisk]));
            return matchesQuery&&matchesState&&matchesType&&matchesAlignment&&matchesRating&&matchesRisk;
        });
        filtered=sortFacilities(filtered);
        const total=filtered.length; const pages=Math.max(1,Math.ceil(total/pageSize)); if(currentPage>pages) currentPage=pages; const start=(currentPage-1)*pageSize; const displayList=filtered.slice(start,start+pageSize);
        if(directoryCount) directoryCount.textContent=`${total.toLocaleString()} records${total!==1?'':''} · showing ${total?start+1:0}–${Math.min(start+pageSize,total)}`;
        tableBody.innerHTML='';
        if(!total){ dirEmptyState.style.display='block'; renderPagination(0); return; }
        dirEmptyState.style.display='none';
        displayList.forEach(item=>{
            const tr=document.createElement('tr'); if(item.facility_key===selectedFacilityKey) tr.className='selected';
            const starClass=item.overall_stars===5?'badge-star-5':item.overall_stars===4?'badge-star-4':item.overall_stars===3?'badge-star-3':item.overall_stars===2?'badge-star-2':'badge-star-1';
            const a=alignmentInfo(item);
            tr.innerHTML=`<td><div class="facility-name-cell">${item.service_name}</div><div class="facility-provider-cell">${item.provider_name}</div></td><td><span class="state-badge">${item.state}</span></td><td><span class="star-badge ${starClass}">${item.overall_stars}★</span></td><td><span class="alignment-pill ${a.cls}">${a.alignment}</span></td><td><div class="facility-evidence">${keyEvidence(item)}</div></td><td><button class="view-btn"><i class="fa-solid fa-file-lines"></i> View Report</button></td>`;
            const openFacility=()=>{selectedFacilityKey=item.facility_key; tableBody.querySelectorAll('tr').forEach(r=>r.classList.remove('selected')); tr.classList.add('selected'); renderReportCard(item); openReportModal();};
            tr.addEventListener('click',openFacility); tr.querySelector('.view-btn')?.addEventListener('click',e=>{e.stopPropagation();openFacility();}); tableBody.appendChild(tr);
        });
        renderPagination(total);
    }
    // Render the report card inside report-card-panel
    function renderReportCard(facility) {
        const panel = document.getElementById('report-card-panel');
        if (!panel) return;

        // Build Stars Helper
        const getStarsHTML = (rating) => {
            if (rating === null || rating === undefined) return '<span style="color:var(--text-muted)">N/A</span>';
            let starsStr = '';
            for (let i = 1; i <= 5; i++) {
                if (i <= rating) {
                    starsStr += '<i class="fa-solid fa-star"></i>';
                } else {
                    starsStr += '<i class="fa-regular fa-star" style="opacity: 0.35;"></i>';
                }
            }
            return starsStr;
        };

        // Class helpers for provider
        const providerClass = facility.provider_type === 'Government' ? 'provider-gov' : 
                              facility.provider_type === 'Not for Profit' ? 'provider-nfp' : 'provider-pfp';

        // Check if care minutes pass targets
        const rnMinutesVal = facility.rn_minutes_actual !== null ? facility.rn_minutes_actual : 'N/A';
        const rnTargetVal = facility.rn_minutes_target !== null ? facility.rn_minutes_target : 'N/A';
        const totalMinutesVal = facility.total_care_minutes_actual !== null ? facility.total_care_minutes_actual : 'N/A';
        const totalTargetVal = facility.total_care_minutes_target !== null ? facility.total_care_minutes_target : 'N/A';

        const rnClass = facility.met_rn_target === 1 ? 'minutes-pass' : 'minutes-fail';
        const totalClass = facility.met_total_care_target === 1 ? 'minutes-pass' : 'minutes-fail';
        const safeNum = v => typeof v === 'number' && Number.isFinite(v) ? v : null;
        const rnActual = safeNum(facility.rn_minutes_actual), rnTarget = safeNum(facility.rn_minutes_target);
        const totalActual = safeNum(facility.total_care_minutes_actual), totalTarget = safeNum(facility.total_care_minutes_target);
        const pctWidth = (actual,target) => actual !== null && target && target > 0 ? Math.min(150, Math.max(0, (actual/target)*100)) : 0;
        const rnStatus = facility.met_rn_target === 1 ? 'Above target' : 'Below target';
        const totalStatus = facility.met_total_care_target === 1 ? 'Above target' : 'Below target';

        // Quality measures percentages
        const formatPct = (val) => val !== null ? `${val.toFixed(1)}%` : 'N/A';

        // Render risk flags HTML
        let flagsHTML = '';
        let activeFlagsCount = 0;
        const flagExplanations = {
            adequately_staffed_poor_outcomes: '<strong>Adequately Staffed, Poor Outcomes</strong>: Met RN targets but clinical outcomes remain low (1-2★ Quality Measures).',
            high_compliance_dignity_gap: '<strong>Compliance Dignity Disconnect</strong>: Passes audit with 5-star compliance, but resident satisfaction is in the bottom national quartile.',
            persistent_food_failure: '<strong>Persistent Food Failure</strong>: Resident experience food score sat in the bottom national quartile in both 2025 and 2026.',
            understaffed_good_outcomes: '<strong>Understaffed, Good Outcomes</strong>: Missed RN care minutes but secures 4-5★ Quality Measures.',
            five_star_low_qm: '<strong>Badge/Clinical Conflict</strong>: Carries an official 5-star overall rating alongside a failing 1-2 star Quality Measures rating.'
        };

        if (facility.flags) {
            Object.keys(flagExplanations).forEach(key => {
                if (Boolean(facility.flags[key])) {
                    activeFlagsCount++;
                    const isSevere = key === 'five_star_low_qm' || key === 'persistent_food_failure';
                    flagsHTML += `
                        <div class="report-concern-card ${isSevere ? 'severe' : ''}">
                            <div class="report-concern-icon"><i class="fa-solid ${isSevere ? 'fa-triangle-exclamation' : 'fa-magnifying-glass-chart'}"></i></div>
                            <div class="report-concern-copy">${flagExplanations[key]}</div>
                            <span class="report-concern-label">Review</span>
                        </div>
                    `;
                }
            });
        }

        if (activeFlagsCount === 0) {
            flagsHTML = `
                <div class="report-clear-state">
                    <div class="report-clear-orb"><i class="fa-solid fa-sparkles"></i></div>
                    <div><strong>No screening concerns identified</strong><span>No analyst-defined concern is active for this facility in the 2026 core records.</span></div>
                </div>
            `;
        }

        // Resident Lived Experience Dimensions (12 dimensions)
        let reDimensionsHTML = '';
        if (facility.re_dimensions) {
            reDimensionsHTML = '<div class="report-outcomes-grid" style="grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-top:0.75rem;">';
            Object.keys(facility.re_dimensions).forEach(dimName => {
                const val = facility.re_dimensions[dimName];
                const valText = val !== null ? `${val.toFixed(0)}% Always` : 'N/A';
                
                // Color code food
                const isFood = dimName.toLowerCase().includes('food');
                const textStyle = isFood && val < 30 ? 'color: var(--accent-danger); font-weight: 700;' : '';

                reDimensionsHTML += `
                    <div style="background: rgba(0,0,0,0.08); padding: 0.5rem; border-radius: 4px; font-size: 0.8rem; border:1px solid var(--card-border);">
                        <div style="color: var(--text-muted); font-size: 0.7rem; font-weight:600;">${dimName}</div>
                        <div style="${textStyle}">${valText}</div>
                    </div>
                `;
            });
            reDimensionsHTML += '</div>';
        } else {
            reDimensionsHTML = '<p style="font-size:0.85rem; color:var(--text-muted);">Lived experience survey detail not available for this facility.</p>';
        }

        panel.innerHTML = `
            <div class="report-hero">
                <div class="report-hero-image"><img src="images/facility_human_care.jpg" alt="Aged care resident and care worker"></div>
                <div class="report-hero-copy">
                    <span class="section-kicker">2026 FACILITY REPORT</span>
                    <div class="report-title">${facility.service_name}</div>
                    <div class="report-provider">${facility.provider_name}</div>
                    <div class="report-meta"><span class="state-badge">${facility.state}</span><span class="provider-badge ${providerClass}">${facility.provider_type}</span><span class="size-badge"><i class="fa-solid fa-users"></i> ${facility.size || 'Medium'} size</span></div>
                </div>
                <div class="report-hero-rating"><span>Overall badge</span><strong>${facility.overall_stars}★</strong><em class="${alignmentInfo(facility).cls}">${alignmentInfo(facility).alignment}</em></div>
            </div>

            <!-- STAR SUB-RATINGS -->
            <div class="report-section-title">
                <i class="fa-solid fa-star"></i> Regulatory Star Ratings
            </div>
            <div class="report-stars-grid">
                <div class="report-star-row" style="background: var(--color-gov-bg); border-color: rgba(20, 184, 166, 0.25);">
                    <span class="report-star-label" style="color:var(--text-primary); font-weight:700;">Overall Rating Badge</span>
                    <span class="report-star-stars" style="color:var(--accent-primary); font-size: 1.1rem;">${getStarsHTML(facility.overall_stars)}</span>
                </div>
                <div class="report-star-row">
                    <span class="report-star-label">Residents' Experience</span>
                    <span class="report-star-stars">${getStarsHTML(facility.residents_experience_stars)}</span>
                </div>
                <div class="report-star-row">
                    <span class="report-star-label">Clinical Quality Measures</span>
                    <span class="report-star-stars">${getStarsHTML(facility.quality_measures_stars)}</span>
                </div>
                <div class="report-star-row">
                    <span class="report-star-label">Staffing Level Stars</span>
                    <span class="report-star-stars">${getStarsHTML(facility.staffing_stars)}</span>
                </div>
                <div class="report-star-row">
                    <span class="report-star-label">Compliance Audit Rating</span>
                    <span class="report-star-stars">${getStarsHTML(facility.compliance_stars)}</span>
                </div>
            </div>

            <!-- STAFFING MINUTES -->
            <div class="report-section-title">
                <i class="fa-solid fa-clock"></i> Care Minutes Compliance
            </div>
            <div class="report-minutes-grid">
                <div class="report-minute-card ${rnClass}">
                    <div class="minute-topline"><span class="report-minute-title">RN Care Minutes</span><span class="minute-status">${rnStatus}</span></div>
                    <div class="minute-values"><strong>${rnMinutesVal}m</strong><span>target ${rnTargetVal}m</span></div>
                    <div class="minute-track"><span style="width:${pctWidth(rnActual,rnTarget)}%"></span><b style="left:100%"></b></div>
                    <small>${rnActual !== null && rnTarget !== null ? `${Math.abs(rnActual-rnTarget).toFixed(0)} minutes ${rnActual >= rnTarget ? 'above' : 'below'} target` : 'Target comparison unavailable'}</small>
                </div>
                <div class="report-minute-card ${totalClass}">
                    <div class="minute-topline"><span class="report-minute-title">Total Care Minutes</span><span class="minute-status">${totalStatus}</span></div>
                    <div class="minute-values"><strong>${totalMinutesVal}m</strong><span>target ${totalTargetVal}m</span></div>
                    <div class="minute-track"><span style="width:${pctWidth(totalActual,totalTarget)}%"></span><b style="left:100%"></b></div>
                    <small>${totalActual !== null && totalTarget !== null ? `${Math.abs(totalActual-totalTarget).toFixed(0)} minutes ${totalActual >= totalTarget ? 'above' : 'below'} target` : 'Target comparison unavailable'}</small>
                </div>
            </div>

            <!-- CLINICAL OUTCOMES -->
            <div class="report-section-title">
                <i class="fa-solid fa-heart-pulse"></i> Clinical Quality Measures (Actual %)
            </div>
            <div class="report-outcomes-grid">
                <div class="report-outcome-card">
                    <div class="report-outcome-title">Falls Rate</div>
                    <div class="report-outcome-value">${formatPct(facility.pct_falls)}</div>
                </div>
                <div class="report-outcome-card">
                    <div class="report-outcome-title">Pressure Injuries</div>
                    <div class="report-outcome-value">${formatPct(facility.pct_pressure_injuries)}</div>
                </div>
                <div class="report-outcome-card">
                    <div class="report-outcome-title">Unplanned Weight Loss</div>
                    <div class="report-outcome-value">${formatPct(facility.pct_unplanned_weight_loss)}</div>
                </div>
                <div class="report-outcome-card">
                    <div class="report-outcome-title">Polypharmacy</div>
                    <div class="report-outcome-value">${formatPct(facility.pct_polypharmacy)}</div>
                </div>
                <div class="report-outcome-card">
                    <div class="report-outcome-title">Antipsychotic Use</div>
                    <div class="report-outcome-value">${formatPct(facility.pct_antipsychotic)}</div>
                </div>
                <div class="report-outcome-card">
                    <div class="report-outcome-title">Restrictive Practices</div>
                    <div class="report-outcome-value">${formatPct(facility.pct_restrictive_practices)}</div>
                </div>
            </div>

            <!-- AUDIT & VERDICT FLAGS -->
            <div class="report-section-title">
                <i class="fa-solid fa-triangle-exclamation"></i> Audit Risk Indicators
            </div>
            <div class="report-flags-container">
                ${flagsHTML}
            </div>

            <!-- LIVED SURVEY DIMENSIONS -->
            <div class="report-section-title" style="margin-top: 1.5rem;">
                <i class="fa-solid fa-clipboard-question"></i> Lived Resident Satisfaction (12 Dimensions)
            </div>
            ${reDimensionsHTML}
        `;
    }

    // =========================================================================
    // 6. INITIAL LOAD & PRE-SELECTION (HAMMONDCARE - HORSLEY DEFAULT)
    // =========================================================================
    
    // Default selection matching published Tableau parameter 1065183447068675
    // "HammondCare - Horsley" in NSW
    const defaultSelection = facilities.find(f => 
        f.service_name.toLowerCase().includes("hammondcare - horsley") ||
        f.facility_key.toLowerCase().includes("hammondcare - horsley")
    ) || facilities[0];

    if (defaultSelection) {
        selectedFacilityKey = defaultSelection.facility_key;
    }

    function openReportModal() {
        if (!reportModal) return;
        reportModal.classList.add('open');
        reportModal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('report-modal-open');
        window.setTimeout(() => reportModalClose?.focus(), 60);
    }

    function closeReportModal() {
        if (!reportModal) return;
        reportModal.classList.remove('open');
        reportModal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('report-modal-open');
    }

    reportModalClose?.addEventListener('click', closeReportModal);
    reportModal?.querySelector('[data-close-report]')?.addEventListener('click', closeReportModal);
    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        if (riskFacilityModal?.classList.contains('open')) { closeRiskFacilityModal(); return; }
        if (reportModal?.classList.contains('open')) closeReportModal();
    });

    const dignityGapCount = riskFlags.find(r => r.key === 'high_compliance_dignity_gap')?.count ?? 0;
    const recommendationDetails = {
        provider: { kicker:'01 · PROVIDERS', title:'Improve care quality where it matters most', text:'Use staffing as a resourcing diagnostic, but do not treat care minutes as a proxy for safety. For weak-rated services, pair staffing gaps with Quality Measures and resident experience before deciding where improvement effort should go.', metrics:[['56.9%','≤3★ facilities where Staffing is the weakest link'],['-0.48★','Matched Quality Measures change, 2024→2026']] },
        auditor: { kicker:'02 · AUDITORS', title:'Look beyond compliance', text:'A compliance pass can coexist with weak lived experience. Review the underlying Quality Measures, resident-experience dimensions and analyst-defined risk signals alongside the official badge.', metrics:[['0.028','Compliance ↔ resident dignity correlation'],[dignityGapCount.toLocaleString(),'High-compliance / dignity-gap facilities in the directory']] },
        families: { kicker:'03 · FAMILIES', title:'Look beyond the overall badge', text:'Use the overall star as a starting point. Ask about clinical Quality Measures, resident experience, staffing and facility-specific signals—especially when comparing otherwise similar services.', metrics:[['71.9%','Facilities at 4★ in 2026'],['28.2%','Residents reporting food quality “Always”']] },
        leaders: { kicker:'04 · SECTOR LEADERS', title:'Turn weak links into improvement priorities', text:'The analysis suggests targeted learning opportunities: investigate common weak links, compare state divergence, and study Hidden Champions whose underlying outcomes outperform their headline badge.', metrics:[['47','Hidden Champions'],['+0.21★','Matched overall improvement, 2024→2026']] },
        policy: { kicker:'05 · POLICYMAKERS', title:'Align oversight with real outcomes', text:'The strongest policy lesson is not that the rating system is wrong, but that a single badge can hide meaningful variation. Outcome measures and lived experience add useful context for oversight and transparency.', metrics:[['2,180','Facilities with complete 2026 ratings'],['84%','Share of facilities with a complete 2026 rating']] }
    };
    const recDetail = document.getElementById('recommendation-detail');
    document.querySelectorAll('.recommendation-card').forEach(card => card.addEventListener('click', () => {
        const d = recommendationDetails[card.dataset.rec];
        if (!d) return;
        document.getElementById('rec-detail-kicker').textContent = d.kicker;
        document.getElementById('rec-detail-title').textContent = d.title;
        document.getElementById('rec-detail-text').textContent = d.text;
        document.getElementById('rec-detail-metrics').innerHTML = d.metrics.map(m => `<div><strong>${m[0]}</strong><span>${m[1]}</span></div>`).join('');
        recDetail?.classList.add('active');
        recDetail?.scrollIntoView({behavior:'smooth', block:'center'});
    }));

    setActiveTabBtn(btnAll);
    renderDirectory();
    updateChartColors(currentTheme);
});
