const $ = s => document.querySelector(s);
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let projects = [];
let current = -1;

/* ---------- intro ---------- */
function hideIntro() { $("#intro").classList.add("gone"); }
setTimeout(hideIntro, 3600);
$("#intro").addEventListener("click", hideIntro);

/* ---------- load + render ---------- */
async function init() {
    let data = { site: {}, projects: [] };
    try { data = await (await fetch("/api/projects", { cache: "no-store" })).json(); }
    catch (e) { console.error("Could not load projects", e); }
    const s = data.site || {};
    if (s.eyebrow) $("#eyebrow").textContent = s.eyebrow;
    if (s.title) { $("#title").textContent = s.title; document.title = s.title; }
    if (s.subtitle) $("#subtitle").textContent = s.subtitle;
    projects = Array.isArray(data.projects) ? data.projects : [];
    $("#count").textContent = String(projects.length).padStart(2, "0") + " PROJECTS";
    renderCards();
}

function artHtml(p) {
    const img = p.image ? `style="background-image:url('${esc(p.image).replace(/'/g, "%27")}')"` : "";
    return `<div class="art" ${img}>${p.image ? "" : `<span class="glyph">${esc(p.glyph || "\u2726")}</span>`}</div>`;
}
function accentStyle(p) {
    const a = Array.isArray(p.accent) && p.accent.length > 1 ? p.accent : ["#7c5cff", "#00d4ff"];
    return `--a:${esc(a[0])};--b:${esc(a[1])}`;
}

function renderCards() {
    const wrap = $("#cards");
    wrap.innerHTML = "";
    projects.forEach((p, i) => {
        const card = document.createElement("article");
        card.className = "card";
        card.style.cssText = accentStyle(p) + `;animation-delay:${3.1 + i * 0.12}s`;
        card.tabIndex = 0;
        card.innerHTML = `<div class="card-in">${artHtml(p)}<div class="spot"></div>
            <div class="card-text"><div class="num">${String(i + 1).padStart(2, "0")} &nbsp;&middot;&nbsp; ${esc(p.tag || "")}</div>
            <h3>${esc(p.name)}</h3><p>${esc(p.summary || "")}</p>
            <span class="open">EXPLORE <b>&rarr;</b></span></div></div>`;
        card.addEventListener("click", () => openProject(i));
        card.addEventListener("keydown", e => { if (e.key === "Enter") openProject(i); });
        card.addEventListener("mousemove", e => {
            const r = card.getBoundingClientRect();
            const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
            card.style.setProperty("--ry", ((x - .5) * 9).toFixed(2) + "deg");
            card.style.setProperty("--rx", ((.5 - y) * 9).toFixed(2) + "deg");
            card.style.setProperty("--mx", (x * 100) + "%");
            card.style.setProperty("--my", (y * 100) + "%");
        });
        card.addEventListener("mouseleave", () => { card.style.setProperty("--rx", "0deg"); card.style.setProperty("--ry", "0deg"); });
        wrap.appendChild(card);
    });
}

/* ---------- detail view ---------- */
function openProject(i) {
    if (!projects.length) return;
    current = (i + projects.length) % projects.length;
    const p = projects[current];
    const sections = (p.details || []).map(d =>
        `<div class="d-sec"><h4>${esc(d.heading)}</h4><p>${esc(d.text)}</p></div>`).join("");
    $("#detail-body").innerHTML = `<div class="d-wrap" style="${accentStyle(p)}">
        <div class="d-banner">${artHtml(p)}<div class="d-title"><div class="d-tag">${esc((p.tag || "").toUpperCase())}</div><h2>${esc(p.name)}</h2></div></div>
        <p class="d-sub">${esc(p.summary || "")}</p>
        ${p.interactive === "magic" ? '<div class="magic" id="magic"></div>' : ""}
        <div class="d-sections">${sections}</div></div>`;
    $("#detail-body").scrollTop = 0;
    $("#detail").classList.add("open");
    $("#detail").setAttribute("aria-hidden", "false");
    document.body.classList.add("locked");
    if (p.interactive === "magic") magicStart();
}
function closeProject() {
    $("#detail").classList.remove("open");
    $("#detail").setAttribute("aria-hidden", "true");
    document.body.classList.remove("locked");
}
$("#back").addEventListener("click", closeProject);
$("#prev").addEventListener("click", () => openProject(current - 1));
$("#next").addEventListener("click", () => openProject(current + 1));
document.addEventListener("keydown", e => {
    if (!$("#detail").classList.contains("open")) return;
    if (e.key === "Escape") closeProject();
    if (e.key === "ArrowLeft") openProject(current - 1);
    if (e.key === "ArrowRight") openProject(current + 1);
});

/* ---------- Magical Number (1-63, six cards) ---------- */
const BITS = [1, 2, 4, 8, 16, 32];
let mStep = 0, mTotal = 0, mYes = [];

function magicCard(bit) {
    const nums = [];
    for (let n = 1; n <= 63; n++) if (n & bit) nums.push(n);
    return nums;
}
function magicStart() {
    mStep = 0; mTotal = 0; mYes = [];
    $("#magic").innerHTML = `<div class="m-kicker">MIND READER</div>
        <h3 class="m-big">Think of a number</h3>
        <p class="m-text">Choose any number between 1 and 63 and keep it secret. I will show you six cards. Tell me whether your number is on each one, and I will read your mind.</p>
        <button class="m-btn" id="m-begin">I'M READY</button>`;
    $("#m-begin").addEventListener("click", magicAsk);
}
function magicAsk() {
    const bit = BITS[mStep];
    const dots = BITS.map((_, i) => `<i class="${i <= mStep ? "on" : ""}"></i>`).join("");
    const cells = magicCard(bit).map(n => `<span>${n}</span>`).join("");
    $("#magic").innerHTML = `<div class="m-kicker">CARD ${mStep + 1} OF 6</div><div class="m-prog">${dots}</div>
        <div class="m-card">${cells}</div>
        <p class="m-q">Is your number on this card?</p>
        <div class="m-row"><button class="m-btn" id="m-yes">YES</button><button class="m-btn ghost" id="m-no">NO</button></div>`;
    $("#m-yes").addEventListener("click", () => magicAnswer(true));
    $("#m-no").addEventListener("click", () => magicAnswer(false));
}
function magicAnswer(yes) {
    if (yes) { mTotal += BITS[mStep]; mYes.push(BITS[mStep]); }
    mStep++;
    if (mStep < BITS.length) magicAsk(); else magicReveal();
}
function magicReveal() {
    const chips = mYes.length ? mYes.map(v => `<b>${v}</b>`).join("") : "<b>0</b>";
    $("#magic").innerHTML = `<div class="m-kicker">YOUR NUMBER IS</div>
        <div class="m-result" id="m-result">0</div>
        <p class="m-how">The first number on each card is a power of two: 1, 2, 4, 8, 16 and 32. Add up the cards you said yes to and you get your number.
        <span class="m-chips">${chips}</span></p>
        <button class="m-btn" id="m-again">PLAY AGAIN</button>`;
    $("#m-again").addEventListener("click", magicStart);
    const out = $("#m-result"), target = mTotal, t0 = performance.now(), dur = 1400;
    const tick = now => {
        const k = Math.min(1, (now - t0) / dur);
        out.textContent = k < 1 ? Math.floor(Math.random() * 63) + 1 : target;
        if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

init();
