import re

# We use simple regex/keywords to catch the most obvious scam signatures.
# This serves as a fast, deterministic layer that doesn't rely on the LLM.

RED_FLAG_PATTERNS = {
    "impersonation_of_authority": [
        r"\b(cbi|ed|customs|police|trai|narcotics|cyber cell|rbi)\b",
        r"supreme court",
        r"fedex.*customs",
        r"telecom regulatory authority",
        r"department of telecommunications"
    ],
    "urgency_and_isolation": [
        r"do not disconnect",
        r"stay on the call",
        r"stay on the line",
        r"don't tell your family",
        r"do not share this",
        r"arrest warrant",
        r"immediate arrest",
        r"legal action will be taken",
        r"within [0-9]+ hours"
    ],
    "financial_demands": [
        r"safe account",
        r"rbi verification",
        r"verification account",
        r"transfer funds",
        r"pay the penalty",
        r"security deposit",
        r"clearance fee",
        r"refundable.*deposit",
        r"share.*otp"
    ],
    "fake_portals_and_documents": [
        r"skype call",
        r"whatsapp video call",
        r"fir copy",
        r"case number",
        r"confidentiality agreement"
    ]
}

def evaluate_rules(text: str) -> list[str]:
    """
    Evaluates the input text against deterministic red flag patterns.
    
    Args:
        text: The transcript or message to analyze.
        
    Returns:
        A list of triggered red flag categories.
    """
    triggered_flags = []
    
    # Normalize text for easier matching (lowercase)
    normalized_text = text.lower()
    
    for flag_category, patterns in RED_FLAG_PATTERNS.items():
        for pattern in patterns:
            # We use re.IGNORECASE just to be safe, though text is lowered
            if re.search(pattern, normalized_text, re.IGNORECASE):
                # Clean up category name for display
                display_name = flag_category.replace("_", " ").title()
                triggered_flags.append(display_name)
                break # Move to next category once triggered
                
    return triggered_flags