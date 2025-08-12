# story_generator.py
# Purpose: Uses OpenAI’s GPT to generate a full story, then saves it to the database.

# This file is responsible for:
# - Talking to GPT-4 to generate a complete branching story in JSON form.
# - Validating that GPT’s output matches your expected structure (StoryLLMResponse).
# - Saving that structure into your database as Story and StoryNode records.
# - Doing this recursively so every branch and choice gets stored.

from sqlalchemy.orm import Session  # Needed to talk to your database (via SQLAlchemy ORM).

from langchain_openai import ChatOpenAI  # ChatOpenAI → LangChain wrapper for GPT models.
from langchain_core.prompts import ChatPromptTemplate  # ChatPromptTemplate → Lets you build structured prompts.
from langchain_core.output_parsers import PydanticOutputParser  # PydanticOutputParser → Ensures GPT’s output matches your Pydantic models.

from core.prompts import STORY_PROMPT  # STORY_PROMPT: The instructions for GPT.
from models.story import Story, StoryNode  # Story / StoryNode: Your database models.
from core.models import StoryLLMResponse, StoryNodeLLM  # StoryLLMResponse / StoryNodeLLM: Your Pydantic models that describe the expected structure of GPT output.
from dotenv import load_dotenv
import os

# Makes sure your .env file (with API keys, DB connection, etc.) is loaded before calling GPT.
load_dotenv()

# This class is essentially a service that handles story creation.
class StoryGenerator:

    # Returns a ready-to-use GPT model (gpt-4o-mini here instead of gpt-4-turbo).
    # Supports custom API keys and base URLs from environment variables (for deployment setups like Choreo).
    @classmethod
    def _get_llm(cls):  # private method
        openai_api_key = os.getenv("CHOREO_OPENAI_CONNECTION_OPENAI_API_KEY")
        serviceurl = os.getenv("CHOREO_OPENAI_CONNECTION_SERVICEURL")

        if openai_api_key and serviceurl:
            return ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key, base_url=serviceurl)

        return ChatOpenAI(model="gpt-4o-mini")

    # This is the main function you call when you want to make a new story.
    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        llm = cls._get_llm()  # get the model

        # Tells LangChain: "Whatever GPT outputs, try to turn it into a StoryLLMResponse object."
        # If GPT outputs something invalid, this will raise an error.
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        # Prepares a chat prompt with my story prompt
        # System message: Your rules (STORY_PROMPT).
        # Human message: The user request (theme).
        # .partial(...) replaces {format_instructions} in STORY_PROMPT with JSON format rules from story_parser.
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                STORY_PROMPT
            ),
            (
                "human",
                f"Create the story with this theme: {theme}"
            )
        ]).partial(format_instructions=story_parser.get_format_instructions())

        # prompt.invoke({}) → builds the final prompt text.
        # llm.invoke(...) → sends it to GPT and gets a response.
        raw_response = llm.invoke(prompt.invoke({}))

        # Some LLM wrappers return an object; here, we grab just the .content text if available.
        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        # Converts GPT’s JSON string into a real Python object (StoryLLMResponse).
        # This step will fail if GPT’s JSON is missing fields or formatted wrong.
        story_structure = story_parser.parse(response_text)

        # Adds a new row in your stories table.
        # flush() writes to DB and populates story_db.id.
        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        # Ensures root node is a proper StoryNodeLLM object.
        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        # calls _process_story_node to recursively save nodes and options
        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        # commit transaction
        db.commit()
        return story_db

    # This is where the recursive magic happens
    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        # Create a DB row for the node
        node = StoryNode(
            story_id=story_id,
            content=node_data.content if hasattr(node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data["isWinningEnding"],
            options=[]
        )

        db.add(node)
        db.flush()
        # Adds this node to DB.
        # Now node.id exists after flush().

        # If it’s not an ending, process its options
        # Loops through each choice in this node.
        # Validates that the nextNode is a StoryNodeLLM.
        # Calls _process_story_node again for each child node (recursion).
        # Links each option text to the child node’s DB id.
        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                child_node = cls._process_story_node(db, story_id, next_node, False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()
        return node  # return this node

## Root Node
# ├─ Option 1 → Node A
# │    ├─ Option 1a → Node A1
# │    └─ Option 1b → Ending Node
# └─ Option 2 → Node B
#      └─ ...
# _process_story_node starts at the root and keeps calling itself
# for each branch until all leaves (endings) are stored.
