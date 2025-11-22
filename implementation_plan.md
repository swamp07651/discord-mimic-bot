# Discord Mimic Bot Implementation Plan

## Goal Description
Create a Discord bot that mimics 'takenicle'. We will **fine-tune Gemini 1.5 Flash** using the extracted message data to create a custom model that speaks exactly like the target user.

## User Review Required
> [!IMPORTANT]
> **Gemini API Key**: You need a Google AI Studio API key.
> **Fine-tuning**: We will upload the data to Google to fine-tune the model. This might take a while (minutes to hours) depending on the queue.
> **Cost**: Gemini 1.5 Flash fine-tuning is currently free (in preview) or low cost, but check the pricing.

## Proposed Changes

### Data Preparation
#### [NEW] [prepare_finetune_data.py](file:///c:/Users/swamp/.gemini/discord_mimic_bot/prepare_finetune_data.py)
- Converts `cleaned_messages.txt` into JSONL format required for Gemini fine-tuning.
- Structure: `{"messages": [{"role": "user", "content": "context..."}, {"role": "model", "content": "target message"}]}`.
- Since we only have messages (no context), we might need to generate synthetic "prompts" or just use the previous message as context if available (which we didn't strictly preserve in the clean list, but we have in `raw_messages.json`).
- *Correction*: We should use `raw_messages.json` to get context-response pairs if possible, or just train on "continuation" style if supported, or use a simple "Mimic this user" prompt + message.

### Fine-tuning
#### [NEW] [finetune_gemini.py](file:///c:/Users/swamp/.gemini/discord_mimic_bot/finetune_gemini.py)
- Uses `google-generativeai` library to upload data and start a fine-tuning job.

### Bot Implementation
#### [NEW] [bot.py](file:///c:/Users/swamp/.gemini/discord_mimic_bot/bot.py)
- Connects to Discord.
- Uses the **tuned model** via Gemini API to generate responses.

## Verification Plan
### Automated Tests
- None.

### Manual Verification
- Run `finetune_gemini.py` and wait for completion.
- Run `bot.py` with the new model ID.
- Chat with the bot and verify the "takenicle" vibe.
