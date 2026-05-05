"""
AML Batch API Retriever & Evaluator
Polls Anthropic for batch completion, downloads the JSONL results, 
and grades the AI against the hidden ground truth.
"""
import os
import json
import logging
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(".env.local")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AML-Batch-Retriever")

# YOUR EXACT BATCH ID
BATCH_ID = "msgbatch_01UeHF6DRjvXvzLh5aGXorXi"

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def clean_llm_json(raw_text: str) -> str:
    """Strips Markdown backticks from LLM output to extract raw JSON."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    return cleaned.strip()

def retrieve_and_evaluate():
    logger.info(f"Checking status for Batch ID: {BATCH_ID}...")
    
    batch = client.messages.batches.retrieve(BATCH_ID)
    status = batch.processing_status
    logger.info(f"Batch Status: {status.upper()}")
    
    if status != "ended":
        logger.warning(f"Batch is still {status}. Please try again in a few minutes.")
        return

    logger.info("Batch complete! Downloading results...")
    results = client.messages.batches.results(BATCH_ID)
    
    with open("data/raw/nightly_alerts.json", "r") as f:
        ground_truth_data = json.load(f)
        truth_map = {alert["alert_id"]: alert["ground_truth_is_threat"] for alert in ground_truth_data}

    total_processed = 0
    correct_identifications = 0
    false_positives_cleared = 0
    
    logger.info("Evaluating AI Performance against Ground Truth...")

    for result in results:
        if result.result.type == "succeeded":
            alert_id = result.custom_id
            ai_text_output = result.result.message.content[0].text
            
            # THE ARCHITECT'S FIX: Scrub the markdown before parsing
            clean_json_string = clean_llm_json(ai_text_output)
            
            try:
                ai_decision = json.loads(clean_json_string)
                ai_flagged_threat = ai_decision.get("is_threat", False)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON for {alert_id}: {clean_json_string}")
                continue

            actual_threat = truth_map.get(alert_id)
            total_processed += 1
            
            if ai_flagged_threat == actual_threat:
                correct_identifications += 1
                if not ai_flagged_threat:
                    false_positives_cleared += 1

    accuracy = (correct_identifications / total_processed) * 100 if total_processed > 0 else 0
    
    print("\n" + "="*50)
    print("📈 AML BATCH PROCESSING REPORT")
    print("="*50)
    print(f"Total Transactions Processed: {total_processed}")
    print(f"AI Accuracy vs Ground Truth:  {accuracy:.2f}%")
    print(f"False Positives Auto-Cleared: {false_positives_cleared}")
    print("\n💰 BUSINESS IMPACT:")
    money_saved = false_positives_cleared * 10 
    print(f"By auto-clearing {false_positives_cleared} false alarms, this nightly batch just saved the bank ~£{money_saved:,.2f} in wasted human investigation hours.")
    print("="*50 + "\n")

if __name__ == "__main__":
    retrieve_and_evaluate()