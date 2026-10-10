"""Static content for the demo database.

Requirement lists summarise the public form instructions at https://www.uscis.gov
and are for demonstration only. Fees change, so they are never hard-coded here.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RequirementSeed:
    title: str
    description: str
    is_required: bool = True


@dataclass(frozen=True)
class FormSeed:
    form_code: str
    title: str
    description: str
    official_url: str
    requirements: tuple[RequirementSeed, ...]


@dataclass(frozen=True)
class UserSeed:
    email: str
    name: str


@dataclass(frozen=True)
class ChecklistSeed:
    """`completed` and `notes` are keyed by 0-based position in the form's requirements."""
    user_email: str
    form_code: str
    status: str
    completed: frozenset[int]
    notes: dict[int, str]


USERS = (
    UserSeed("maria@example.com", "Maria Gonzalez"),
    UserSeed("james@example.com", "James Okafor"),
)

FORMS = (
    FormSeed(
        "I-130",
        "Petition for Alien Relative",
        "Used by a U.S. citizen or permanent resident to establish a family relationship with a relative who wants to immigrate.",
        "https://www.uscis.gov/i-130",
        (
            RequirementSeed("Signed Form I-130", "Complete every applicable part and sign the form."),
            RequirementSeed("Filing fee", "Check the current fee on uscis.gov before paying."),
            RequirementSeed("Proof of petitioner's status", "Birth certificate, U.S. passport, naturalization certificate, or a copy of the green card."),
            RequirementSeed("Proof of family relationship", "Marriage certificate for a spouse, or birth certificate showing the parent-child relationship."),
            RequirementSeed("Proof that prior marriages ended", "Divorce decree, annulment, or death certificate for each prior marriage of either spouse.", False),
            RequirementSeed("Passport-style photos", "One photo each of the petitioner and the beneficiary; only needed when filing for a spouse.", False),
            RequirementSeed("English translations", "Certified translation of every document not in English.", False),
        ),
    ),
    FormSeed(
        "I-485",
        "Application to Register Permanent Residence or Adjust Status",
        "Used by a person in the United States to apply for a green card without leaving the country.",
        "https://www.uscis.gov/i-485",
        (
            RequirementSeed("Signed Form I-485", "Complete every applicable part and sign the form."),
            RequirementSeed("Filing fee", "Check the current fee on uscis.gov before paying."),
            RequirementSeed("Passport-style photos", "Two identical color photos taken within the last 30 days."),
            RequirementSeed("Government-issued photo ID", "Copy of a passport or other photo identification."),
            RequirementSeed("Birth certificate", "Copy of the long-form birth certificate with an English translation if needed."),
            RequirementSeed("Passport page and I-94", "Copy of the passport page with the visa and admission stamp, plus the I-94 record."),
            RequirementSeed("Medical exam (Form I-693)", "Completed by a USCIS-designated civil surgeon and submitted in a sealed envelope."),
            RequirementSeed("Affidavit of Support (Form I-864)", "Required for most family-based applicants; filed by the financial sponsor."),
            RequirementSeed("Evidence of eligibility category", "Approved I-130 or receipt notice, job offer letter, or other proof of the basis for the green card."),
            RequirementSeed("Court records", "Certified arrest and court dispositions if you have ever been arrested or charged.", False),
            RequirementSeed("Concurrent Forms I-765 and I-131", "Optional work permit and travel document applications filed with the I-485.", False),
        ),
    ),
    FormSeed(
        "I-765",
        "Application for Employment Authorization",
        "Used to request a work permit (Employment Authorization Document) in the United States.",
        "https://www.uscis.gov/i-765",
        (
            RequirementSeed("Signed Form I-765", "Complete every applicable part and sign the form."),
            RequirementSeed("Filing fee", "Check the current fee on uscis.gov; some categories are exempt."),
            RequirementSeed("Passport-style photos", "Two identical color photos taken within the last 30 days."),
            RequirementSeed("Government-issued photo ID", "Copy of a passport or other photo identification."),
            RequirementSeed("Copy of Form I-94", "Arrival/departure record showing your current status."),
            RequirementSeed("Evidence of eligibility category", "For example the I-485 receipt notice if you are applying under category (c)(9)."),
            RequirementSeed("Previous work permit", "Copy of the front and back of any Employment Authorization Document you were issued before.", False),
        ),
    ),
    FormSeed(
        "N-400",
        "Application for Naturalization",
        "Used by a permanent resident to apply for U.S. citizenship.",
        "https://www.uscis.gov/n-400",
        (
            RequirementSeed("Signed Form N-400", "Complete every applicable part and sign the form."),
            RequirementSeed("Filing fee", "Check the current fee on uscis.gov; a reduced fee or fee waiver may apply."),
            RequirementSeed("Permanent Resident Card", "Copy of the front and back of your green card."),
            RequirementSeed("Marriage certificate and spouse's citizenship proof", "Needed when applying after three years as the spouse of a U.S. citizen.", False),
            RequirementSeed("Trip records", "Details and evidence for any trip outside the U.S. of six months or more.", False),
            RequirementSeed("Selective Service registration", "Proof of registration if you are a male who lived in the U.S. between ages 18 and 26.", False),
            RequirementSeed("Court records", "Certified arrest and court dispositions if you have ever been arrested or charged.", False),
            RequirementSeed("Tax transcripts", "IRS tax transcripts if you owe overdue taxes or filed as a nonresident.", False),
            RequirementSeed("Medical disability waiver (Form N-648)", "Only for applicants requesting an exception to the English and civics tests.", False),
        ),
    ),
    FormSeed(
        "I-90",
        "Application to Replace Permanent Resident Card",
        "Used by a permanent resident to renew or replace a green card.",
        "https://www.uscis.gov/i-90",
        (
            RequirementSeed("Signed Form I-90", "Complete every applicable part and sign the form."),
            RequirementSeed("Filing and biometrics fee", "Check the current fees on uscis.gov before paying."),
            RequirementSeed("Copy of current green card", "Front and back; if it was lost or stolen submit another government-issued ID instead."),
            RequirementSeed("Name-change evidence", "Marriage certificate or court order if your name changed.", False),
            RequirementSeed("Police report", "Only if the card was stolen.", False),
        ),
    ),
    FormSeed(
        "I-131",
        "Application for Travel Document",
        "Used to request advance parole, a reentry permit, or a refugee travel document.",
        "https://www.uscis.gov/i-131",
        (
            RequirementSeed("Signed Form I-131", "Complete every applicable part and sign the form."),
            RequirementSeed("Filing fee", "Check the current fee on uscis.gov; some categories are exempt."),
            RequirementSeed("Passport-style photos", "Two identical color photos taken within the last 30 days."),
            RequirementSeed("Government-issued photo ID", "Copy of a passport or other photo identification."),
            RequirementSeed("Evidence of eligibility", "For example the I-485 receipt notice for advance parole, or the green card for a reentry permit."),
        ),
    ),
)

CHECKLISTS = (
    ChecklistSeed(
        "maria@example.com", "I-485", "IN_PROGRESS",
        frozenset({0, 2, 3, 4}),
        {1: "Waiting for payday to buy the money order", 6: "Civil surgeon appointment on Nov 3"},
    ),
    ChecklistSeed(
        "maria@example.com", "I-765", "IN_PROGRESS",
        frozenset({0, 2}),
        {},
    ),
    ChecklistSeed(
        "james@example.com", "N-400", "COMPLETED",
        frozenset(range(9)),
        {2: "Scanned both sides"},
    ),
    ChecklistSeed(
        "james@example.com", "I-90", "IN_PROGRESS",
        frozenset({0}),
        {},
    ),
)
