:root {
    --red: #d5202f;
    --red-dark: #981b25;
    --ink: #101828;
    --muted: #667085;
    --panel: rgba(255,255,255,0.92);
    --line: #eaecf0;
    --soft: #f8fafc;
    --white: #ffffff;
    --shadow: 0 24px 70px rgba(16, 24, 40, 0.12);
    --shadow-soft: 0 12px 34px rgba(16, 24, 40, 0.08);
    --radius: 24px;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: Inter, Segoe UI, Arial, Helvetica, sans-serif;
    background:
        radial-gradient(circle at 10% 5%, rgba(213,32,47,0.16), transparent 30%),
        radial-gradient(circle at 88% 12%, rgba(16,24,40,0.12), transparent 28%),
        linear-gradient(135deg, #f7f8fb 0%, #eef2f7 100%);
    color: var(--ink);
}

.app-shell {
    display: grid;
    grid-template-columns: 310px 1fr;
    min-height: 100vh;
}

.sidebar {
    background:
        linear-gradient(180deg, rgba(255,255,255,0.08), transparent 22%),
        linear-gradient(180deg, #111827 0%, #080b12 100%);
    color: white;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 26px;
    position: sticky;
    top: 0;
    height: 100vh;
    box-shadow: 18px 0 50px rgba(16,24,40,0.16);
}

.brand {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 14px;
    align-items: center;
}

.logo-card {
    background: white;
    border-radius: 22px;
    padding: 8px;
    box-shadow: 0 16px 35px rgba(0,0,0,0.28);
}

.logo-card img {
    width: 100%;
    border-radius: 15px;
    display: block;
}

.brand h1 {
    font-size: 22px;
    line-height: 1.04;
    margin: 0;
    letter-spacing: -0.02em;
}

.brand p {
    margin: 8px 0 0;
    color: #d0d5dd;
    font-size: 13px;
}

.menu { display: grid; gap: 10px; }

.menu a {
    color: white;
    text-decoration: none;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.09);
    padding: 14px 16px;
    border-radius: 16px;
    font-weight: 800;
    transition: 0.18s ease;
}

.menu a:hover {
    background: linear-gradient(135deg, var(--red), var(--red-dark));
    transform: translateX(4px);
    box-shadow: 0 12px 28px rgba(213,32,47,0.3);
}

.menu .exit-link { background: rgba(213,32,47,0.2); }

.sidebar-footer {
    margin-top: auto;
    display: grid;
    gap: 5px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 16px;
    border-radius: 18px;
    font-size: 13px;
    color: #e5e7eb;
}

.sidebar-footer strong { color: white; font-size: 19px; }

.content { padding: 28px; min-width: 0; }

.topbar {
    background: rgba(255,255,255,0.76);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.86);
    border-radius: var(--radius);
    box-shadow: var(--shadow-soft);
    padding: 22px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 26px;
    gap: 18px;
}

.eyebrow {
    color: var(--red);
    text-transform: uppercase;
    letter-spacing: 0.10em;
    font-weight: 900;
    font-size: 12px;
}

.topbar h2 {
    margin: 6px 0 0;
    font-size: 34px;
    letter-spacing: -0.04em;
}

.top-action,
button {
    background: linear-gradient(135deg, var(--red), var(--red-dark));
    color: white;
    border: 0;
    border-radius: 15px;
    padding: 13px 18px;
    font-weight: 900;
    text-decoration: none;
    cursor: pointer;
    box-shadow: 0 14px 28px rgba(213,32,47,0.26);
    white-space: nowrap;
}

.top-action:hover,
button:hover { filter: brightness(0.96); transform: translateY(-1px); }

.hero {
    background:
        radial-gradient(circle at 92% 20%, rgba(255,255,255,0.18), transparent 24%),
        linear-gradient(135deg, #121826 0%, #2b3343 58%, #d5202f 100%);
    color: white;
    border-radius: 32px;
    padding: 32px;
    display: grid;
    grid-template-columns: 1fr 190px;
    gap: 24px;
    align-items: center;
    box-shadow: var(--shadow);
    margin-bottom: 22px;
    overflow: hidden;
}

.hero h3 {
    font-size: 38px;
    line-height: 1.04;
    margin: 14px 0 12px;
    max-width: 820px;
    letter-spacing: -0.04em;
}

.hero p { color: #eef2f6; margin: 0; font-size: 16px; max-width: 760px; }
.hero img { width: 190px; border-radius: 28px; background: white; padding: 8px; }

.badge {
    display: inline-flex;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 999px;
    padding: 8px 12px;
    font-weight: 900;
    font-size: 13px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(160px, 1fr));
    gap: 18px;
    margin-bottom: 22px;
}

.stats-grid.small-gap { margin-top: -6px; }

.stat-card {
    background: var(--panel);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow-soft);
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: "";
    width: 10px;
    height: 56px;
    background: linear-gradient(180deg, var(--red), var(--red-dark));
    border-radius: 20px;
    position: absolute;
    top: 20px;
    right: 20px;
}

