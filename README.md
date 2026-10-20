---
title: News Triage
description: Extract company news and classify articles for company risk with Microsoft Foundry.
---

[classify_news.py](./classify_news.py) screens a news article for company risk. It uses **Microsoft-Decision-1**, a Microsoft Foundry model that returns typed decisions (probabilities and labels) instead of generated text.

> **Model in use: Microsoft-Decision-1**
> Deployed in Microsoft Foundry as the deployment `decision-model` and called through the Decision API (`/providers/microsoft`). Learn more in [Deploy and use Microsoft-Decision-1](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision).

## How it works

One `system_one` request sends the article text together with three typed questions:

| Question | Type | Purpose | Result |
|---|---|---|---|
| `is_allegation` | `noul` | Does the article report an allegation, investigation, lawsuit, or enforcement action? | Probability from 0 to 1 |
| `classify` | `choice` | Is the news `concerning` or `not-concerning`? | Selected label, confidence, and per-label probabilities |
| `severity` | `score` | How severe is the risk (Low, Moderate, High, Critical)? | Score from 0 to 3, which can fall between levels |

The script combines the results into an action:

| Condition | Action |
|---|---|
| `concerning` and severity of at least 2 | `escalate` |
| `concerning`, or allegation probability of at least 0.5 | `review` |
| Otherwise | `ignore` |

These thresholds are starting points. Validate them on labeled examples before automating decisions.

## Setup

1. Deploy `Microsoft-Decision-1` in your Foundry project and note the resource endpoint and deployment name.
2. Update `endpoint` and `deployment_name` in [classify_news.py](./classify_news.py).
3. Install the dependencies:

   ```powershell
   pip install azure-identity typesafe_sdk
   ```

4. Sign in so `DefaultAzureCredential` can authenticate, for example with `az login`.

## Usage

```powershell
python classify_news.py
```

Example output format:

```text
Allegation reported: <probability>
Classification: <label> (confidence <percent>)
Severity: <score> of 3 (confidence <percent>)
Action: <escalate | review | ignore>
```

Change `news_state` in the `__main__` block, or import `classify_news(state)` to classify your own text.

## News extraction model

[fetch_news.py](./fetch_news.py) calls the existing `extract-news-agent` through
the OpenAI Responses API. Its request explicitly sets `model="gpt-4.1"`, matching
the deployment used in [create_news_extract_agent.py](./create_news_extract_agent.py).
Binding a client with `agent_name` selects the agent endpoint but does not populate
the request's `model` field. Omitting that field can cause a `400 no_model_name` error.

If you change the extraction agent's model deployment, update the model in both
scripts. Keep the classifier's `DEPLOYMENT_NAME` separate: it identifies the
Microsoft-Decision-1 deployment, not the news extraction model.
