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

## 🔄 Gratuity Settlement Work-Flow Cycle

Below is the execution lifecycle of a gratuity record inside the Odoo 19 ecosystem:

```text
  [ Employee Resigns / Retires ]
                 │
                 ▼
     [ Create Gratuity Record ]  ──► (Status: Draft)
                 │
                 ▼
  [ Compute Service Tenure & Base ] ──► Adheres to BD Labor Law 2006
                 │
                 ▼
   [ Compute TDS / Tax Exemption ] ──► Adheres to NBR Regulations
                 │
                 ▼
    [ HR Manager Verification ]  ──► (Status: Confirmed / Approved)
                 │
                 ▼
   [ Finance & Payroll Posting ] ──► (Status: Paid)
                 │
                 ▼
[ Generate & Print A4 PDF Statement ] ──► Multi-Dept Signature Sign-Off
```

## ⚙️ Installation & Configuration

### Prerequisites
Before triggering the module initialization, ensure that your Odoo 19 environment has the core dependencies active and that the host server is configured correctly:
- `hr` (Base Employee Directory)
- `mail` (Enterprise Discussion & Tracking Mixin)
- **External Dependency:** `wkhtmltopdf` (v0.12.5 or v0.12.6 with patched Qt) must be globally accessible in the host system PATH to render custom typography, multi-page breaks, and BDT currency symbols without CSS degradation.

---

### Module Setup & Initial Deployment

1. **Repository Synchronization:** Extract the `hr_gratuity` module directory and copy it directly into your designated Odoo custom addons repository path.
2. **Server-Side Warm Restart:** Force-release any active background zombie processes locking your target deployment port and restart the core Odoo server instance:
   ```bash
   sudo fuser -k 8088/tcp
   ./odoo-bin -c odoo.conf -d dbv19 -u hr_gratuity
   ```