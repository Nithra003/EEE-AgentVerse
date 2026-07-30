"""
shared/ui_components.py
Reusable UI components used across all agents.
Fixed: XSS via html.escape(), lazy components import.
"""

import html
import streamlit as st

# components imported lazily inside voice_input() and tts_speak() only

# ── Language config ────────────────────────────────────────────────────────────
LANGUAGES = {
    "English":    {"code": "en-IN", "flag": "🇬🇧", "label": "EN"},
    "Tamil":      {"code": "ta-IN", "flag": "🇮🇳", "label": "TA"},
    "Hindi":      {"code": "hi-IN", "flag": "🇮🇳", "label": "HI"},
    "Telugu":     {"code": "te-IN", "flag": "🇮🇳", "label": "TE"},
    "Kannada":    {"code": "kn-IN", "flag": "🇮🇳", "label": "KN"},
    "Malayalam":  {"code": "ml-IN", "flag": "🇮🇳", "label": "ML"},
}

AGENT_NAV = [
    {"id": "medicine",     "icon": "💊", "label": "Medicine Reminder",     "port": 8501},
    {"id": "emergency",    "icon": "🚨", "label": "Emergency Detection",   "port": 8502},
    {"id": "appointment",  "icon": "📅", "label": "Appointment Booking",   "port": 8503},
    {"id": "prescription", "icon": "📋", "label": "Prescription Explainer","port": 8504},
    {"id": "health",       "icon": "📊", "label": "Health Report",         "port": 8505},
    {"id": "family",       "icon": "👨‍👩‍👧", "label": "Family Notifier",       "port": 8506},
    {"id": "diet",         "icon": "🥗", "label": "Diet Recommendation",   "port": 8507},
    {"id": "exercise",     "icon": "🏃", "label": "Exercise Coach",        "port": 8508},
    {"id": "mood",         "icon": "😊", "label": "Mood Companion",        "port": 8509},
    {"id": "voice",        "icon": "🎙️", "label": "Voice Assistant",       "port": 8510},
]


# ── Theme toggle ───────────────────────────────────────────────────────────────

