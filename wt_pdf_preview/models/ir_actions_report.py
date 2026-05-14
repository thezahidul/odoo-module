from odoo import models
from odoo.tools.safe_eval import safe_eval, time
import base64

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def action_open_pdf_preview(self, res_ids):
        self.ensure_one()
        if len(res_ids) > 1:
            pdf_parts = []
            for res_id in res_ids:
                try:
                    pdf_content, _ = self._render_qweb_pdf(
                        self.report_name,
                        [res_id]
                    )
                    pdf_parts.append(pdf_content)
                except Exception:
                    pass
            merged_pdf = self._merge_pdfs(pdf_parts)
            pdf_base64 = base64.b64encode(merged_pdf).decode('utf-8')
            filename = "%s (%d records)" % (self.name or 'report', len(res_ids))
        else:
            pdf_content, _ = self._render_qweb_pdf(
                self.report_name,
                res_ids
            )
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            filename = self.name or 'report'
            if self.print_report_name and res_ids:
                try:
                    record = self.env[self.model].browse(res_ids[0])
                    filename = safe_eval(
                        self.print_report_name,
                        {'object': record, 'time': time}
                    )
                except Exception:
                    filename = self.name or 'report'

        return {
            'type': 'ir.actions.client',
            'tag': 'pdf_preview_client_action',
            'name': 'PDF Preview',
            'context': {'dialog_size': 'large'},
            'target': 'new',
            'params': {
                'pdf_base64': pdf_base64,
                'filename': filename + '.pdf',
                'report_id': self.id,
                'res_ids': res_ids,
            }
        }

    def _merge_pdfs(self, pdf_list):
        try:
            from pypdf import PdfWriter, PdfReader
            import io
            writer = PdfWriter()
            for pdf_bytes in pdf_list:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                for page in reader.pages:
                    writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            return output.getvalue()
        except ImportError:
            return pdf_list[0] if pdf_list else b''