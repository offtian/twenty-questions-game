import os
from pathlib import Path
from typing import Any, Dict, Union, List, Tuple, Optional
import random
import argparse
import openai
from langchain.llms.openai import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory, ChatMessageHistory

import src.utils.config as config
from src.utils.llm_factory import create_llm
from src.utils.data_processing import read_objects_from_file
from src.utils.game_utils import *


def initialize_game(llm: AzureChatOpenAI) -> TwentyQuestionsGame:
    """
    Initializes and returns a TwentyQuestionsGame instance with the given AI model.
    """
    history = ChatMessageHistory()
    memory = ConversationBufferMemory(
        chat_memory=history, memory_key="chat_history", return_messages=True
    )
    return TwentyQuestionsGame(llm, memory)


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
    config.load_env_variables()

    (
        openai_api_type,
        deployment_name,
        api_base,
        api_version,
        openai_api_key,
    ) = config.get_api_credentials(False)

    # Initialize the Azure Chat AI model
    llm = create_llm(
        openai_api_type,
        deployment_name,
        api_base,
        api_version,
        openai_api_key,
        temperature=0,
    )

    # Create a game instance with the AI model and memory
    game = initialize_game(llm)

    # Play the game
    if play_mode == "play":
        game_loop(game)
    elif play_mode == "bulk_test":
        root_path = Path(__file__).parent
        objects = read_objects_from_file(
            os.path.join(root_path, "data/bulk_test/objects.txt")
        )
        results = bulk_test_game(game, objects, num_games=10)
        print("\nResults:")
        for k, v in results.items():
            print(f"\n{k}:", v)


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
