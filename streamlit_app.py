import streamlit as st
from streamlit_feedback import streamlit_feedback
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory

from src.twenty_questions_game import TwentyQuestionsGame
from src.utils.config import load_env_variables, get_api_credentials
from src.streamlit_utils.ui_components import (
    setup_streamlit_page,
    initialize_question_count,
    get_temperature_setting,
)
from src.utils.llm_factory import create_llm


class StreamlitChatApp:
    """A Streamlit application to play the "20 Questions" game with a Language Learning Model (LLM).

    The app interfaces with the OpenAI API to utilize Azure's Chat OpenAI model for playing the game.
    It maintains conversation state and history using Streamlit's session state and Langchain's memory components.
    """

    def __init__(self):
        """Initialize the Streamlit app, load environment variables, and set up the game."""
        load_env_variables()
        setup_streamlit_page()
        initialize_question_count()
        self.setup_memory()
        (
            openai_api_type,
            deployment_name,
            api_base,
            api_version,
            openai_api_key,
        ) = get_api_credentials(is_streamlit_active=True)
        self.temperature = get_temperature_setting()  # Get temperature setting
        self.llm = create_llm(
            openai_api_type,
            deployment_name,
            api_base,
            api_version,
            openai_api_key,
            self.temperature,
        )
        self.setup_game()  # Initialize the game logic

    def setup_memory(self):
        """Set up the memory for storing the chat history. Initialize the history with a starting message."""

        self.msgs = StreamlitChatMessageHistory(key="langchain_messages")
        self.memory = ConversationBufferMemory(
            chat_memory=self.msgs, memory_key="chat_history", return_messages=True
        )
        if len(self.msgs.messages) == 0:
            self.msgs.add_ai_message(
                "Let's play 20 Questions! Think of an object, and I will try to guess it. You can only answer 'Yes' or 'No'."
            )

    def setup_game(self):
        """Initialize the TwentyQuestionsGame with the configured LLM and memory."""
        self.game = TwentyQuestionsGame(self.llm, self.memory)

    def run(self):
        """The main loop of the app. Handles user inputs and AI responses, and manages the game's logic."""
        for msg in self.msgs.messages:
            st.chat_message(msg.type).write(msg.content)

        if user_input := st.chat_input():
            st.chat_message("human").write(user_input)
            try:
                response = self.game.run(user_input)
                self.handle_game_logic(response)
                st.chat_message("ai").write(response)
                streamlit_feedback(feedback_type="thumbs")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    def handle_game_logic(self, response):
        """Handle the game logic based on the AI's response.
        Check for game winning / losing conditions and manage the question count.
        """
        if response.strip().lower().startswith("hooray"):
            st.toast("Hooray!", icon="🎉")
            st.success(
                f"AI successfully guessed the object correctly in {st.session_state.question_count} questions!"
            )

            return st.button("Restart Game", on_click=self.restart_game)

        st.session_state.question_count += 1

        if st.session_state.question_count > 20:
            st.chat_message("ai").write(
                "I am sorry, I couldn't guess the object you're thinking about!"
            )

            st.error("Game over! The AI failed to guess in 20 questions.")
            st.button("Restart Game", on_click=self.restart_game)
            st.stop()

    def restart_game(self):
        """Restart the game by resetting the question count and rerunning the Streamlit app."""
        st.session_state.langchain_messages = []
        st.session_state.question_count = 1
        # st.rerun()


# Main execution
if __name__ == "__main__":
    app = StreamlitChatApp()
    app.run()
