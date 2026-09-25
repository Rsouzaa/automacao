"""Flask server for the AutomacaoBDD report dashboard."""
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, jsonify, render_template, request, send_file

from dashboard.exports import build_pdf, build_xlsx
from dashboard.local_runner import LocalRunManager
from dashboard.report_service import DEFAULT_REPORT_PATH, load_report


def create_app(report_path=DEFAULT_REPORT_PATH):
    """Create the dashboard application for a Talos JSON report."""
    app = Flask(__name__)
    app.config['REPORT_PATH'] = Path(report_path)
    runner = LocalRunManager(app.config['REPORT_PATH'])

    def local_request():
        origin = request.headers.get('Origin')
        return (request.remote_addr in ('127.0.0.1', '::1')
                and urlsplit(request.host_url).hostname in ('127.0.0.1', 'localhost', '::1')
                and (not origin or origin.rstrip('/') == request.host_url.rstrip('/')))

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/report')
    def report():
        return jsonify(load_report(app.config['REPORT_PATH']))

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    @app.get('/api/run')
    def run_status():
        if not local_request():
            return jsonify({'error': 'Disponível somente no computador local.'}), 403
        return jsonify(runner.snapshot())

    @app.post('/api/run')
    def run_tests():
        if not local_request():
            return jsonify({'error': 'Disponível somente no computador local.'}), 403
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get('url'), str):
            return jsonify({'error': 'Informe uma URL válida.'}), 400
        try:
            state = runner.start(data['url'], data.get('expected_text', ''),
                                 data.get('show_browser', False), data.get('suite', 'url_smoke'))
        except ValueError as error:
            return jsonify({'error': str(error)}), 400
        except RuntimeError as error:
            return jsonify({'error': str(error)}), 409
        return jsonify(state), 202

    @app.get('/api/export/pdf')
    def export_pdf():
        if not app.config['REPORT_PATH'].is_file():
            return jsonify({'error': 'Nenhum relatório disponível.'}), 404
        return send_file(
            build_pdf(load_report(app.config['REPORT_PATH'])), as_attachment=True,
            download_name='automacaobdd-resultados.pdf', mimetype='application/pdf',
        )

    @app.get('/api/export/xlsx')
    def export_xlsx():
        if not app.config['REPORT_PATH'].is_file():
            return jsonify({'error': 'Nenhum relatório disponível.'}), 404
        return send_file(
            build_xlsx(load_report(app.config['REPORT_PATH'])), as_attachment=True,
            download_name='automacaobdd-resultados.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5050, debug=False, use_reloader=False)
