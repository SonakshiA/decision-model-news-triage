from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from typesafe_sdk import TypeSafeClient
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["ENDPOINT"]
deployment_name = os.environ["DEPLOYMENT_NAME"]
token_scope = "https://ai.azure.com/.default"

def classify_news(state: str):
    with DefaultAzureCredential() as credential:
        token_provider = get_bearer_token_provider(credential, token_scope)
        with TypeSafeClient(
            api_key=token_provider(),
            base_url=endpoint,
            model=deployment_name,
            timeout=60,
        ) as client:
            response = client.system_one(
                state=state,
                questions={
                    "is_allegation": {
                        "type": "noul",
                        "instructions": "Does this article report an allegation, investigation, lawsuit, or enforcement action against the company?",
                        "criteria": {
                            "true": "Reports allegations, investigations, litigation, or regulatory action against the company",
                            "false": "No such allegation or action is reported",
                        },
                    },
                    "classify": {
                        "type": "choice",
                        "instructions": "What is the nature of this news?",
                        "criteria": {
                            "concerning": "Negative news or allegations involving the company, including regulatory or legal investigations, alleged misconduct, fraud, compliance violations, or reputational risk.",
                            "not-concerning": "Routine software, technical, product, or integration issues without legal, regulatory, financial, or reputational concerns.",
                        },
                    },
                     "severity": {
                        "type": "score",
                        "instructions": "How severe is the risk to the company described in this news?",
                        "criteria": [
                            "Low: routine or no real risk",
                            "Moderate: limited or unproven concern",
                            "High: formal allegation or investigation with material exposure",
                            "Critical: confirmed misconduct, major penalties, or severe financial impact",
                        ],
                    },
                },
            )
    
    return response

if __name__ == "__main__":
    news_state = "Microsoft faces accusations of fraud and inflating its stock price by failing to disclose slowing Azure growth. The class action, led by a Michigan pension fund, was filed after Microsoft shares fell 10% on Jan 29 in reaction to its quarterly earnings report. Microsoft says it believes the claims are 'without merit' and will vigorously defend itself in court"

    response = classify_news(news_state)
    
    gate = response.nouls["is_allegation"]
    label = response.choices["classify"]
    severity = response.scores["severity"]

    print(f"Allegation reported: {gate.noul:.1%}")
    print(f"Classification: {label.choice} (confidence {label.confidence:.1%})")
    print(f"Severity: {severity.score:.2f} of 3 (confidence {severity.confidence:.1%})")

    if label.choice == "concerning" and severity.score >= 2:
        action = "escalate"
    elif label.choice == "concerning" or gate.noul >= 0.5:
        action = "review"
    else:
        action = "ignore"
    print(f"Action: {action}")