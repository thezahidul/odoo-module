# Recruiter Stage Approval Workflow

This Odoo 19 module implements a strict multi-tier validation control system for **Job Positions (`hr.job`)**, ensuring that vacancy recruitment workflows and website publishing operations follow formal corporate approval structures.

## 📌 Features

- **Sequential Status Flow:** Controls the structural lifecycle of recruitment positions:
  `Draft` ➡️ `1st Stage` ➡️ `2nd Stage` ➡️ `Final Stage` ➡️ `Recruitment In Progress (Open)` / `Refused`
- **Strict Server-Side Validation:** Python validation guards intercept unauthorized `write` or status mutations, preventing bypass attempts even if front-end UI buttons are made visible.
- **Automated Activity Delegation:** Seamlessly integrates with `mail.activity.mixin` to schedule deadlined To-Do items inside the assignee’s upper navigation bar icon instantly when a record requires action.
- **Enterprise-Ready Auditing:** Fully leverages Odoo Chatter tracking to archive sequential history stamps showing precisely who authorized or refused requests and when.
- **Safe UI Adaptation:** Automatically adapts to Odoo 19’s default responsive layout without interfering with side-chatter responsive rendering configurations.

---

## 🛠️ Workflow Lifecycle

1. **Draft:** The Job Position profile is initialized. Specific system users must be designated as the **1st Stage Approver**, **2nd Stage Approver**, and **Final Approver**.
2. **1st Stage:** Submitted for review. An automated activity is assigned to the designated *1st Stage Approver*.
3. **2nd Stage:** Upon approval, the pending task is marked as complete, and a new activity is dynamically generated for the *2nd Stage Approver*.
4. **Final Stage:** Sent to the *Final Approver*. At this checkpoint, the system gives the authorized user exclusive rights to either **Publish & Start** or **Refuse** the request.
5. **Open / Refused:** The final termination point. Publishing triggers the automatic synchronization switch for `website_published` to expose the link online.

---

## ⚙️ Installation & Configuration

### Prerequisites
Make sure your custom addons directory contains this module and that the Odoo base recruitment components are active:
- `hr_recruitment`
- `website_hr_recruitment`
- `mail`

### Module Setup
1. Copy the `recruiter_stage_approval` directory into your configured Odoo custom addons repository path.
2. Restart your Odoo server instance.
3. Access your database backend, activate **Developer Mode**, navigate to **Apps**, and execute **Update Apps List**.
4. Search for `Recruiter Stage Approval Workflow` and click **Install** or update via your terminal using:
   ```bash
   ./odoo-bin -c odoo.conf -d your_db_name -u recruiter_stage_approval