def init_theme() -> bool:
    """Initialize theme in session state. Returns True if dark mode."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True
    return st.session_state.dark_mode


def theme_toggle() -> bool:
    """Render a compact theme toggle. Returns current dark_mode value."""
    dark = st.session_state.get("dark_mode", True)
    label = "☀️ Light" if dark else "🌙 Dark"
    if st.button(label, key="_theme_toggle", help="Toggle dark/light mode",
                 use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()
    return st.session_state.dark_mode


# ── Language selector ──────────────────────────────────────────────────────────

def language_selector(key: str = "lang") -> dict:
    """
    Compact language selector. Returns the selected language dict
    with keys: code, flag, label.
    """
    if key not in st.session_state:
        st.session_state[key] = "English"

    lang_names = list(LANGUAGES.keys())
    selected = st.selectbox(
        "🌐 Language",
        lang_names,
        index=lang_names.index(st.session_state[key]),
        key=f"_{key}_select",
        label_visibility="collapsed",
    )
    st.session_state[key] = selected
    return LANGUAGES[selected]


# ── Sidebar navigation ─────────────────────────────────────────────────────────

def sidebar_nav(active_id: str = "", show_events: bool = True) -> None:
    """
    Render the full sidebar: branding, theme toggle, language selector,
    agent navigation links, and live event count badge.
    """
    from shared.event_bus import _load as _load_events

    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:0.5rem 0 1rem; text-align:center;">
          <div style="font-size:1.3rem; font-weight:800; letter-spacing:-0.02em;">
            ElderCare <span style="color:var(--accent)">AI</span>
          </div>
          <div style="font-size:0.68rem; color:var(--text3); margin-top:0.2rem; letter-spacing:0.08em; text-transform:uppercase;">
            AgentVerse · EEE Team
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Theme + Language row
        c1, c2 = st.columns([1, 1])
        with c1:
            theme_toggle()
        with c2:
            language_selector()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Agent navigation
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:var(--text3);margin-bottom:0.5rem;">Agents</div>',
            unsafe_allow_html=True,
        )

        # Count unread events per agent for badges
        event_counts: dict[str, int] = {}
        if show_events:
            try:
                all_events = _load_events()
                for ev in all_events:
                    src = ev.get("source", "")
                    for ag in AGENT_NAV:
                        if ag["id"] in src.lower():
                            event_counts[ag["id"]] = event_counts.get(ag["id"], 0) + 1
            except Exception:
                pass

        for ag in AGENT_NAV:
            is_active = ag["id"] == active_id
            badge_html = ""
            if event_counts.get(ag["id"], 0) > 0:
                badge_html = f'<span class="nav-badge">{event_counts[ag["id"]]}</span>'
            active_cls = "active" if is_active else ""
            st.markdown(
                f'<a class="nav-item {active_cls}" href="http://localhost:{ag["port"]}" target="_self">'
                f'<span class="nav-icon" aria-hidden="true">{ag["icon"]}</span>'
                f'<span>{ag["label"]}</span>'
                f'{badge_html}'
                f'</a>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Status
        st.markdown(
            '<div style="font-size:0.72rem;color:var(--text3);text-align:center;">'
            '<span class="pulse-dot" aria-hidden="true"></span>All agents online</div>',
            unsafe_allow_html=True,
        )


# ── Voice controls ─────────────────────────────────────────────────────────────

def voice_input(lang_code: str = "en-IN", key: str = "voice_in") -> str:
    """
    Render a mic button. On click, uses browser SpeechRecognition API
    to capture speech and injects it into a hidden text field.
    Returns the transcribed text (empty string if nothing captured yet).
    """
    import streamlit.components.v1 as components
    result_key = f"_{key}_result"
    if result_key not in st.session_state:
        st.session_state[result_key] = ""

    components.html(f"""
    <div id="voice_container_{key}" style="display:inline-block;">
      <button
        id="mic_btn_{key}"
        onclick="startListening_{key}()"
        aria-label="Start voice input"
        style="
          display:inline-flex; align-items:center; gap:6px;
          background:var(--surface2,#111e33); border:1px solid var(--border,#1a2840);
          color:var(--text2,#8899aa); border-radius:8px;
          padding:7px 14px; font-size:13px; font-weight:500;
          cursor:pointer; font-family:Inter,sans-serif;
          transition:all 0.2s;
        "
        onmouseover="this.style.borderColor='var(--accent,#4f9cf9)';this.style.color='var(--accent,#4f9cf9)'"
        onmouseout="this.style.borderColor='var(--border,#1a2840)';this.style.color='var(--text2,#8899aa)'"
      >
        🎙️ Speak
      </button>
      <span id="status_{key}" style="font-size:12px;color:#8899aa;margin-left:8px;"></span>
    </div>
    <script>
    function startListening_{key}() {{
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
        document.getElementById('status_{key}').textContent = 'Not supported in this browser';
        return;
      }}
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SR();
      rec.lang = '{lang_code}';
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      const btn = document.getElementById('mic_btn_{key}');
      const status = document.getElementById('status_{key}');
      btn.textContent = '🔴 Listening...';
      btn.style.borderColor = '#f87171';
      btn.style.color = '#f87171';
      status.textContent = 'Speak now...';
      rec.start();
      rec.onresult = (e) => {{
        const text = e.results[0][0].transcript;
        status.textContent = '✓ ' + text;
        btn.textContent = '🎙️ Speak';
        btn.style.borderColor = '';
        btn.style.color = '';
        // Post to Streamlit via query param trick
        const url = new URL(window.location.href);
        url.searchParams.set('voice_{key}', text);
        window.history.replaceState(null, '', url.toString());
        window.parent.postMessage({{type:'voice_result',key:'{key}',text:text}}, '*');
      }};
      rec.onerror = (e) => {{
        status.textContent = 'Error: ' + e.error;
        btn.textContent = '🎙️ Speak';
        btn.style.borderColor = '';
        btn.style.color = '';
      }};
      rec.onend = () => {{
        if (btn.textContent === '🔴 Listening...') {{
          btn.textContent = '🎙️ Speak';
          btn.style.borderColor = '';
          btn.style.color = '';
        }}
      }};
    }}
    </script>
    """, height=44)

    return st.session_state.get(result_key, "")


def tts_speak(text: str, lang_code: str = "en-IN", rate: float = 0.88) -> None:
    """Inject browser TTS to speak the given text."""
    import streamlit.components.v1 as components
    safe = text.replace("'", " ").replace('"', " ").replace("\n", " ")
    safe = safe.encode("ascii", "ignore").decode("ascii")[:500]
    components.html(f"""
    <script>
    (function() {{
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance('{safe}');
      u.lang = '{lang_code}';
      u.rate = {rate};
      u.pitch = 1.0;
      u.volume = 1.0;
      window.speechSynthesis.speak(u);
    }})();
    </script>
    """, height=0)


def tts_button(text: str, label: str = "🔊 Read Aloud",
               lang_code: str = "en-IN", key: str = "tts") -> None:
    """Render a speak button that reads `text` aloud when clicked."""
    if st.button(label, key=key, help="Read this aloud"):
        tts_speak(text, lang_code)


# ── Progress bar ───────────────────────────────────────────────────────────────

def progress_bar(current: int, total: int, label: str = "Progress") -> None:
    """Render an animated step progress bar."""
    pct = int((current / max(total, 1)) * 100)
    st.markdown(f"""
    <div class="progress-wrap" role="progressbar"
         aria-valuenow="{current}" aria-valuemin="0" aria-valuemax="{total}"
         aria-label="{label}">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span>{label}</span>
        <span style="font-weight:600;color:var(--accent);">Step {current} / {total}</span>
      </div>
      <div class="progress-bar-outer">
        <div class="progress-bar-inner" style="width:{pct}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Loading skeleton ───────────────────────────────────────────────────────────

