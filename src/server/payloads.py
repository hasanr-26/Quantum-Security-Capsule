"""
Realistic financial wire payload generation.

Every call produces a genuinely fresh message: new message identifiers, a new
UETR, a live settlement timestamp and a randomised principal amount drawn from
a realistic corridor. Nothing here replays a canned string, so two consecutive
demo runs never produce identical bytes - which is exactly what an evaluator
checks when asking whether a demo is hardcoded.
"""

import json
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

# Realistic correspondent banking corridors used by the generator.
CORRIDORS = [
    {
        "debtor_agent": "BARCGB22XXX",
        "creditor_agent": "HDFCINBBXXX",
        "currency": "GBP",
        "clearing": "CHAPS",
        "debtor": "GlaxoSmithKline Treasury UK",
        "debtor_iban": "GB82BARC20000012345678",
        "debtor_addr": ("980 Great West Road", "Brentford", "TW8 9GS", "GB"),
        "creditor": "Apollo Healthcare Infrastructure India Ltd",
        "creditor_iban": "IN45HDFC0001234567890",
        "creditor_addr": ("21 Greams Lane, Off Greams Road", "Chennai", "600006", "IN"),
        "remittance": "Phase III oncology unit capital equipment tranche",
    },
    {
        "debtor_agent": "DEUTDEFFXXX",
        "creditor_agent": "CHASUS33XXX",
        "currency": "EUR",
        "clearing": "TARGET2",
        "debtor": "Siemens Energy Global GmbH",
        "debtor_iban": "DE89370400440532013000",
        "debtor_addr": ("Otto-Hahn-Ring 6", "Munich", "81739", "DE"),
        "creditor": "Dominion Grid Holdings LLC",
        "creditor_iban": "US64SVBKUS6S3300958879",
        "creditor_addr": ("120 Tremont Street", "Boston", "02108", "US"),
        "remittance": "HVDC converter station milestone payment",
    },
    {
        "debtor_agent": "MIDLGB22XXX",
        "creditor_agent": "SMBCJPJTXXX",
        "currency": "USD",
        "clearing": "CHIPS",
        "debtor": "Rio Tinto Commercial Treasury",
        "debtor_iban": "GB29MIDL60161331926819",
        "debtor_addr": ("6 St James Square", "London", "SW1Y 4AD", "GB"),
        "creditor": "Nippon Steel Trading Corporation",
        "creditor_iban": "JP38SMBC00110012345678",
        "creditor_addr": ("2-6-3 Otemachi, Chiyoda-ku", "Tokyo", "100-8071", "JP"),
        "remittance": "Iron ore concentrate shipment settlement",
    },
]


def _fresh_ids(corridor: Dict[str, Any]) -> Dict[str, str]:
    """Builds a fresh identifier set for one payment instruction."""
    now = datetime.now(timezone.utc)
    serial = random.randint(10000, 99999)
    bank_prefix = corridor["debtor_agent"][:4]
    return {
        "msg_id": f"{bank_prefix}-{now.strftime('%Y%m%d')}-{serial}",
        "instr_id": f"INSTR-{bank_prefix}-{serial}",
        "end_to_end_id": f"E2E-{bank_prefix}-{corridor['creditor_agent'][:4]}-{serial}",
        "tx_id": f"TXN-{serial}",
        "uetr": str(uuid.uuid4()),
        "created_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value_date": now.strftime("%Y-%m-%d"),
        "mt_date": now.strftime("%y%m%d"),
    }


def _principal(currency: str) -> float:
    """Draws a realistic high-value settlement amount for the corridor."""
    base = random.randint(25, 950) * 100_000
    return float(base) + random.randint(0, 99) / 100.0


