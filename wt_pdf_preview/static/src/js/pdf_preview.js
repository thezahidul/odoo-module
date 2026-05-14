/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, xml, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class PdfPreviewClientAction extends Component {
    static template = xml`
        <div style="display:flex; flex-direction:column; width:100%; height:80vh;">
            <div style="padding:8px 12px; border-bottom:1px solid #ddd; display:flex; gap:8px; background:#fff;">
                <button class="btn btn-primary btn-sm" t-on-click="onPrint">Print</button>
                <button class="btn btn-secondary btn-sm" t-on-click="onDownload">Download</button>
                <button class="btn btn-light btn-sm" t-on-click="onClose">Close</button>
            </div>
            <iframe
                t-ref="pdfIframe"
                style="flex:1; width:100%; min-height:70vh; border:none; display:block;"
                type="application/pdf"
            />
        </div>
        <style>
            .o_dialog footer { display: none !important; }
        </style>
    `;

    static props = ["*"];

    setup() {
        this.iframe = useRef("pdfIframe");
        this.action = useService("action");

        onMounted(() => {
            const base64 = this.props.action.params.pdf_base64;
            const byteChars = atob(base64);
            const byteNums = new Array(byteChars.length);
            for (let i = 0; i < byteChars.length; i++) {
                byteNums[i] = byteChars.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNums);
            const blob = new Blob([byteArray], { type: 'application/pdf' });
            const url = URL.createObjectURL(blob);
            this.iframe.el.src = url;
        });
    }

    onPrint() {
        this.iframe.el.contentWindow.print();
    }

    onDownload() {
        const base64 = this.props.action.params.pdf_base64;
        const filename = this.props.action.params.filename;
        const link = document.createElement('a');
        link.href = 'data:application/pdf;base64,' + base64;
        link.download = filename;
        link.click();
    }

    onClose() {
        this.action.doAction({ type: 'ir.actions.act_window_close' });
    }
}

registry.category("actions").add("pdf_preview_client_action", PdfPreviewClientAction);

registry.category("ir.actions.report handlers").add("pdf_preview_handler", async (action, options, env) => {
    if (action.report_type !== "qweb-pdf") {
        return false;
    }

    const orm = env.services.orm;
    const actionService = env.services.action;

    const reportIds = await orm.search("ir.actions.report", [
        ["report_name", "=", action.report_name]
    ]);

    if (!reportIds.length) return false;

    const activeIds = (action.context && action.context.active_ids) || 
                      (action.context && action.context.active_id 
                        ? [action.context.active_id] 
                        : []);

    if (!activeIds.length) return false;

    const result = await orm.call(
        "ir.actions.report",
        "action_open_pdf_preview",
        [[reportIds[0]], activeIds]
    );

    await actionService.doAction(result);
    return true;
});