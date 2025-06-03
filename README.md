# 🩺 MedScraper: CT Doctor License + Disciplinary Action Extractor

## 📌 Project Background

A buddy of mine who's an IRS agent approached me with a frustrating but important issue: it's incredibly hard to find reliable information about doctors online. Most platforms are riddled with fake reviews—often paid for by the practitioners themselves—and it’s shockingly tedious to verify whether a doctor has any history of disciplinary actions. The State of Connecticut has this information publicly available, but only through a clunky manual web form.

This is more than just an inconvenience. One growing concern is the unethical overprescription of addictive medications—especially to elderly patients—by certain private practitioners. Once patients are hooked, some doctors raise their prices dramatically, exploiting their dependency and vulnerability. The human and financial consequences of this are devastating.

## 🎯 Project Goal

The long-term goal of this project is to build a **transparent, trustworthy, and publicly accessible database of physicians**, focused on:

- Identifying practitioners with disciplinary history
- Aggregating official documentation (e.g., consent orders, probation notices)
- Flagging patterns of unethical behavior (e.g., overprescribing addictive drugs)
- Creating a tool for investigators, reporters, patients, and families to verify provider history

**Step 1** in this process is developing a scraper that collects disciplinary data directly from the Connecticut state licensing portal.

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Selenium WebDriver** – for navigating and interacting with the CT license lookup portal
- **Requests** – for downloading public disciplinary PDF documents
- **ChromeDriver** – for browser automation
- **CSV output** – for logging and analysis
- *(Planned)* SQLite or Airtable integration for structured storage

---

## 🚦 Phase 1: Complete

✅ Automate CT license portal search  
✅ Iterate through active "Physician / Surgeon" records  
✅ Open detail modals and check for disciplinary history  
✅ Download and save any associated public PDF files  
✅ Log doctor name, license number, and case info in CSV

---

## 🧭 Roadmap

### Phase 2 (Next Steps)
- [ ] Accept input from list of license numbers
- [ ] Add headless mode for server/cloud execution
- [ ] Add retry logic for flaky detail modals or slow pages
- [ ] Improve error logging and data deduplication
- [ ] Output data to structured DB (SQLite/Airtable)

### Phase 3 (Stretch Goals)
- [ ] Cross-reference with Medicare prescription data for red-flag analysis
- [ ] Add keyword OCR extraction from PDFs (e.g., for substance misuse terms)
- [ ] Deploy frontend to visualize doctor histories
- [ ] Enable API endpoint for external queries

---

## 📂 File Structure

```
MedScraper/
├── main.py                 # Main full-page scraper with pagination
├── test.py                 # Lightweight license-specific checker
├── docs/                   # Downloaded PDF disciplinary documents
├── results_log.csv         # Output log (name, license, status, actions)
└── README.md               # Project overview
```

---

## 🙌 Purpose

This tool is designed in the public interest to help make healthcare safer, more accountable, and more transparent. It is especially useful for:

- Government auditors and investigators
- Journalists and watchdog organizations
- Families evaluating long-term care
- Patients seeking trustworthy providers

Suggestions and contributions welcome!
