"""
shared/ui_theme.py
Single source of truth for all UI styling across every agent.
Provides dark mode, light mode, glassmorphism, animations, responsive layout,
accessibility improvements, and loading states.
"""

# ── Colour tokens ─────────────────────────────────────────────────────────────
DARK = {
    "bg":           "#080d18",
    "surface":      "#0d1526",
    "surface2":     "#111e33",
    "border":       "#1a2840",
    "border2":      "#243350",
    "text":         "#e2eaf5",
    "text2":        "#8899aa",
    "text3":        "#445566",
    "accent":       "#4f9cf9",
    "accent2":      "#a78bfa",
    "success":      "#34d399",
    "warning":      "#fbbf24",
    "danger":       "#f87171",
    "glass_bg":     "rgba(13,21,38,0.72)",
    "glass_border": "rgba(79,156,249,0.18)",
}

LIGHT = {
    "bg":           "#f0f4f8",
    "surface":      "#ffffff",
    "surface2":     "#f8fafc",
    "border":       "#e2e8f0",
    "border2":      "#cbd5e1",
    "text":         "#0f172a",
    "text2":        "#475569",
    "text3":        "#94a3b8",
    "accent":       "#2563eb",
    "accent2":      "#7c3aed",
    "success":      "#16a34a",
    "warning":      "#d97706",
    "danger":       "#dc2626",
    "glass_bg":     "rgba(255,255,255,0.72)",
    "glass_border": "rgba(37,99,235,0.18)",
}

AGENT_ACCENTS = [
    "#4f9cf9", "#f87171", "#34d399", "#a78bfa",
    "#38bdf8", "#fb923c", "#4ade80", "#60a5fa",
    "#e879f9", "#2dd4bf", "#f59e0b",
]


def _css_vars(t: dict) -> str:
    return "\n".join(f"  --{k.replace('_','-')}: {v};" for k, v in t.items())


def get_css(dark: bool = True) -> str:
    t = DARK if dark else LIGHT
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── CSS variables ── */
:root {{
{_css_vars(t)}
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.12);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.18);
  --shadow-lg: 0 12px 40px rgba(0,0,0,0.28);
  --transition: 0.22s cubic-bezier(0.4,0,0.2,1);
}}

/* ── Reset & base ── */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {{
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
footer, #MainMenu {{ display: none !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: var(--surface); }}
::-webkit-scrollbar-thumb {{ background: var(--border2); border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebarContent"] {{ padding: 1rem 0.75rem !important; }}

/* ── Glassmorphism card ── */
.glass {{
  background: var(--glass-bg) !important;
  backdrop-filter: blur(16px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
}}

/* ── Surface card ── */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
  transition: box-shadow var(--transition), border-color var(--transition);
}}
.card:hover {{
  border-color: var(--border2);
  box-shadow: var(--shadow-md);
}}

/* ── Agent card ── */
.agent-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.4rem 1rem 1.2rem;
  text-align: center;
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  animation: cardPop 0.5s ease both;
  position: relative;
  overflow: hidden;
}}
.agent-card::after {{
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, var(--card-glow, rgba(79,156,249,0.08)), transparent 70%);
  opacity: 0;
  transition: opacity var(--transition);
  pointer-events: none;
}}
.agent-card:hover {{ transform: translateY(-5px); box-shadow: var(--shadow-lg); border-color: var(--card-accent, var(--accent)); }}
.agent-card:hover::after {{ opacity: 1; }}
.agent-card:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}

.agent-icon-wrap {{
  width: 52px; height: 52px;
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.9rem;
  font-size: 1.5rem;
  border: 1px solid var(--card-accent, var(--border));
  box-shadow: 0 0 18px var(--card-shadow, rgba(79,156,249,0.15));
  background: var(--surface2);
}}
.agent-num  {{ font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--card-accent, var(--accent)); margin-bottom: 0.25rem; }}
.agent-name {{ font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; line-height: 1.3; }}
.agent-desc {{ font-size: 0.72rem; color: var(--text3); line-height: 1.45; }}

