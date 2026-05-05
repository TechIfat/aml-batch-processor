"""
AML Batch API Submitter (Anthropic Native)
Formats raw JSON alerts into Anthropic's native Batch Array format,
and dispatches them directly to the cloud for 50%-discounted asynchronous processing.
"""
import os
import json
import logging
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(".env.local")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AML-Batch-Submitter")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Use the exact model string that worked for your workspace previously
MODEL_NAME = "claude-haiku-4-5-20251001" 

def submit_anthropic_batch():
    """Reads the 500 alerts, formats them as Anthropic Requests, and submits the batch."""
    input_file = "data/raw/nightly_alerts.json"
    
    logger.info(f"Reading {input_file}...")
    with open(input_file, "r") as f:
        alerts = json.load(f)
        
    logger.info("Formatting data into Anthropic Batch Requests...")
    
    # We build a massive array of requests in RAM
    batch_requests = []
    
    for alert in alerts:
        # We extract ONLY the transaction_data, stripping out the ground_truth so the AI has to figure it out!
        transaction_data = alert["transaction_data"]
        
        # EXAM CONCEPT: Anthropic Batch Request Schema
        request_obj = {
            "custom_id": alert["alert_id"], # We use our alert ID to map the answers later!
            "params": {
                "model": MODEL_NAME,
                "max_tokens": 300,
                "temperature": 0,
                "system": "You are a bank AML investigator. Analyze the transaction and output STRICTLY valid JSON with two keys: 'is_threat' (boolean) and 'reason' (string). Do not output any markdown formatting or conversational text.",
                "messages":[
                    {
                        "role": "user",
                        "content": f"Analyze this transaction: {json.dumps(transaction_data)}"
                    }
                ]
            }
        }
        batch_requests.append(request_obj)
            
    logger.info(f"✅ Formatted {len(batch_requests)} records.")
    
    # 2. Trigger the Batch Job directly with the array!
    logger.info("Submitting payload to Anthropic Message Batches API (50% Cost Reduction Mode)...")
    
    message_batch = client.messages.batches.create(
        requests=batch_requests
    )
    
    logger.info("🎉 BATCH JOB SUBMITTED SUCCESSFULLY!")
    logger.info("=" * 50)
    logger.info(f"BATCH ID: {message_batch.id}")
    logger.info("=" * 50)
    logger.info("Save this Batch ID. We will need it for Sprint 3 to retrieve the results!")

if __name__ == "__main__":
    submit_anthropic_batch()