.stat-card.soft::before { background: linear-gradient(180deg, #344054, #101828); }
.stat-card.accent::before { background: linear-gradient(180deg, #ffb020, #d5202f); }

.stat-card span {
    display: block;
    color: var(--muted);
    font-weight: 800;
    margin-bottom: 12px;
}

.stat-card strong { font-size: 31px; letter-spacing: -0.04em; }
.money strong, .accent strong { color: var(--red); }

.grid-2 {
    display: grid;
    grid-template-columns: 1.25fr 0.75fr;
    gap: 22px;
}

.panel {
    background: var(--panel);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: var(--radius);
    padding: 22px;
    box-shadow: var(--shadow-soft);
    margin-bottom: 22px;
}

.highlight-panel {
    background:
        linear-gradient(135deg, rgba(213,32,47,0.05), rgba(255,255,255,0.92)),
        var(--panel);
}

.narrow { max-width: 680px; }

.panel-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 18px;
}

.panel-head h3 { margin: 0; font-size: 23px; letter-spacing: -0.03em; }
.panel-head a { color: var(--red); font-weight: 900; text-decoration: none; }
.subtext, .help-text { color: var(--muted); margin: 7px 0 0; font-size: 14px; }

.table-wrap { width: 100%; overflow-x: auto; }

table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 780px; }

th {
    background: #f3f5f8;
    color: #475467;
    text-align: left;
    padding: 13px 12px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.055em;
    white-space: nowrap;
}

td {
    padding: 14px 12px;
    border-bottom: 1px solid var(--line);
    vertical-align: top;
}

tr:hover td { background: #fbfcfe; }

.form-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(170px, 1fr));
    gap: 16px;
    align-items: end;
}

.form-grid-large { grid-template-columns: repeat(3, minmax(190px, 1fr)); }
.form-vertical { display: grid; gap: 12px; }
.full { grid-column: 1 / -1; }

label {
    display: block;
    font-weight: 900;
    margin-bottom: 8px;
    color: #344054;
}

input, select, textarea {
    width: 100%;
    border: 1px solid #d0d5dd;
    background: white;
    border-radius: 14px;
    padding: 13px 14px;
    font-size: 15px;
    outline: none;
    transition: 0.16s ease;
}

textarea { min-height: 92px; resize: vertical; }
input:focus, select:focus, textarea:focus {
    border-color: var(--red);
    box-shadow: 0 0 0 4px rgba(213,32,47,0.12);
}

.calc-card {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    padding: 16px;
    border-radius: 20px;
    background: #101828;
    color: white;
}

.calc-card div {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 15px;
}

.calc-card span { display: block; color: #d0d5dd; font-weight: 800; margin-bottom: 8px; }
.calc-card strong { font-size: 26px; letter-spacing: -0.04em; }

.actions { display: flex; gap: 10px; align-items: center; white-space: nowrap; }
.actions a, .cancel {
    color: var(--red);
    font-weight: 900;
    text-decoration: none;
}
.actions .danger { color: #b42318; }
.cancel { display: inline-block; margin-top: 4px; }

.worker-list { display: grid; gap: 12px; }
.worker-item {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 15px;
    border: 1px solid var(--line);
    border-radius: 18px;
    background: #fff;
}
.worker-item span { display: block; color: var(--muted); font-size: 13px; margin-top: 5px; }
.worker-item b { color: var(--red); white-space: nowrap; }
.empty { color: var(--muted); }

.notice, .flash {
    border-radius: 18px;
    padding: 14px 16px;
    background: #fff7e6;
    border: 1px solid #fedf89;
    color: #7a4b00;
    font-weight: 800;
}

.flash-wrap { display: grid; gap: 10px; margin-bottom: 18px; }
.flash.ok { background: #ecfdf3; border-color: #abefc6; color: #067647; }
.exit-panel { text-align: center; padding: 42px; }
.exit-panel h3 { font-size: 30px; margin-top: 0; }

@media (max-width: 1100px) {
    .app-shell { grid-template-columns: 1fr; }
    .sidebar { position: relative; height: auto; }
    .menu { grid-template-columns: repeat(2, 1fr); }
    .hero, .grid-2 { grid-template-columns: 1fr; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .form-grid, .form-grid-large { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 720px) {
    .content, .sidebar { padding: 16px; }
    .topbar { align-items: flex-start; flex-direction: column; }
    .topbar h2 { font-size: 28px; }
    .hero { padding: 24px; }
    .hero h3 { font-size: 30px; }
    .hero img { display: none; }
    .stats-grid, .form-grid, .form-grid-large, .calc-card, .menu { grid-template-columns: 1fr; }
}

.ok-card strong { color: #067647; }
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 10px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 13px;
    white-space: nowrap;
}
.badge.paid {
    background: #ecfdf3;
    color: #067647;
    border: 1px solid #abefc6;
}
.badge.pending {
    background: #fff7e6;
    color: #b54708;
    border: 1px solid #fedf89;
}
.inline-form {
    display: inline-flex;
    margin: 0;
}
.mini-btn,
.link-button {
    border: 0;
    border-radius: 999px;
    padding: 9px 12px;
    font-weight: 900;
    cursor: pointer;
    background: var(--red);
    color: white;
    box-shadow: none;
    width: auto;
}
.mini-btn.secondary,
.link-button {
    background: #f2f4f7;
    color: #344054;
}
.link-button {
    padding: 0;
    background: transparent;
    color: var(--red);
    border-radius: 0;
}
small {
    display: block;
    color: var(--muted);
    margin-top: 4px;
    font-weight: 700;
}
