import sys
import os

# Ensure Python can find the detection module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detection.rules import evaluate_rules

def main():
    print("Testing Rule-Based Detection Engine\n")
    
    test_cases = [
        {
            "name": "CBI Digital Arrest Scam",
            "text": "Hello, I am calling from the CBI. There is a case number 8472 against you for money laundering. Do not disconnect this Skype call. You must transfer funds to the RBI verification account immediately or you will face immediate arrest."
        },
        {
            "name": "FedEx Customs Scam",
            "text": "Your FedEx package was stopped by customs because it contains illegal items. We will connect you to the cyber cell now. Please share the OTP."
        },
        {
            "name": "Safe Bank Notification (Should not flag)",
            "text": "Your salary of Rs. 50,000 has been credited to your account. Have a great day!"
        }
    ]
    
    for case in test_cases:
        print(f"--- Case: {case['name']} ---")
        print(f"Input: {case['text']}")
        flags = evaluate_rules(case['text'])
        print(f"Triggered Flags ({len(flags)}): {flags}\n")

if __name__ == "__main__":
    main()