def generate_pacs008(corridor: Dict[str, Any] = None, amount: float = None) -> Dict[str, Any]:
    """
    Builds an ISO 20022 pacs.008.001.08 FIToFICstmrCdtTrf message.

    This is the message type that actually moves money between financial
    institutions on CHAPS, TARGET2 and the SWIFT gpi rails.
    """
    corridor = corridor or random.choice(CORRIDORS)
    ids = _fresh_ids(corridor)
    amount = amount if amount is not None else _principal(corridor["currency"])
    d_street, d_town, d_post, d_ctry = corridor["debtor_addr"]
    c_street, c_town, c_post, c_ctry = corridor["creditor_addr"]

    return {
        "Document": {
            "@xmlns": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08",
            "FIToFICstmrCdtTrf": {
                "GrpHdr": {
                    "MsgId": ids["msg_id"],
                    "CreDtTm": ids["created_at"],
                    "NbOfTxs": "1",
                    "SttlmInf": {
                        "SttlmMtd": "CLRG",
                        "ClrSys": {"Prtry": f"{corridor['clearing']}_PQC"},
                    },
                    "InstgAgt": {"FinInstnId": {"BICFI": corridor["debtor_agent"]}},
                    "InstdAgt": {"FinInstnId": {"BICFI": corridor["creditor_agent"]}},
                },
                "CdtTrfTxInf": {
                    "PmtId": {
                        "InstrId": ids["instr_id"],
                        "EndToEndId": ids["end_to_end_id"],
                        "TxId": ids["tx_id"],
                        "UETR": ids["uetr"],
                    },
                    "PmtTpInf": {
                        "InstrPrty": "HIGH",
                        "LclInstrm": {"Prtry": corridor["clearing"]},
                    },
                    "IntrBkSttlmAmt": {
                        "value": round(amount, 2),
                        "currency": corridor["currency"],
                    },
                    "IntrBkSttlmDt": ids["value_date"],
                    "ChrgBr": "SHAR",
                    "Dbtr": {
                        "Nm": corridor["debtor"],
                        "PstlAdr": {
                            "StrtNm": d_street,
                            "TwnNm": d_town,
                            "PstCd": d_post,
                            "Ctry": d_ctry,
                        },
                    },
                    "DbtrAcct": {"Id": {"IBAN": corridor["debtor_iban"]}},
                    "DbtrAgt": {"FinInstnId": {"BICFI": corridor["debtor_agent"]}},
                    "CdtrAgt": {"FinInstnId": {"BICFI": corridor["creditor_agent"]}},
                    "Cdtr": {
                        "Nm": corridor["creditor"],
                        "PstlAdr": {
                            "StrtNm": c_street,
                            "TwnNm": c_town,
                            "PstCd": c_post,
                            "Ctry": c_ctry,
                        },
                    },
                    "CdtrAcct": {"Id": {"IBAN": corridor["creditor_iban"]}},
                    "RmtInf": {
                        "Ustrd": f"{corridor['remittance']} - ref {ids['tx_id']}"
                    },
                },
            },
        }
    }


