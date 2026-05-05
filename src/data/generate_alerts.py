
"""
Synthetic AML Alert Generator
Simulates a nightly batch export from a legacy Transaction Monitoring System.
Generates 500 alerts (95% False Positives, 5% True Positives).
"""
import json
import random
import uuid
from datetime import datetime, timedelta

# Constants for Generation
NUM_ALERTS = 500
HIGH_RISK_COUNTRIES = ["Panama", "Cyprus", "Cayman Islands", "Malta", "UAE"]
SAFE_COUNTRIES =["UK", "France", "Germany", "USA", "Japan"]

def generate_false_positive():
    """Generates a perfectly innocent transaction that tripped a dumb rule."""
    amount = round(random.uniform(500, 25000), 2)
    return {
        "transaction_amount": f"£{amount}",
        "sender": f"User_{random.randint(1000, 9999)}",
        "receiver": f"Vendor_{random.randint(1000, 9999)}",
        "destination_country": random.choice(SAFE_COUNTRIES),
        "rule_triggered": "LARGE_TRANSFER_ABROAD",
        "context": "Customer paying invoice for overseas software licenses. 3-year account history shows similar monthly payments."
    }

def generate_true_positive():
    """Generates suspicious structuring (smurfing) or shell company behavior."""
    # Smurfing: Sending just under the £10,000 reporting threshold
    amount = round(random.uniform(9900, 9999), 2) 
    return {
        "transaction_amount": f"£{amount}",
        "sender": f"Shell_Corp_{random.randint(100, 999)}",
        "receiver": "Offshore_Holdings_LLC",
        "destination_country": random.choice(HIGH_RISK_COUNTRIES),
        "rule_triggered": "STRUCTURING_THRESHOLD_EVASION",
        "context": "Account opened 3 days ago. Immediate wire transfer just below the £10k limit to a known tax haven. No prior business history."
    }

def main():
    print("🏦 Booting Legacy AML System Simulator...")
    alerts =[]
    
    for i in range(NUM_ALERTS):
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        
        # 5% chance of being a real threat
        if random.random() < 0.05:
            data = generate_true_positive()
            is_threat = True
        else:
            data = generate_false_positive()
            is_threat = False
            
        alert_record = {
            "alert_id": alert_id,
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            "transaction_data": data,
            "ground_truth_is_threat": is_threat # We keep this hidden from Claude!
        }
        alerts.append(alert_record)

    # Save to the raw data folder
    output_path = "data/raw/nightly_alerts.json"
    with open(output_path, "w") as f:
        json.dump(alerts, f, indent=4)

    print(f"✅ Generated {NUM_ALERTS} AML Alerts.")
    print(f"📁 Saved to: {output_path}")

if __name__ == "__main__":
    main()