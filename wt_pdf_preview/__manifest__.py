{
    'name': 'PDF Preview',
    'version': '19.0.1.0.0',
    'author': 'Warlock Technologies',
    'website': 'http://warlocktechnologies.com',
    'support': 'support@warlocktechnologies.com',
    'category': 'base',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'wt_pdf_preview/static/src/js/pdf_preview.js',
            'wt_pdf_preview/static/src/css/style.css',
        ],
    },
    'images': ['static/images/wt_pdf_preview.png'],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}