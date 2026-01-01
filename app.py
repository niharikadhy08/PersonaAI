import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import textwrap

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

st.set_page_config(
    page_title="PersonaAI",
    page_icon="֎",
    layout="wide"
)


st.title("֎ PersonaAI")


if "messages" not in st.session_state:
    st.session_state.messages = {
        "💬 Chat": [],
        "📸 Creator": [],
        "🧠 Study": [],
        "✍️ Writer": []
    }

if "disclaimer_added" not in st.session_state:
    st.session_state.disclaimer_added = True

    disclaimer_text = (
        "Hi 👋 I'm PersonaAI!\n\n"
                "You can chat with me, create content ideas, study concepts, "
                "or get help with writing.\n\n"
                "✨ Choose a mode from the sidebar and start typing!"
    )

    for mode in st.session_state.messages:
        st.session_state.messages[mode].append(
            {"role": "assistant", "content": disclaimer_text}
        )


if len(st.session_state.messages["💬 Chat"]) == 0:
    st.session_state.messages["💬 Chat"].append(
        {
            "role": "assistant",
            "content": (
                "Hi 👋 I'm PersonaAI!\n\n"
                "You can chat with me, create content ideas, study concepts or get help with writing.\n\n"
                "✨ Choose a mode from the sidebar and start typing!"
            )
        }
    )


with st.sidebar:
    st.header("🧠 AI Mode")

    ai_mode = st.radio(
        "Choose how AI should behave:",
        ["💬 Chat", "📸 Creator", "🧠 Study", "✍️ Writer"]
    )

    st.divider()

    st.header("📸 Content Ideas")

    topic = st.text_input(
        "Topic",
        placeholder="e.g. coding reels, fitness, travel"
    )

    if st.button("✨ Generate Ideas"):
        if topic.strip() == "":
            st.warning("Please enter a topic")
        else:
            with st.spinner("Thinking of ideas..."):
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a social media expert. "
                                "Format your response clearly using headings and bullet points."
                            )
                        },
                        {
                            "role": "user",
                            "content": f"Suggest content ideas for: {topic}"
                        }
                    ]
                )
                st.markdown(completion.choices[0].message.content)

    st.divider()

    def export_chat_txt():
        chat = st.session_state.messages[ai_mode]
        if not chat:
            return "No messages to export."

        text = f"PersonaAI\nMode: {ai_mode}\n"
        text += "-" * 60 + "\n\n"

        for msg in chat:
            role = "You" if msg["role"] == "user" else "AI"
            text += f"{role}: {msg['content']}\n\n"

        return text

    def export_chat_pdf():
        chat = st.session_state.messages[ai_mode]
        if not chat:
            return None

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        left_margin = 40
        bottom_margin = 50
        text = pdf.beginText(left_margin, height - 50)
        text.setFont("Helvetica", 10)

        text.textLine("PersonaAI")
        text.textLine(f"Mode: {ai_mode}")
        text.textLine("-" * 60)
        text.textLine("")

        for msg in chat:
            role = "You" if msg["role"] == "user" else "AI"
            full_text = f"{role}: {msg['content']}"

            wrapped_lines = textwrap.wrap(full_text, width=90)

            for line in wrapped_lines:
                if text.getY() < bottom_margin:
                    pdf.drawText(text)
                    pdf.showPage()
                    text = pdf.beginText(left_margin, height - 50)
                    text.setFont("Helvetica", 10)

                text.textLine(line)

            text.textLine("")

        pdf.drawText(text)
        pdf.save()
        buffer.seek(0)
        return buffer

    st.subheader("📄 Export Chat")

    st.download_button(
        label="⬇️ Export as TXT",
        data=export_chat_txt(),
        file_name=f"{ai_mode.replace(' ', '_')}_chat.txt",
        mime="text/plain"
    )

    if st.button("⬇️ Export as PDF"):
        pdf_file = export_chat_pdf()
        if pdf_file is None:
            st.warning("No messages to export yet.")
        else:
            st.download_button(
                label="📥 Click to Download PDF",
                data=pdf_file,
                file_name=f"{ai_mode.replace(' ', '_')}_chat.pdf",
                mime="application/pdf"
            )

    st.divider()

    def generate_summary():
        chat = st.session_state.messages[ai_mode]
        if not chat:
            return "No messages to summarize."

        conversation = ""
        for msg in chat:
            role = "User" if msg["role"] == "user" else "AI"
            conversation += f"{role}: {msg['content']}\n"

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize the conversation clearly using bullet points. "
                        "Highlight key ideas and conclusions."
                    )
                },
                {
                    "role": "user",
                    "content": conversation
                }
            ]
        )
        return completion.choices[0].message.content

    with st.expander("Auto Summary"):
        if st.button("Generate Summary"):
            with st.spinner("Summarizing..."):
                st.markdown(generate_summary())

    st.divider()

    if st.button("🧹 Clear Chat"):
        st.session_state.messages[ai_mode] = []
        st.success("Chat cleared!")

for msg in st.session_state.messages[ai_mode]:
    if msg["role"] == "user":
        with st.chat_message("👩‍💻"):
            st.write(msg["content"])
    else:
            st.write(msg["content"])

user_message = st.chat_input("Type your message...")

if user_message:
    if ai_mode == "💬 Chat":
        system_prompt = "You are a friendly, casual Meta-style AI assistant."
    elif ai_mode == "📸 Creator":
        system_prompt = "You are a social media content creator expert."
    elif ai_mode == "🧠 Study":
        system_prompt = "You are a patient teacher who explains things simply."
    else:
        system_prompt = "You are a professional writing assistant."

    st.session_state.messages[ai_mode].append(
        {"role": "user", "content": user_message}
    )

    with st.spinner("AI is thinking..."):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages[ai_mode]
            ]
        )

        ai_reply = completion.choices[0].message.content

    st.session_state.messages[ai_mode].append(
        {"role": "assistant", "content": ai_reply}
    )

    st.rerun()