/* ── Hero ── */
.hero {{ text-align: center; padding: 3rem 1rem 1.5rem; animation: fadeUp 0.6s ease both; }}
.hero-badge {{
  display: inline-block;
  background: var(--surface2); color: var(--accent);
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 0.3rem 1rem; border-radius: 999px;
  border: 1px solid var(--border2); margin-bottom: 1.2rem;
}}
.hero-title {{
  font-size: clamp(2rem, 5vw, 3rem); font-weight: 800;
  color: var(--text); letter-spacing: -0.03em; line-height: 1.1;
}}
.hero-title .accent {{
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}
.hero-sub {{ margin-top: 0.8rem; font-size: 1rem; color: var(--text2); font-weight: 400; }}
.hero-stats {{ display: flex; justify-content: center; gap: 2.5rem; margin-top: 2rem; flex-wrap: wrap; }}
.stat {{ text-align: center; }}
.stat-num {{ font-size: 1.8rem; font-weight: 700; color: var(--accent); }}
.stat-lbl {{ font-size: 0.68rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.2rem; }}

/* ── Section label ── */
.section-lbl {{
  text-align: center; font-size: 0.68rem; font-weight: 700;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--text3); margin: 2rem 0 1.2rem;
}}

/* ── Progress bar ── */
.progress-wrap {{
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.7rem 1rem;
  margin-bottom: 0.8rem; font-size: 0.78rem; color: var(--text2);
}}
.progress-bar-outer {{
  background: var(--border); border-radius: 999px;
  height: 5px; margin-top: 0.5rem; overflow: hidden;
}}
.progress-bar-inner {{
  height: 5px; border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
  position: relative; overflow: hidden;
}}
.progress-bar-inner::after {{
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  animation: shimmer 1.5s infinite;
}}

/* ── Loading skeleton ── */
.skeleton {{
  background: linear-gradient(90deg, var(--surface2) 25%, var(--border) 50%, var(--surface2) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}}

/* ── Pulse dot ── */
.pulse-dot {{
  display: inline-block; width: 8px; height: 8px;
  border-radius: 50%; background: var(--success);
  animation: pulse 2s infinite; vertical-align: middle; margin-right: 5px;
}}

/* ── Tags ── */
.tag {{
  display: inline-block; font-size: 0.65rem; font-weight: 700;
  padding: 0.18rem 0.6rem; border-radius: 4px;
  letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.4rem;
}}
.tag-tool      {{ background: var(--surface2); color: var(--accent);   border: 1px solid var(--border2); }}
.tag-question  {{ background: var(--surface2); color: var(--accent2);  border: 1px solid var(--border2); }}
.tag-emergency {{ background: rgba(248,113,113,0.12); color: var(--danger); border: 1px solid rgba(248,113,113,0.3); }}
.tag-success   {{ background: rgba(52,211,153,0.12); color: var(--success); border: 1px solid rgba(52,211,153,0.3); }}

/* ── Emergency box ── */
.emergency-box {{
  background: rgba(248,113,113,0.08);
  border: 1px solid rgba(248,113,113,0.35);
  border-radius: var(--radius-md); padding: 1rem 1.2rem;
  color: var(--danger); animation: emergencyPulse 1s ease 3;
}}

/* ── Response box ── */
.response-box {{
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 1rem 1.2rem;
  font-size: 0.9rem; line-height: 1.85; color: var(--text2);
  white-space: pre-wrap; font-family: 'Inter', sans-serif;
}}

/* ── Chat header ── */
.chat-header {{
  background: var(--surface); border-bottom: 1px solid var(--border);
  padding: 1.1rem 1.5rem; animation: slideDown 0.4s ease both;
  border-left: 4px solid var(--accent);
}}
.chat-header h2 {{ font-size: 1.05rem; font-weight: 700; color: var(--text); margin: 0; }}
.chat-header p  {{ font-size: 0.8rem; color: var(--text2); margin: 0.2rem 0 0; }}

/* ── Streamlit overrides ── */
[data-testid="stChatMessage"] {{ animation: fadeUp 0.3s ease both; }}
[data-testid="stChatMessage"] p {{
  font-size: 0.97rem !important; line-height: 1.85 !important;
  color: var(--text) !important;
}}
[data-testid="stChatInput"] textarea {{
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  color: var(--text) !important; border-radius: var(--radius-md) !important;
  font-size: 0.95rem !important; font-family: 'Inter', sans-serif !important;
  transition: border-color var(--transition), box-shadow var(--transition) !important;
}}
[data-testid="stChatInput"] textarea:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(79,156,249,0.12) !important;
}}

