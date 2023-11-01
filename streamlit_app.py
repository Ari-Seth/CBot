import streamlit as st
import qdrant_client

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings

def get_vectorstore():
    client = qdrant_client.QdrantClient(
        st.secrets["QDRANT_HOST"],
        api_key=st.secrets["QDRANT_API_KEY"]
    )
        
    embeddings = OpenAIEmbeddings()

    vector_store = Qdrant(
        client=client,
        collection_name=st.secrets["QDRANT_COLLECTION_NAME"],
        embeddings=embeddings,
    )


    return vector_store


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(temperature=0.6)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response.get('chat_history', [])

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            # content_after_pipe = message.content[16:].strip()
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def on_key_press(e):
  # Clear the user input when the user hits Enter
  if e.key == "Enter":
    st.session_state["user_question"] = ""
    
css = '''
    <style>
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #2b313e
    }
    .chat-message.bot {
        background-color: #475063
    }
    .chat-message .avatar {
    width: 20%;
    }
    .chat-message .avatar img {
    max-width: 78px;
    max-height: 78px;
    border-radius: 50%;
    object-fit: cover;
    }
    .chat-message .message {
    width: 80%;
    padding: 0 1.5rem;
    color: #fff;
    }
    '''

bot_template = '''
    <div class="chat-message bot">
        <div class="avatar">
            <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
        </div>
        <div class="message">{{MSG}}</div>
    </div>
    '''

user_template = '''
    <div class="chat-message user">
        <div class="avatar">
            <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png">
        </div>    
        <div class="message">{{MSG}}</div>
    </div>
    '''

    


def main():    
    st.set_page_config(page_title="CurBot", page_icon="images/CurBot chatbot.png")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # Sidebar
    # st.sidebar.header("Conversation History")   


    st.header("Curriculum Bot")
    user_question = st.text_input("ECNG 1009 Edition")

    if user_question:
        handle_userinput(user_question)    

    vectorstore = get_vectorstore()

    # create conversation chain
    if st.session_state.conversation is None:
        st.session_state.conversation = get_conversation_chain(vectorstore)

    

if __name__ == '__main__':
    main()