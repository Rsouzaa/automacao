"""Flask server for the AutomacaoBDD report dashboard."""
from pathlib import Path

from flask import Flask, jsonify, render_template, send_file

from dashboard.exports import build_pdf, build_xlsx
from dashboard.report_service import DEFAULT_REPORT_PATH, load_report


def create_app(report_path=DEFAULT_REPORT_PATH):
    """Create the dashboard application for a Talos JSON report."""
    app = Flask(__name__)
    app.config['REPORT_PATH'] = Path(report_path)

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/report')
    def report():
        return jsonify(load_report(app.config['REPORT_PATH']))

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    @app.get('/api/export/pdf')
    def export_pdf():
        return send_file(
            build_pdf(load_report(app.config['REPORT_PATH'])), as_attachment=True,
            download_name='automacaobdd-resultados.pdf', mimetype='application/pdf',
        )

    @app.get('/api/export/xlsx')
    def export_xlsx():
        return send_file(
            build_xlsx(load_report(app.config['REPORT_PATH'])), as_attachment=True,
            download_name='automacaobdd-resultados.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5050, debug=True)