.stButton > button {{
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  color: var(--text) !important; font-size: 0.8rem !important; font-weight: 500 !important;
  border-radius: var(--radius-sm) !important; padding: 0.45rem 0.7rem !important;
  transition: all var(--transition) !important; font-family: 'Inter', sans-serif !important;
}}
.stButton > button:hover {{
  border-color: var(--accent) !important; color: var(--accent) !important;
  background: var(--surface2) !important; box-shadow: var(--shadow-sm) !important;
}}
.stButton > button:focus-visible {{
  outline: 2px solid var(--accent) !important; outline-offset: 2px !important;
}}

.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  color: var(--text) !important; border-radius: var(--radius-sm) !important;
  font-family: 'Inter', sans-serif !important;
}}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(79,156,249,0.1) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
  background: var(--surface2) !important; border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important; padding: 3px !important; gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important; color: var(--text2) !important;
  border-radius: var(--radius-sm) !important; font-size: 0.82rem !important;
  font-weight: 500 !important; border: none !important;
  transition: all var(--transition) !important;
}}
.stTabs [aria-selected="true"] {{
  background: var(--surface) !important; color: var(--accent) !important;
  box-shadow: var(--shadow-sm) !important;
}}

.stDataFrame {{ border-radius: var(--radius-md) !important; overflow: hidden !important; }}
.stDataFrame table {{ background: var(--surface) !important; color: var(--text) !important; }}
.stDataFrame th {{ background: var(--surface2) !important; color: var(--text2) !important; font-size: 0.78rem !important; }}
.stDataFrame td {{ color: var(--text) !important; font-size: 0.82rem !important; border-color: var(--border) !important; }}

.stAlert {{ border-radius: var(--radius-md) !important; border: 1px solid var(--border) !important; }}
.stInfo    {{ background: rgba(79,156,249,0.08) !important; border-color: rgba(79,156,249,0.25) !important; color: var(--text) !important; }}
.stSuccess {{ background: rgba(52,211,153,0.08) !important; border-color: rgba(52,211,153,0.25) !important; color: var(--text) !important; }}
.stWarning {{ background: rgba(251,191,36,0.08) !important; border-color: rgba(251,191,36,0.25) !important; color: var(--text) !important; }}
.stError   {{ background: rgba(248,113,113,0.08) !important; border-color: rgba(248,113,113,0.25) !important; color: var(--text) !important; }}

.stExpander {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-md) !important; }}
.stExpander summary {{ color: var(--text) !important; font-weight: 500 !important; }}

/* ── Sidebar nav item ── */
.nav-item {{
  display: flex; align-items: center; gap: 0.7rem;
  padding: 0.6rem 0.8rem; border-radius: var(--radius-sm);
  cursor: pointer; transition: all var(--transition);
  font-size: 0.85rem; font-weight: 500; color: var(--text2);
  border: 1px solid transparent; margin-bottom: 2px;
  text-decoration: none;
}}
.nav-item:hover {{ background: var(--surface2); color: var(--text); border-color: var(--border); }}
.nav-item.active {{ background: var(--surface2); color: var(--accent); border-color: var(--border2); font-weight: 600; }}
.nav-item .nav-icon {{ font-size: 1rem; width: 22px; text-align: center; flex-shrink: 0; }}
.nav-item .nav-badge {{
  margin-left: auto; font-size: 0.6rem; font-weight: 700;
  background: var(--accent); color: #fff;
  padding: 0.1rem 0.45rem; border-radius: 999px;
}}