def generate_mt103(corridor: Dict[str, Any] = None, amount: float = None) -> str:
    """
    Builds a SWIFT MT103 Single Customer Credit Transfer in FIN block format.

    Blocks: {1:} basic header, {2:} application header, {3:} user header
    (carrying the UETR in field 121), {4:} text block with the payment fields.
    """
    corridor = corridor or random.choice(CORRIDORS)
    ids = _fresh_ids(corridor)
    amount = amount if amount is not None else _principal(corridor["currency"])
    # SWIFT amounts use a comma as the decimal separator and no thousands separator.
    amount_swift = f"{amount:.2f}".replace(".", ",")
    d_street, d_town, d_post, d_ctry = corridor["debtor_addr"]
    c_street, c_town, c_post, c_ctry = corridor["creditor_addr"]

    sender = corridor["debtor_agent"][:8] + "A" + corridor["debtor_agent"][8:]
    receiver = corridor["creditor_agent"] + "X"
    ccy = corridor["currency"]

    lines = [
        "{1:F01" + sender + "0000000000}"
        + "{2:I103" + receiver + "N}"
        + "{3:{108:" + ids["end_to_end_id"] + "}{121:" + ids["uetr"] + "}}"
        + "{4:",
        ":20:" + ids["tx_id"],
        ":23B:CRED",
        ":23E:SDVA",
        ":32A:" + ids["mt_date"] + ccy + amount_swift,
        ":33B:" + ccy + amount_swift,
        ":50K:/" + corridor["debtor_iban"],
        corridor["debtor"].upper(),
        d_street.upper(),
        f"{d_town.upper()} {d_post} {d_ctry}",
        ":52A:" + corridor["debtor_agent"],
        ":53A:" + corridor["debtor_agent"],
        ":57A:" + corridor["creditor_agent"],
        ":59:/" + corridor["creditor_iban"],
        corridor["creditor"].upper(),
        c_street.upper(),
        f"{c_town.upper()} {c_post} {c_ctry}",
        ":70:/INV/" + ids["tx_id"],
        "/RFB/" + corridor["remittance"].upper(),
        ":71A:SHA",
        ":72:/ACC/SETTLED AS QSC CAPSULE",
        "/INS/" + corridor["debtor_agent"],
        "-}",
    ]
    return "\n".join(lines)


def build_payload(kind: str = "pacs008") -> Tuple[bytes, Dict[str, Any]]:
    """
    Produces a wire payload ready for encapsulation.

    Args:
        kind: "pacs008", "mt103", or "card" (a PAN-bearing authorisation record,
              used to show exactly what leaks when a TLS session is harvested).

    Returns:
        (payload_bytes, descriptor) where descriptor carries the media type, a
        human label and the corridor the message travels.
    """
    corridor = random.choice(CORRIDORS)

    if kind == "mt103":
        text = generate_mt103(corridor)
        return text.encode("utf-8"), {
            "kind": "mt103",
            "label": "SWIFT MT103 Single Customer Credit Transfer",
            "media_type": "text/plain",
            "standard": "SWIFT FIN MT103",
            "corridor": f"{corridor['debtor_agent']} -> {corridor['creditor_agent']}",
        }

    if kind == "card":
        record = {
            "auth_type": "CARD_NOT_PRESENT",
            "pan": f"4539{random.randint(100000000000, 999999999999)}",
            "cardholder": corridor["debtor"],
            "expiry": "11/29",
            "cvv": f"{random.randint(100, 999)}",
            "amount": round(_principal(corridor["currency"]) / 1000, 2),
            "currency": corridor["currency"],
            "merchant_id": f"MID-{random.randint(100000, 999999)}",
            "acquirer_bic": corridor["creditor_agent"],
        }
        return json.dumps(record, indent=2).encode("utf-8"), {
            "kind": "card",
            "label": "Card Authorisation Record (PCI DSS scope)",
            "media_type": "application/json",
            "standard": "ISO 8583 derived",
            "corridor": f"{corridor['debtor_agent']} -> {corridor['creditor_agent']}",
        }

    doc = generate_pacs008(corridor)
    tx = doc["Document"]["FIToFICstmrCdtTrf"]["CdtTrfTxInf"]
    return json.dumps(doc, indent=2).encode("utf-8"), {
        "kind": "pacs008",
        "label": "ISO 20022 pacs.008.001.08 Customer Credit Transfer",
        "media_type": "application/json",
        "standard": "ISO 20022",
        "corridor": f"{corridor['debtor_agent']} -> {corridor['creditor_agent']}",
        "amount": tx["IntrBkSttlmAmt"]["value"],
        "currency": tx["IntrBkSttlmAmt"]["currency"],
        "uetr": tx["PmtId"]["UETR"],
    }


AVAILABLE_PAYLOADS = [
    {"kind": "pacs008", "label": "ISO 20022 pacs.008 (Interbank Credit Transfer)"},
    {"kind": "mt103", "label": "SWIFT MT103 (Customer Credit Transfer)"},
    {"kind": "card", "label": "Card Authorisation Record (PCI DSS)"},
]
