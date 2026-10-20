from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from classify_news import classify_news
import json
import os

from dotenv import load_dotenv
load_dotenv()

endpoint = os.environ["PROJECT_ENDPOINT"]
agent_name = "extract-news-agent"
user_message = "Amazon"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    # Bind the OpenAI client to the existing agent endpoint.
    openai_client = project_client.get_openai_client(agent_name=agent_name)

    # GitHub Copilot preview agents require a conversation for every Responses turn.
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=[{"role": "user", "content": user_message}],
    )

    raw_output = response.output[-1].content[0].text
    news_items = json.loads(raw_output)
    summaries = [item["summary"] for item in news_items]

    # Classify each news summary
    for summary in summaries:
        classification = classify_news(summary).choices["classify"]
        print(f"\nNews Summary: {summary}")
        print(f"Classification: {classification.choice} (confidence: {classification.confidence:.1%})")
        print(f"Probability the news is concerning: {classification.probabilities['concerning']:.1%}")
        print(f"Probability the news is not concerning: {classification.probabilities['not-concerning']:.1%}")