/* ── Voice button ── */
.voice-btn {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--text2); border-radius: var(--radius-sm);
  padding: 0.45rem 0.9rem; font-size: 0.8rem; font-weight: 500;
  cursor: pointer; transition: all var(--transition);
}}
.voice-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
.voice-btn.listening {{
  border-color: var(--danger); color: var(--danger);
  animation: voicePulse 1s infinite;
}}

/* ── Language selector ── */
.lang-pill {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 999px; padding: 0.25rem 0.75rem;
  font-size: 0.75rem; font-weight: 600; color: var(--text2);
  cursor: pointer; transition: all var(--transition);
}}
.lang-pill:hover {{ border-color: var(--accent); color: var(--accent); }}

/* ── Divider ── */
.divider {{
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 1.5rem 0;
}}

/* ── Scanline effect ── */
.scanline {{
  position: fixed; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(79,156,249,0.12), transparent);
  animation: scanline 8s linear infinite;
  pointer-events: none; z-index: 9999;
}}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .hero {{ padding: 2rem 0.75rem 1rem; }}
  .hero-title {{ font-size: 1.8rem; }}
  .hero-stats {{ gap: 1.5rem; }}
  .agent-grid {{ grid-template-columns: repeat(2, 1fr) !important; gap: 0.75rem !important; }}
  .card {{ padding: 0.9rem 1rem; }}
  [data-testid="stChatInput"] textarea {{ font-size: 16px !important; }}
}}
@media (max-width: 480px) {{
  .agent-grid {{ grid-template-columns: 1fr 1fr !important; }}
  .hero-stats {{ gap: 1rem; }}
  .stat-num {{ font-size: 1.4rem; }}
}}

/* ── Animations ── */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideDown {{
  from {{ opacity: 0; transform: translateY(-8px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes cardPop {{
  from {{ opacity: 0; transform: scale(0.93) translateY(10px); }}
  to   {{ opacity: 1; transform: scale(1) translateY(0); }}
}}
@keyframes shimmer {{
  0%   {{ background-position: -200% 0; }}
  100% {{ background-position:  200% 0; }}
}}
@keyframes pulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(52,211,153,0.5); }}
  50%       {{ box-shadow: 0 0 0 6px rgba(52,211,153,0); }}
}}
@keyframes voicePulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(248,113,113,0.4); }}
  50%       {{ box-shadow: 0 0 0 8px rgba(248,113,113,0); }}
}}
@keyframes emergencyPulse {{
  0%, 100% {{ border-color: rgba(248,113,113,0.35); }}
  50%       {{ border-color: rgba(248,113,113,0.8); }}
}}
@keyframes scanline {{
  0%   {{ transform: translateY(-100vh); }}
  100% {{ transform: translateY(100vh); }}
}}
@keyframes spin {{
  to {{ transform: rotate(360deg); }}
}}

/* ── Loading spinner ── */
.spinner {{
  width: 20px; height: 20px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}}

