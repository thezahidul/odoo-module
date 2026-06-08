# KPI Management System

The **KPI Management System** is a robust, custom-built Odoo 19 module designed to streamline employee performance appraisals. It automates skill-based evaluation and attendance synchronization, providing a transparent, data-driven approach to human resource management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Stack](#technical-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Business Logic](#business-logic)
- [Maintainer Information](#maintainer-information)

---

## 🚀 Overview

This module empowers HR managers to define custom KPI templates tailored to specific departments. It reduces manual intervention by intelligently syncing with Odoo's native attendance tracking system and calculating weighted performance scores dynamically.

## ✨ Key Features

* **Dynamic Template Engine:** Create and activate department-specific evaluation templates with ease.
* **Automated Attendance Synchronization:** Automatically calculates attendance scores based on real-time check-in/check-out data when the "Attendance" skill is included in a template.
* **Weighted Scoring Logic:** Allows granular control over evaluation metrics by assigning specific weights (totaling 100%) to individual skills.
* **Duplicate Evaluation Prevention:** Built-in Python constraints ensure that an employee cannot be evaluated against the same template on the same date more than once.
* **Unified Interface:** A clean, Odoo-standardized UI for managing evaluation workflows from initiation to final scoring.

## 🛠 Technical Stack

* **Framework:** Odoo 19
* **Programming Language:** Python 3.12
* **Core Dependencies:** `hr`, `hr_attendance`, `base`
* **Data Integrity:** Implemented via custom Odoo constraints and validation for database-level accuracy.

## 📦 Installation

To install this module, follow these steps:

1. Copy the `kpi_management` directory into your Odoo custom addons path.
2. Restart your Odoo service.
3. Activate **Developer Mode** in your Odoo instance.
4. Navigate to **Apps > Update Apps List**.
5. Search for "KPI Management" and click **Install**.
   * *Alternatively, use the command line:*
     ```bash
     ./odoo-bin -c odoo.conf -d <your_db_name> -u kpi_management
     ```

## ⚙️ Configuration

1. **Skill Library:** Navigate to `Configuration > Skill Library` to define your core competencies (e.g., Attendance, Coding Logic, Behavior).
2. **KPI Templates:** Navigate to `Configuration > KPI Templates` to structure your evaluation forms.
    * Add skills to the template lines.
    * Assign weights to ensure the total weight sums to 100%.
    * Click **Activate** to finalize the template.

## 💡 Business Logic

The system's intelligence relies on the `onchange` method for template selection:

* When a template is selected, the system checks for the presence of the "Attendance" skill.
* If found, it automatically calculates the score based on the formula: 
  $$\text{Score} = \left( \frac{\text{Present Days}}{\text{Total Days in Month}} \right) \times 100$$
* This score is populated within the evaluation details to ensure accuracy and auditability.

## 🤝 Maintainer Information

* **Maintainer:** ZENCORE SOLUTIONS LIMITED
* **Lead Developer:** Zahidul Islam
* **Support:** thezahidkhans@gmail.com

---

*License: LGPL-3 | Version: 1.0.0*