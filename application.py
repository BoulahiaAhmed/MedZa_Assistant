import streamlit as st
from chatbot import Chatbot


# Streamed response emulator
def response_generator(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)


st.title("MedZa Assistant")
st.subheader("Always fresh, always informed!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = Chatbot(prompt)
        response = st.write_stream(response_generator(response))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

st.sidebar.header("**Welcome to MedZa Assistant!**")
st.sidebar.write("""\n\n I'm here to provide you with the latest updates, answer your burning questions.\n\n From trending news to real-time data, think of me as your knowledgeable sidekick, ready to assist you whenever you need it.\n\n Let's explore together and stay ahead of the curve!\n\n""")
st.sidebar.divider()
st.sidebar.write("""Created with :heart: by Ahmed & Hamza Boulahia""")