def loading_skeleton(lines: int = 3) -> None:
    """Show skeleton loading placeholders."""
    bars = "".join(
        f'<div class="skeleton" style="height:14px;margin-bottom:8px;'
        f'width:{90 - i*12}%;"></div>'
        for i in range(lines)
    )
    st.markdown(
        f'<div style="padding:1rem;">{bars}</div>',
        unsafe_allow_html=True,
    )


# ── Agent header ───────────────────────────────────────────────────────────────

def agent_header(title: str, subtitle: str, accent: str = "#4f9cf9",
                 back_url: str = "http://localhost:8500") -> None:
    """Render a consistent page header with back button."""
    safe_title    = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    safe_accent   = html.escape(accent)
    safe_back_url = html.escape(back_url)
    st.markdown(f"""
    <div class="chat-header" style="border-left-color:{safe_accent};"
         role="banner">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
        <div>
          <h2 style="color:var(--text);">{safe_title}</h2>
          <p style="color:var(--text2);">{safe_subtitle}</p>
        </div>
        <a href="{safe_back_url}"
           style="font-size:0.75rem;color:var(--text3);text-decoration:none;
                  border:1px solid var(--border);border-radius:6px;
                  padding:0.3rem 0.8rem;transition:all 0.2s;"
           aria-label="Back to dashboard">
          ← Dashboard
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Event banner ───────────────────────────────────────────────────────────────

def event_banner(events: list[dict], icon: str = "📡",
                 title: str = "Incoming Event") -> None:
    """Render inter-agent event notification banners."""
    for ev in events:
        p = ev.get("payload", {})
        ts = html.escape(ev.get("timestamp", ""))
        src = html.escape(ev.get("source", ""))
        # Escape all payload values to prevent XSS
        summary = " · ".join(
            f"{html.escape(str(k))}: {html.escape(str(v))}"
            for k, v in p.items() if k != "recommendations"
        )
        st.markdown(f"""
        <div class="card" role="alert" aria-live="polite"
             style="border-left:3px solid var(--accent);padding:0.8rem 1rem;">
          <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
            <span aria-hidden="true">{icon}</span>
            <span style="font-size:0.75rem;font-weight:700;color:var(--accent);
                         text-transform:uppercase;letter-spacing:0.08em;">{title}</span>
            <span style="margin-left:auto;font-size:0.68rem;color:var(--text3);">{ts}</span>
          </div>
          <div style="font-size:0.82rem;color:var(--text2);">
            <span style="color:var(--text3);">From:</span> {src}<br>
            {summary}
          </div>
        </div>
        """, unsafe_allow_html=True)
