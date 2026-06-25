# -*- coding: utf-8 -*-
{
    "name": "My Portfolio Theme",
    "summary": "A clean and professional portfolio website theme.",
    "description": "Custom theme for software developer portfolio showcasing projects and skills.",
    "category": "Website",
    "version": "1.0.0",
    "author": "Zahidul Islam",
    "depends": ["website"],
    "data": [
        "views/pages.xml",
        "views/snippets.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "portfolio/static/src/css/portfolio.css",
            "portfolio/static/src/js/portfolio.js",
        ],
    },
    "images": [
        "static/description/portfolio_screenshot.png",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