/* ── Agent-1 Medicine Reminder specific ── */
.login-box {{
  max-width: 420px; margin: 3rem auto; padding: 2rem;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); box-shadow: var(--shadow-md);
}}
.login-title {{
  font-size: 1.4rem; font-weight: 800; color: var(--text);
  text-align: center; margin-bottom: 0.3rem;
}}
.login-sub {{
  font-size: 0.78rem; color: var(--text3); text-align: center;
  margin-bottom: 1.5rem; letter-spacing: 0.05em;
}}
.header-box {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 1rem 1.4rem;
  margin-bottom: 1rem;
}}
.header-box h1 {{ font-size: 1.2rem; font-weight: 700; color: var(--text); margin: 0; }}
.header-box p  {{ font-size: 0.82rem; color: var(--text2); margin: 0.2rem 0 0; }}
.voice-box {{
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 0.9rem 1rem;
  font-size: 0.85rem; color: var(--text2); line-height: 1.6;
}}
.alert-box {{
  background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.3);
  border-radius: var(--radius-sm); padding: 0.7rem 1rem;
  font-size: 0.82rem; color: var(--warning); margin-bottom: 0.5rem;
}}
.metric-card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 1rem;
  text-align: center;
}}
.metric-card h2 {{ font-size: 1.8rem; font-weight: 700; margin: 0; color: var(--text); }}
.metric-card p  {{ font-size: 0.75rem; color: var(--text3); margin: 0.3rem 0 0; }}

/* ── Agent-2 Emergency Detection specific ── */
.reading-counter {{
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.5rem 1rem;
  font-size: 0.8rem; color: var(--text2); margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.5rem;
}}
.alert-banner {{
  background: rgba(248,113,113,0.1); border: 2px solid var(--danger);
  border-radius: var(--radius-md); padding: 1rem 1.4rem;
  margin-bottom: 1rem; animation: emergencyPulse 1s ease 3;
}}
.alert-banner-title {{
  font-size: 1rem; font-weight: 800; color: var(--danger);
  letter-spacing: 0.05em; margin-bottom: 0.3rem;
}}
.alert-banner-sub {{ font-size: 0.82rem; color: var(--text2); }}
.status-emergency {{
  background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.4);
  border-radius: var(--radius-lg); padding: 1.4rem;
  margin-bottom: 1rem;
}}
.status-safe {{
  background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.3);
  border-radius: var(--radius-lg); padding: 1.4rem;
  margin-bottom: 1rem;
}}
.status-label {{
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.15em;
  text-transform: uppercase; color: var(--text3); margin-bottom: 0.4rem;
}}
.status-text-emergency {{ font-size: 1.3rem; font-weight: 700; color: var(--danger); }}
.status-text-safe      {{ font-size: 1.3rem; font-weight: 700; color: var(--success); }}
.detail-row {{
  display: flex; justify-content: space-between;
  font-size: 0.82rem; padding: 0.3rem 0;
  border-bottom: 1px solid var(--border);
}}
.detail-key   {{ color: var(--text3); }}
.detail-value {{ color: var(--text); font-weight: 500; }}
.sensor-grid {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem; margin-bottom: 1rem;
}}
.sensor-card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 1rem;
  text-align: center;
}}
.sensor-label {{ font-size: 0.68rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem; }}
.sensor-value {{ font-size: 1.1rem; font-weight: 700; }}
.sensor-value.ok     {{ color: var(--success); }}
.sensor-value.warn   {{ color: var(--warning); }}
.sensor-value.danger {{ color: var(--danger); }}
.log-container {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 0.8rem 1rem;
  max-height: 280px; overflow-y: auto; font-family: monospace;
}}
.log-entry {{
  font-size: 0.78rem; padding: 0.25rem 0;
  border-bottom: 1px solid var(--border); color: var(--text2);
}}
.log-time {{ color: var(--text3); margin-right: 0.5rem; }}
.log-info {{ color: var(--accent); margin-right: 0.3rem; }}
.log-alert {{ color: var(--danger); font-weight: 600; }}
.log-safe  {{ color: var(--success); }}
.pulse-dot.red {{ background: var(--danger); }}

/* ── Accessibility ── */
:focus-visible {{
  outline: 2px solid var(--accent) !important;
  outline-offset: 3px !important;
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }}
}}
</style>
"""


def inject(dark: bool = True) -> None:
    """Call this once at the top of any agent app.py."""
    import streamlit as st
    st.markdown(get_css(dark), unsafe_allow_html=True)
    if dark:
        st.markdown('<div class="scanline" aria-hidden="true"></div>', unsafe_allow_html=True)
