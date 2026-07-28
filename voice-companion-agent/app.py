import streamlit as st

from chatbot import (
    generate_ai_response,
    get_daily_motivation,
    get_wellness_suggestions,
)
from responses import get_industry_notes, get_intro_text
from utils import create_history_dataframe, format_timestamp, validate_patient_form


def initialize_session_state() -> None:
    """Initialize persistent Streamlit state for the companion app."""
    defaults = {
        "patient_name": "",
        "age": "",
        "gender": "",
        "mood": "",
        "conversation_history": [],
        "motivation_quote": "",
        "chat_ready": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header() -> None:
    """Render the friendly landing page header."""
    st.title("😊 ElderCare AI – Voice Companion Agent")
    st.write(get_intro_text())
    st.caption("A calm, kind assistant for conversation, emotional support, and daily wellness encouragement.")


def render_patient_form() -> None:
    """Render the patient information form and validate user input."""
    st.subheader("🧾 Patient Information")
    st.write("Please enter a few details so the companion can greet you warmly and offer helpful support.")

    mood_options = [
        ("😊 Happy", "Happy"),
        ("😐 Normal", "Normal"),
        ("😔 Sad", "Sad"),
        ("😟 Anxious", "Anxious"),
        ("😴 Tired", "Tired"),
        ("😕 Lonely", "Lonely"),
    ]

    with st.form("patient_form", clear_on_submit=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            patient_name = st.text_input(
                "Patient Name",
                value=st.session_state.patient_name,
                placeholder="Enter name",
            )
        with col2:
            age = st.text_input(
                "Age",
                value=str(st.session_state.age) if st.session_state.age != "" else "",
                placeholder="Enter age",
            )

        gender = st.selectbox(
            "Gender",
            options=["Female", "Male", "Non-binary", "Prefer not to say"],
            index=0 if st.session_state.gender == "" else ["Female", "Male", "Non-binary", "Prefer not to say"].index(st.session_state.gender),
        )
        mood_label = st.selectbox("Current Mood", options=[item[0] for item in mood_options])
        mood_value = dict(mood_options)[mood_label]
        submitted = st.form_submit_button("Save Patient Details")

        if submitted:
            is_valid, message = validate_patient_form(patient_name, age, gender, mood_value)
            if not is_valid:
                st.error(message)
            else:
                st.session_state.patient_name = patient_name.strip()
                st.session_state.age = int(age)
                st.session_state.gender = gender
                st.session_state.mood = mood_value
                st.session_state.chat_ready = True
                st.session_state.motivation_quote = ""
                st.success(f"Thank you, {patient_name.strip()}! Your profile is ready.")


def render_chat_interface() -> None:
    """Render the chat UI and maintain conversation history."""
    if not st.session_state.chat_ready:
        st.info("Please save your details first to unlock the companion chat.")
        return

    st.markdown("---")
    st.subheader("💬 Voice Companion Chat")
    st.caption("Type a message and the companion will respond with kindness and encouragement.")

    if not st.session_state.conversation_history:
        with st.chat_message("assistant"):
            st.write(
                f"Hello {st.session_state.patient_name}! I’m here with you today. "
                f"How are you feeling right now?"
            )

    for entry in st.session_state.conversation_history:
        with st.chat_message("user"):
            st.write(entry["user_message"])
        with st.chat_message("assistant"):
            st.write(entry["ai_response"])

    prompt = st.chat_input("Type your message here...")
    if prompt is not None:
        if not prompt.strip():
            st.warning("Please type a message before sending.")
        else:
            ai_response = generate_ai_response(
                patient_name=st.session_state.patient_name,
                user_message=prompt,
                mood=st.session_state.mood,
            )
            st.session_state.conversation_history.append(
                {
                    "time": format_timestamp(),
                    "user_message": prompt.strip(),
                    "ai_response": ai_response,
                }
            )
            st.rerun()


def render_wellness_section() -> None:
    """Show wellness suggestions and daily motivation."""
    if not st.session_state.chat_ready:
        return

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌿 Wellness Suggestions")
        suggestions = get_wellness_suggestions(st.session_state.mood)
        for suggestion in suggestions:
            st.write(f"• {suggestion}")

    with col2:
        st.subheader("🌟 Daily Motivation")
        if st.button("Get Daily Motivation"):
            st.session_state.motivation_quote = get_daily_motivation()
            st.info(st.session_state.motivation_quote)
        if st.session_state.motivation_quote:
            st.info(st.session_state.motivation_quote)


def render_history_section() -> None:
    """Display the conversation history in a simple table."""
    if not st.session_state.chat_ready:
        return

    st.markdown("---")
    st.subheader("📜 Conversation History")
    history_df = create_history_dataframe(st.session_state.conversation_history)
    st.dataframe(history_df, use_container_width=True)


def render_future_integration_notes() -> None:
    """Show where future ElderCare agents can plug in."""
    st.markdown("---")
    st.subheader("🔧 Future Integration Points")
    notes = get_industry_notes()
    for note in notes:
        st.write(f"• {note}")


def main() -> None:
    """Run the full ElderCare AI companion experience."""
    st.set_page_config(page_title="ElderCare AI", page_icon="🤖", layout="centered")
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(135deg, #f7fbff 0%, #eef7f2 100%); }
        .stButton>button { background-color: #4f9d69; color: white; border-radius: 10px; padding: 0.5rem 1rem; }
        .stTextInput>div>div>input { border-radius: 8px; }
        .stSelectbox>div>div>div { border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    initialize_session_state()
    render_header()
    render_patient_form()
    render_chat_interface()
    render_wellness_section()
    render_history_section()
    render_future_integration_notes()


if __name__ == "__main__":
    main()
