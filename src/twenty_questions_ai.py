from typing import Any, Dict, Union, List, Tuple
import os
import random
import argparse
from dotenv import load_dotenv
import openai
from langchain.llms.openai import AzureOpenAI
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.schema.messages import SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory, ChatMessageHistory


class TwentyQuestionsGame:
    """
    A class to handle the 20 Questions game using a Language Model (LM) chain.

    Args:
        llm (LLM): An instance of a Language Model.
        memory (ConversationBufferMemory): Memory buffer to store the conversation history.
        llm_chain (LLMChain): Chain of language models used for generating responses.

    Methods:
        setup_llm_chain(): Sets up the language model chain with the appropriate prompt template.
        run(user_input): Processes the user input and returns the model's response.
    """

    def __init__(self, llm: Any, memory: ConversationBufferMemory) -> None:
        """
        Initializes the TwentyQuestionsGame with a language model and memory.

        Args:
            llm (LLM): The language model to be used in the game.
            memory (ConversationBufferMemory): The memory buffer to store conversation history.
        """
        self.llm: AzureChatOpenAI = llm
        self.memory: ConversationBufferMemory = memory
        self.llm_chain: Union[LLMChain, None] = None
        self.setup_llm_chain()

    def setup_llm_chain(self) -> None:
        """
        Sets up the LLM chain with a specific chat prompt template.

        This template guides the AI in how to play the game, including the tone,
        the format of questions, and how to handle user responses.
        """
        chat_template = ChatPromptTemplate.from_messages(
            [
                # System message defining the game rules and AI behavior
                SystemMessage(
                    content=(
                        """
                        Welcome to "20 Questions"! 
                        You are playing the role of a guesser, tasked with identifying an object chosen by the human player. 
                        Your goal is to guess the object within 20 questions, using only binary ('Yes' or 'No') questions. Please maintain a respectful and upbeat tone throughout the game.
                        ## Requirements:
                        1. Question Format: Your questions should be short and binary, requiring only a 'Yes' or 'No' answer, and must be related to the object in question.
                        2. Response to 'No' Answers: If the human player answers 'No', provide an apologetic response, such as "Sorry for the unrelated question, let's try a different approach," and then continue with a new question. Ensure the apology is concise and not repetitive.
                        3. Response to 'Yes' Answers: After receiving a 'Yes' answer, continue with your line of questioning to further narrow down the object's identity.
                        4. Tracking Questions: Monitor the number of questions asked by referring to the length of the chat history. Remember, you have a limit of 20 AI questions to guess the object.
                        5. End Game Conditions: If you guess the object correctly, celebrate with an enthusiastic "Hooray!" and conclude the game. If you do not guess the object within 20 questions, acknowledge the end of the game and invite the player to reveal the object.
                        6. Hints and Progress Check: After 10 questions, you may offer a summary of what you have deduced so far or provide a hint to the player to enhance engagement.
                        7. Encouragement and Engagement: Throughout the game, use encouraging remarks and show enthusiasm to keep the player engaged and enjoying the experience.
                        8. Feedback Opportunity: At the end of the game, ask the player for feedback on their experience. This information can be invaluable for future improvements to the game.
                        9. Adaptive Strategy: If your system is capable of learning, try to adapt your questioning strategy based on previous games to improve your chances of success.
                        """
                    )  # [Game rules and AI behavior text]
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )  # Add the necessary templates
        self.llm_chain = LLMChain(
            llm=self.llm,
            prompt=chat_template,
            memory=self.memory,
        )

    def run(self, user_input: str) -> str:
        """
        Processes the user input through the LLM chain to get a response.

        Args:
            user_input (str): The input from the user.

        Returns:
            str: The response generated by the AI.
        """
        return self.llm_chain.run(user_input)

    def get_latest_question(self) -> str:
        """
        Retrieves the latest question asked by the AI from the conversation history.

        Returns:
            The most recent question asked by the AI.
        """
        ai_messages = [
            msg
            for msg in self.memory.chat_memory.messages
            if isinstance(msg, AIMessage)
        ]
        return ai_messages[-1].content if ai_messages else None

    def reset_game(self) -> None:
        """
        Resets the game state to start a new game.

        This method clears the conversation history and resets any game-specific
        variables, preparing the TwentyQuestionsGame instance for a new round.
        """

        # Reset the conversation history
        # Assuming self.memory is an instance of ConversationBufferMemory
        self.memory.clear()

        # Reset any other game-specific state variables here
        # For example, if you have a variable tracking the number of questions asked,
        # it should be reset here.

        # Reinitialize the LLM chain, if necessary
        self.setup_llm_chain()


def load_environment_variables() -> Dict[str, str]:
    """
    Loads and returns necessary environment variables for the OpenAI and Azure configurations.
    """
    # Load environment variables
    load_dotenv()
    return {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "api_type": os.getenv("OPENAI_API_TYPE"),
        "api_base": os.getenv("OPENAI_API_BASE"),
        "api_version": os.getenv("OPENAI_API_VERSION"),
        "deployment_name": os.getenv("DEPLOYMENT_NAME"),
    }


def initialize_llm_model(deployment_name: str) -> AzureChatOpenAI:
    """
    Initializes and returns an Azure Chat AI model instance.
    """
    return AzureChatOpenAI(azure_deployment=deployment_name)


def initialize_game(llm: AzureChatOpenAI) -> TwentyQuestionsGame:
    """
    Initializes and returns a TwentyQuestionsGame instance with the given AI model.
    """
    history = ChatMessageHistory()
    memory = ConversationBufferMemory(
        chat_memory=history, memory_key="chat_history", return_messages=True
    )
    return TwentyQuestionsGame(llm, memory)


def game_loop(game: TwentyQuestionsGame) -> None:
    """
    Executes the main game loop for a given TwentyQuestionsGame instance.
    """
    init_message = "Let's play 20 Questions! Think of an object, and I will try to guess it. You can only answer 'Yes' or 'No'."
    print("AI: ", init_message)
    game.memory.chat_memory.add_ai_message(init_message)

    game_over = False

    while not game_over:
        user_input = input("Your answer (Yes/No): ")
        response, game_over, question_count = process_game_turn(game, user_input)

        print(f"AI: ", response)
        print(question_count)

        if game_over:
            print(
                f"AI successfully guessed the object correctly in {question_count} questions!"
            )
        elif question_count >= 20:
            print("Game over! The AI failed to guess the object in 20 questions.")
            break


def main(play_mode: str) -> None:
    """
    Main function to execute the 20 Questions game.

    This function initializes and starts the 20 Questions game using an AI model.
    It loads environment variables for configuring the AI, sets up the necessary
    components for the game, and handles the game loop.

    The AI model used here is AzureChatOpenAI, which relies on a deployment name
    specified in the environment variables. The ConversationBufferMemory is used
    to maintain a history of the game, ensuring that the AI can reference past
    questions and answers.
    """

    # Retrieve API configuration from environment variables
    env_vars = load_environment_variables()
    openai.api_key = env_vars["api_key"]
    openai.api_type = env_vars["api_type"]
    openai.api_base = env_vars["api_base"]
    openai.api_version = env_vars["api_version"]

    # Initialize the Azure Chat AI model
    llm = initialize_llm_model(env_vars["deployment_name"])

    # Create a game instance with the AI model and memory
    game = initialize_game(llm)

    # Play the game
    if play_mode == "play":
        game_loop(game)
    elif play_mode == "bulk_test":
        results = bulk_test_game(game, ["apple", "car", "computer"], num_games=5)
        print(results)


def bulk_test_game(
    game_instance: TwentyQuestionsGame, concepts: List[str], num_games: int = 10
) -> List[Tuple[str, int]]:
    """
    Simulates multiple rounds of the 20 Questions game for testing purposes.

    Args:
        game_instance: Instance of TwentyQuestionsGame for running the simulation.
        concepts: List of concepts for the AI user to think of.
        num_games: Number of games to simulate.

    Returns:
        List of tuples, each indicating the result ('Success' or 'Failure') and number of questions used in each game.
    """
    return [
        simulate_game(game_instance, random.choice(concepts)) for _ in range(num_games)
    ]


def process_game_turn(
    game: TwentyQuestionsGame, user_input: str
) -> Tuple[str, bool, int]:
    """
    Processes a single turn in the 20 Questions game.

    Args:
        game: Instance of TwentyQuestionsGame for running the game.
        user_input: User (or AI) input for the game turn.

    Returns:
        A tuple containing the AI response, a flag indicating if the game is over, and the current question count.
    """
    game.memory.chat_memory.add_user_message(user_input)
    response = game.run(user_input)

    game_over = response.strip().lower().startswith("hooray")
    ai_messages = [
        msg for msg in game.memory.chat_memory.messages if isinstance(msg, AIMessage)
    ]
    question_count = len(ai_messages) - 1

    return response, game_over, question_count


def simulate_game(game_instance: TwentyQuestionsGame, concept: str) -> Tuple[str, int]:
    """
    Simulates a single round of the 20 Questions game using an AI user.

    Args:
        game_instance: Instance of TwentyQuestionsGame for running the game.
        llm_chain: Instance of LLMChain to generate AI user responses.
        concept: The concept the AI user is thinking of.

    Returns:
        Tuple with the result of the game ('Success' or 'Failure') and number of questions asked.
    """
    env_vars = load_environment_variables()

    game_instance.reset_game()

    print("\nHuman: The concept is ...", concept)
    init_message = "Let's play 20 Questions! Think of an object, and I will try to guess it. You can only answer 'Yes' or 'No'."
    print("AI: ", init_message)
    game_instance.memory.chat_memory.add_ai_message(init_message)

    for i in range(1, 21, 1):
        latest_question = game_instance.get_latest_question()
        if i == 1:
            user_input = "Yes"
        else:
            user_input = ai_user_response(
                llm=AzureChatOpenAI(
                    azure_deployment=env_vars["deployment_name"], temperature=0.7
                ),
                concept=concept,
                question=latest_question,
            )
        response, game_over, question_count = process_game_turn(
            game_instance, user_input
        )
        print("\nHuman: ", user_input)
        print("\nAI: ", response)
        if game_over:
            return "Success", question_count

    return "Failure", question_count


def ai_user_response(llm: AzureOpenAI, concept: str, question: str) -> str:
    """
    Generates a binary response using an AzureChatOpenAI LLMChain based on the concept and the question.

    Args:
        llm_chain: An instance of LLMChain to generate responses.
        concept: The concept or object the AI user is thinking of.
        question: The question asked by the guessing AI.

    Returns:
        'Yes' or 'No' based on the AI's response.
    """
    # Construct the prompt for the AI model
    prompt = f"""
    You are playing the '20 Questions' game with another player. Your role is to answer 'Yes' or 'No' to questions based on a given concept or object.

    ## Concept/Object:
    The concept/object for this session is identified as {concept}.
    ## Rules for Answering Questions:
    Direct Relevance: If the binary question ({question}) asked by the player is directly related to the {concept}, respond truthfully based on the nature of the {concept}.
    - Answer 'YES' if the {question} correctly pertains to the {concept}.
    - Answer 'NO' if the {question} does not pertain to the {concept}.
    Answer:"""
    # Get the AI's response
    ai_response = llm.predict(prompt)

    # Process and return the AI's response
    return "Yes" if ai_response.strip().lower() == "yes" else "No"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Play 20 Questions Game or run a bulk test."
    )
    parser.add_argument(
        "play_mode",
        type=str,
        default="play",
        choices=["play", "bulk_test"],
        help="Mode to play the game: 'play' for interactive mode, 'bulk_test' for automated testing.",
    )
    args = parser.parse_args()

    main(args.play_mode)
