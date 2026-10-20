import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BingCustomSearchPreviewTool,
    BingCustomSearchToolParameters,
    BingCustomSearchConfiguration,
)

from dotenv import load_dotenv
load_dotenv()

PROMPT = """
You are a useful news agent, proficient in extracting news headlines and summaries in raw format as present in the news source. 
Provide headline and summary in JSON format along with the URL for a given company. 
Extract news only from allowed domains. You can extract multiple news items if available.
If you don't find any news from the allowed domains, return NA. 
Don't send news from random other URLs.

output json format:
{
    "headline": "",
    "summary": "",
    "url": ""
}
"""

conn_id = os.getenv("CONN_ID")

project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

tool = BingCustomSearchPreviewTool(
    bing_custom_search_preview=BingCustomSearchToolParameters(
        search_configurations=[
            BingCustomSearchConfiguration(
                project_connection_id=conn_id,
                instance_name="mbbdomains",
            )
        ]
    )
)

with project_client:
    agent = project_client.agents.create_version(
        agent_name="extract-news-agent",
        definition=PromptAgentDefinition(
            model="gpt-4.1",
            instructions=PROMPT,
            tools=[tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")