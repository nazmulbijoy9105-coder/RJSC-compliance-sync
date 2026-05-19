"""
Bangladesh Compliance Rules Engine
Deterministic calculation of all corporate compliance deadlines, penalties, and obligations.
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from dateutil.relativedelta import relativedelta

class BangladeshComplianceRules:
    """
    Deterministic compliance rules engine for Bangladesh corporate law.
    Calculates all filing deadlines, penalties, and compliance obligations
    based on company metadata.
    """

    # RJSC Filing Deadlines (in days relative to trigger event)
    RJSC_DEADLINES = {
        "agm": {"days_after_fy_end": 180, "form": None, "description": "Annual General Meeting"},
        "schedule_x": {"days_after_agm": 21, "form": "Schedule X", "description": "Annual Return"},
        "balance_sheet": {"days_after_agm": 30, "form": "Balance Sheet & P&L", "description": "Audited Financial Statements"},
        "form_23b": {"days_after_auditor_appointment": 30, "form": "Form 23B", "description": "Auditor Appointment Notice"},
        "director_change": {"days_after_event": 14, "form": "Form XII", "description": "Change in Directors"},
        "share_transfer": {"days_after_event": 60, "form": "Form III/IV", "description": "Transfer of Shares"},
        "capital_increase": {"days_after_event": 15, "form": "Form XV", "description": "Increase in Share Capital"},
        "address_change": {"days_after_event": 28, "form": "Form VI", "description": "Change of Registered Address"},
        "moa_amendment": {"days_after_event": 28, "form": "Form VIII", "description": "Amendment to MOA/AOA"},
        "charge_creation": {"days_after_event": 21, "form": "Form XVIII", "description": "Creation of Charge/Mortgage"},
        "charge_modification": {"days_after_event": 21, "form": "Form XIX", "description": "Modification of Charge"},
        "charge_satisfaction": {"days_after_event": 21, "form": "Form XXVIII", "description": "Satisfaction of Charge"},
    }

    # NBR Tax Deadlines
    TAX_DEADLINES = {
        "corporate_tax_return": {"month": 3, "day": 15, "description": "Corporate Income Tax Return"},
        "advance_tax_q1": {"month": 9, "day": 15, "description": "Advance Tax Q1 Installment"},
        "advance_tax_q2": {"month": 12, "day": 15, "description": "Advance Tax Q2 Installment"},
        "advance_tax_q3": {"month": 3, "day": 15, "description": "Advance Tax Q3 Installment"},
        "advance_tax_q4": {"month": 6, "day": 15, "description": "Advance Tax Q4 Installment"},
        "vat_return": {"frequency": "monthly", "day": 15, "description": "VAT Return (Mushak 9.1)"},
        "tds_statement_q1": {"month": 4, "day": 25, "description": "TDS Statement Q1"},
        "tds_statement_q2": {"month": 7, "day": 25, "description": "TDS Statement Q2"},
        "tds_statement_q3": {"month": 10, "day": 25, "description": "TDS Statement Q3"},
        "tds_statement_q4": {"month": 1, "day": 25, "description": "TDS Statement Q4"},
    }

    # BSEC Corporate Governance (Public Companies Only)
    BSEC_DEADLINES = {
        "q1_financial_report": {"days_after_quarter_end": 45, "description": "Q1 Financial Report"},
        "q2_financial_report": {"days_after_quarter_end": 45, "description": "Q2 Financial Report (Half-Yearly)"},
        "q3_financial_report": {"days_after_quarter_end": 45, "description": "Q3 Financial Report"},
        "annual_report": {"days_after_fy_end": 180, "description": "Annual Report with Corporate Governance Disclosure"},
        "corporate_governance_certificate": {"days_after_agm": 30, "description": "Corporate Governance Compliance Certificate"},
        "director_shareholding_disclosure": {"days_after_fy_end": 30, "description": "Director Shareholding Disclosure"},
        "price_sensitive_info": {"immediate": True, "description": "Price Sensitive Information Disclosure"},
    }

    # Penalty Structure
    PENALTIES = {
        "rjsc_daily_fine": 500,  # BDT per day
        "rjsc_director_fine": 10000,  # BDT per director for serious default
        "tax_late_filing": 0.02,  # 2% monthly interest
        "tax_non_filing": 0.10,  # 10% of assessed tax
        "bsec_penalty": 100000,  # BDT up to for listed companies
    }

    @staticmethod
    def get_fiscal_year_dates(incorporation_date: date, fiscal_year_end: str = "06-30") -> List[Tuple[date, date]]:
        """Generate fiscal year start/end dates from incorporation to current date."""
        mm, dd = map(int, fiscal_year_end.split("-"))
        current_date = date.today()
        fiscal_years = []

        first_fy_end = date(incorporation_date.year, mm, dd)
        if first_fy_end < incorporation_date:
            first_fy_end = date(incorporation_date.year + 1, mm, dd)

        fy_start = incorporation_date
        fy_end = first_fy_end

        while fy_start <= current_date:
            fiscal_years.append((fy_start, fy_end))
            fy_start = fy_end + timedelta(days=1)
            fy_end = date(fy_start.year + (1 if mm <= 6 else 0), mm, dd)
            if fy_end < fy_start:
                fy_end = date(fy_start.year + 1, mm, dd)

        return fiscal_years

    @classmethod
    def calculate_rjsc_events(cls, company, fiscal_year: Tuple[date, date]) -> List[Dict]:
        """Calculate all RJSC compliance events for a fiscal year."""
        fy_start, fy_end = fiscal_year
        events = []
        year_label = f"{fy_start.year}-{str(fy_end.year)[-2:]}"

        # AGM
        agm_deadline = fy_end + timedelta(days=cls.RJSC_DEADLINES["agm"]["days_after_fy_end"])
        events.append({
            "event_type": "agm",
            "title": f"Annual General Meeting FY {year_label}",
            "description": f"AGM must be held within 6 months of fiscal year end ({fy_end.strftime('%d-%b-%Y')})",
            "due_date": datetime.combine(agm_deadline, datetime.min.time()),
            "fiscal_year": year_label,
            "form": None,
            "priority": "high"
        })

        # Schedule X (Annual Return)
        schedule_x_deadline = agm_deadline + timedelta(days=cls.RJSC_DEADLINES["schedule_x"]["days_after_agm"])
        events.append({
            "event_type": "schedule_x",
            "title": f"Annual Return (Schedule X) FY {year_label}",
            "description": "Filed with RJSC within 21 days of AGM. Includes shareholder list, director particulars.",
            "due_date": datetime.combine(schedule_x_deadline, datetime.min.time()),
            "fiscal_year": year_label,
            "form": "Schedule X",
            "priority": "high"
        })

        # Balance Sheet & P&L
        bs_deadline = agm_deadline + timedelta(days=cls.RJSC_DEADLINES["balance_sheet"]["days_after_agm"])
        events.append({
            "event_type": "balance_sheet",
            "title": f"Balance Sheet & Profit/Loss Account FY {year_label}",
            "description": "Audited financial statements filed with RJSC within 30 days of AGM. Must include Digital Verification Code (DVC).",
            "due_date": datetime.combine(bs_deadline, datetime.min.time()),
            "fiscal_year": year_label,
            "form": "Balance Sheet & P&L",
            "priority": "high"
        })

        return events

    @classmethod
    def calculate_tax_events(cls, company, fiscal_year: Tuple[date, date]) -> List[Dict]:
        """Calculate all NBR tax compliance events for a fiscal year."""
        fy_start, fy_end = fiscal_year
        events = []
        year_label = f"{fy_start.year}-{str(fy_end.year)[-2:]}"

        # Corporate Tax Return
        tax_due_month = (fy_end.month + 8) % 12 or 12
        tax_due_year = fy_end.year + (fy_end.month + 8) // 12
        tax_deadline = date(tax_due_year, tax_due_month, 15)

        events.append({
            "event_type": "corporate_tax_return",
            "title": f"Corporate Income Tax Return FY {year_label}",
            "description": "Filed by 15th of 9th month after fiscal year end. Penalty: 2% monthly interest + up to 10% of tax assessed.",
            "due_date": datetime.combine(tax_deadline, datetime.min.time()),
            "fiscal_year": year_label,
            "form": "IT-11G",
            "priority": "urgent"
        })

        # Advance Tax (4 quarterly installments)
        for q, (month, day, desc) in enumerate([(9, 15, "Q1"), (12, 15, "Q2"), (3, 15, "Q3"), (6, 15, "Q4")], 1):
            adv_year = fy_start.year if month > 6 else fy_end.year
            adv_deadline = date(adv_year, month, day)
            if fy_start <= adv_deadline <= fy_end + timedelta(days=365):
                events.append({
                    "event_type": f"advance_tax_q{q}",
                    "title": f"Advance Tax Installment {desc} FY {year_label}",
                    "description": f"Quarterly advance tax installment. Due {adv_deadline.strftime('%d-%b-%Y')}.",
                    "due_date": datetime.combine(adv_deadline, datetime.min.time()),
                    "fiscal_year": year_label,
                    "form": "Challan",
                    "priority": "high"
                })

        # VAT Return (Monthly)
        current_month = fy_start.replace(day=1)
        while current_month <= fy_end:
            vat_deadline = (current_month + relativedelta(months=1)).replace(day=15)
            if vat_deadline <= date.today() + timedelta(days=365):
                events.append({
                    "event_type": "vat_return",
                    "title": f"VAT Return (Mushak 9.1) - {current_month.strftime('%b %Y')}",
                    "description": "Monthly VAT return due by 15th of following month. Penalty: Tk 10,000 or 5% of tax due.",
                    "due_date": datetime.combine(vat_deadline, datetime.min.time()),
                    "fiscal_year": year_label,
                    "form": "Mushak 9.1",
                    "priority": "high"
                })
            current_month += relativedelta(months=1)

        return events

    @classmethod
    def calculate_bsec_events(cls, company, fiscal_year: Tuple[date, date]) -> List[Dict]:
        """Calculate BSEC corporate governance events for public listed companies."""
        if not getattr(company, 'is_listed', False):
            return []

        fy_start, fy_end = fiscal_year
        events = []
        year_label = f"{fy_start.year}-{str(fy_end.year)[-2:]}"

        quarters = [
            ("Q1", 9, 30, "q1_financial_report"),
            ("Q2", 12, 31, "q2_financial_report"),
            ("Q3", 3, 31, "q3_financial_report"),
        ]

        for label, month, day, event_key in quarters:
            quarter_end = date(fy_end.year if month <= 6 else fy_start.year, month, day)
            if quarter_end < fy_start:
                quarter_end = date(fy_start.year, month, day)

            report_deadline = quarter_end + timedelta(days=cls.BSEC_DEADLINES[event_key]["days_after_quarter_end"])
            events.append({
                "event_type": event_key,
                "title": f"{label} Financial Report FY {year_label}",
                "description": "Quarterly financial report due within 45 days of quarter end.",
                "due_date": datetime.combine(report_deadline, datetime.min.time()),
                "fiscal_year": year_label,
                "form": "BSEC Quarterly Report",
                "priority": "urgent"
            })

        # Corporate Governance Certificate
        agm_deadline = fy_end + timedelta(days=cls.RJSC_DEADLINES["agm"]["days_after_fy_end"])
        cg_deadline = agm_deadline + timedelta(days=cls.BSEC_DEADLINES["corporate_governance_certificate"]["days_after_agm"])
        events.append({
            "event_type": "corporate_governance_certificate",
            "title": f"Corporate Governance Compliance Certificate FY {year_label}",
            "description": "Certified by practicing accountant/company secretary (not statutory auditor). Mandatory under BSEC Corporate Governance Code 2023.",
            "due_date": datetime.combine(cg_deadline, datetime.min.time()),
            "fiscal_year": year_label,
            "form": "CG Certificate",
            "priority": "urgent"
        })

        return events

    @classmethod
    def calculate_trade_license_event(cls, company) -> Optional[Dict]:
        """Calculate trade license renewal event."""
        expiry = getattr(company, 'trade_license_expiry', None)
        if not expiry:
            return None

        if isinstance(expiry, datetime):
            expiry = expiry.date()

        return {
            "event_type": "trade_license_renewal",
            "title": f"Trade License Renewal - {getattr(company, 'trade_license_number', 'N/A')}",
            "description": f"Trade license expires {expiry.strftime('%d-%b-%Y')}. Renewal required before expiry to avoid penalty.",
            "due_date": datetime.combine(expiry, datetime.min.time()),
            "fiscal_year": None,
            "form": "Trade License Application",
            "priority": "high"
        }

    @classmethod
    def generate_full_compliance_calendar(cls, company) -> List[Dict]:
        """Generate complete compliance calendar for a company."""
        inc_date = getattr(company, 'incorporation_date', None)
        if not inc_date:
            return []

        if isinstance(inc_date, datetime):
            inc_date = inc_date.date()

        fy_end_str = getattr(company, 'fiscal_year_end', '06-30')
        fiscal_years = cls.get_fiscal_year_dates(inc_date, fy_end_str)
        all_events = []

        for fy in fiscal_years:
            all_events.extend(cls.calculate_rjsc_events(company, fy))
            all_events.extend(cls.calculate_tax_events(company, fy))
            all_events.extend(cls.calculate_bsec_events(company, fy))

        tl_event = cls.calculate_trade_license_event(company)
        if tl_event:
            all_events.append(tl_event)

        all_events.sort(key=lambda x: x["due_date"])

        cutoff = datetime.now() - timedelta(days=365)
        all_events = [e for e in all_events if e["due_date"] >= cutoff or e["due_date"].year >= datetime.now().year - 1]

        return all_events

    @classmethod
    def calculate_penalty(cls, event_type: str, days_overdue: int, company_type: str = "private") -> int:
        """Calculate penalty amount for overdue filing."""
        if days_overdue <= 0:
            return 0

        if event_type in ["schedule_x", "balance_sheet", "agm"]:
            daily_fine = cls.PENALTIES["rjsc_daily_fine"]
            return min(days_overdue * daily_fine, 50000)
        elif event_type == "corporate_tax_return":
            return days_overdue * 100
        elif event_type.startswith("vat_return"):
            return 10000
        elif event_type in ["q1_financial_report", "q2_financial_report", "q3_financial_report", 
                          "corporate_governance_certificate", "director_shareholding_disclosure"]:
            return cls.PENALTIES["bsec_penalty"] if company_type == "public" else 0
        return 0

    @classmethod
    def get_event_priority(cls, event_type: str, days_remaining: int) -> str:
        """Determine priority based on event type and urgency."""
        if days_remaining < 0:
            return "urgent"
        elif days_remaining <= 7:
            return "urgent"
        elif days_remaining <= 14:
            return "high"
        elif days_remaining <= 30:
            return "high"
        elif event_type in ["corporate_tax_return", "agm", "corporate_governance_certificate"]:
            return "high"
        else:
            return "medium"

# Export
compliance_rules = BangladeshComplianceRules()
