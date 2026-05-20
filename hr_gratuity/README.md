# HR Gratuity Settlement Management

An enterprise-grade, standalone Odoo 19 module configured to automate, manage, and audit corporate employee gratuity funds in strict compliance with the statutory provisions of the **Bangladesh Labor Act 2006**.

---

## 🚀 Key Features

* **Independent Ledger Engine:** Completely isolates the `hr.gratuity` transactional model from standard employee master data to ensure audit integrity.
* **Statutory Compliance Rules:** * Automatically applies the 30-day basic salary multiplier for employees with 1–5 continuous years of tenure.
  * Dynamically escalates to a 45-day multiplier for continuous service profiles exceeding 5 years.
* **Automated Tax Auditing:** Computes Tax Deducted at Source (TDS) seamlessly while enforcing National Board of Revenue (NBR) approved statutory tax exemption limits.
* **Pixel-Perfect A4 Documents:** Generates clean, corporate-paged PDF Gratuity Settlement Statements complete with dynamic letterheads, breakdown lines, and a multi-department signature loop (**Employee, HR, Accounts, Management**).
* **Smart HR Integration:** Embeds interactive Smart Buttons inside employee profiles to track real-time accumulated gratuity statistics instantly.

---

## 🛠️ System Architecture & Directories

```text
hr_gratuity/
├── models/             # Business logic & compliance algorithms
├── views/              # Form, Tree, and Smart Button views
├── report/             # Document layouts & A4 print specifications
├── security/           # Access rights & record rules
├── README.md           # Module documentation & feature list
├── __init__.py         # Python initialization
└── __manifest__.py     # Module manifest configuration