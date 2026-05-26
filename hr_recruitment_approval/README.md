# HR Recruitment Approval Workflow

This Odoo 19 module provides a secure and automated multi-level approval system for Job Positions, along with a dynamic recruitment pipeline that supports professional Offer Letter generation and email automation.

---

## 📌 Key Features

* **Multi-Level Job Approval:** Enforces a three-tier approval hierarchy (**1st Stage ➔ 2nd Stage ➔ Final Stage**) before a job position can be published.
* **Automated Workflow:** Uses Odoo `mail.activity` to notify the designated approvers via the system's activity bar (clock icon).
* **Candidate Pipeline:** Manages the recruitment flow from initial application to contract proposal.
* **Dynamic Offer Letters:** Generates professional, ready-to-print PDF offer letters with auto-filled candidate and job details.
* **Email Automation:** Built-in integration to send offer letters directly to candidates via email using pre-configured templates.

---

## 🛠️ Workflow Lifecycle

### 1. Job Approval
1.  **Creation:** HR creates a Job Position and assigns specific approvers for each stage.
2.  **Submission:** The user submits the job for the first level of approval.
3.  **Approval Chain:** Each designated approver receives a system notification, reviews the request, and approves it to move to the next stage.
4.  **Publishing:** Upon final approval, the Job Position becomes eligible for website publishing.

### 2. Recruitment & Offer Generation
* **Pipeline Management:** Recruiters move applicants through the standard Odoo recruitment pipeline (**Qualification ➔ Interview ➔ Contract Proposal**).
* **Offer Letter:** Once at the 'Contract Proposal' stage, the "Print offer" button generates a custom PDF including:
    * Company Header & Logo.
    * Candidate details.
    * Job specifics (Department, Title, Employment Type).
    * Proposed Joining Date (from the *Availability* field).
    * Salary package.

---

## ⚙️ Installation & Configuration

1.  **Prerequisites:** Ensure your Odoo instance has `hr_recruitment` and `mail` modules installed.
2.  **Path:** Copy the `hr_recruitment_approval` directory into your custom addons folder.
3.  **Upgrade:** Restart your Odoo server and update your apps list.
4.  **Install:** Install the module from the Apps dashboard or via terminal:

```bash
./odoo-bin -c odoo.conf -d your_db_name -u hr_recruitment_approval
```