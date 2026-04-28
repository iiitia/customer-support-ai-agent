# Evaluation Results
**Total test cases:** 15  
**Pipeline success rate:** 93.3%  
**Intent accuracy:** 100.0%  
**Urgency accuracy:** 85.7%  
**Exact match (intent + urgency):** 85.7%  
**Needs-human rate:** 28.6%  
**Average confidence:** 0.83  

## Per-case Results

| # | Label | Intent ✓ | Urgency ✓ | Exact | Confidence | Error |
|---|-------|----------|-----------|-------|------------|-------|
| 1 | 01_en_refund_basic | ✅ | ✅ | ✅ | 0.95 | — |
| 2 | 02_en_inquiry_tracking | ✅ | ✅ | ✅ | 0.95 | — |
| 3 | 03_en_complaint_safety | ✅ | ✅ | ✅ | 0.95 | — |
| 4 | 04_ar_refund | ✅ | ✅ | ✅ | 0.90 | — |
| 5 | 05_ar_complaint_damaged | ✅ | ✅ | ✅ | 0.90 | — |
| 6 | 06_en_exchange | ✅ | ❌ | ❌ | 0.95 | — |
| 7 | 07_edge_minimal_input | ✅ | ✅ | ✅ | 0.20 | — |
| 8 | 08_edge_gibberish | ✅ | ✅ | ✅ | 0.20 | — |
| 9 | 09_edge_mixed_language | ✅ | ✅ | ✅ | 0.85 | — |
| 10 | 10_adversarial_escalation_threat | ✅ | ✅ | ✅ | 0.95 | — |
| 11 | 11_adversarial_repeated_contact | ✅ | ✅ | ✅ | 0.95 | — |
| 12 | 12_adversarial_prompt_injection | ❌ | ❌ | ❌ | — | Failed to get a valid response after 2 a |
| 13 | 13_edge_mixed_sentiment | ✅ | ✅ | ✅ | 0.95 | — |
| 14 | 14_en_exchange_wrong_item | ✅ | ❌ | ❌ | 0.95 | — |
| 15 | 15_ar_inquiry | ✅ | ✅ | ✅ | 0.95 | — |
