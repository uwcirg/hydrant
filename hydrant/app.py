from flask import Flask
import logging
from pythonjsonlogger.jsonlogger import JsonFormatter
from werkzeug.middleware.proxy_fix import ProxyFix

from hydrant.audit import audit_log_init, audit_entry
from hydrant.views import base_blueprint
from hydrant.logserverhandler import LogServerHandler


def create_app(testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('hydrant')
    app.config.from_object('hydrant.config')
    app.config['TESTING'] = testing

    register_blueprints(app)
    configure_logging(app)
    configure_proxy(app)

    return app


def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(base_blueprint)


def configure_logging(app):
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))
    app.logger.debug(
        "hydrant logging initialized",
        extra={'tags': ['testing', 'logging', 'app']})

    if not app.config['LOGSERVER_URL']:
        return

    audit_log_init(app)
    audit_entry(
        "hydrant <event> logging initialized",
        extra={'tags': ['testing', 'logging', 'events']})


def configure_proxy(app):
    """Add werkzeug fixer to detect headers applied by upstream reverse proxy"""
    if app.config.get('PREFERRED_URL_SCHEME', '').lower() == 'https':
        app.wsgi_app = ProxyFix(
            app=app.wsgi_app,

            # trust X-Forwarded-Host
            x_host=1,

            # trust X-Forwarded-Port
            x_port=1,
        )

