import configparser

from flask import Flask, request, Response
from flask_openapi import Swagger

from routes.insitu import insitu_bp
from routes.pages import pages
from routes.categeries import categeries
from routes.exampledb import dbconnect

config = configparser.ConfigParser()
config.read('env.ini')

SECRET_KEY = config['DEFAULT']["SECRET_KEY"]
TITLE = config['DEFAULT']["TITLE"]
DESCRIPTION = config['DEFAULT']["DESCRIPTION"]

app = Flask(__name__)
# Stats(app)
app.jinja_env.autoescape = True

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['TIMEOUT'] = 600
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

prefix_url_api = '/api'
prefix_monitoring = f'{prefix_url_api}/monitoring'
prefix_json = f'{prefix_monitoring}/dump.json'
prefix_url_docs = f'{prefix_url_api}/docs'

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "openapi",
            "route": f"{prefix_url_api}/openapi.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": f"{prefix_url_api}/flasgger_static",
    "swagger_ui": True,
    "specs_route": f"{prefix_url_docs}/",
    "title": TITLE,
    "description": DESCRIPTION,
    "openapi": "3.0.3",
    "version": "1.0.11",
    "swagger_ui_bundle_js": "//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js",
    "swagger_ui_standalone_preset_js": "//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js",
    "jquery_js": "//unpkg.com/jquery@2.2.4/dist/jquery.min.js",
    "swagger_ui_css": "//unpkg.com/swagger-ui-dist@3/swagger-ui.css",
    "components": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "in": "header",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    }
}
app.config["DEBUG"] = True
app.config["flask_profiler"] = {
    "enabled": app.config["DEBUG"],
    "endpointRoot": f"{prefix_monitoring}/",
    "endpointJson": f"{prefix_json}",
    "storage": {
        "engine": "sqlite",
        "db_url": 'jdbc:mariadb://192.168.0.121:3306/pg',
    },
    "basicAuth":{
        "enabled": True,
        "username": "w00t",
        "password": "w00t"
    },
    "samplingInterval": 0.1,
    "maxSamples": 1000,
    "enableMemoryProfiling": True
}


swagger = Swagger(app, config=swagger_config)
app.register_blueprint(insitu_bp, url_prefix=f'{prefix_url_api}/insitu')
app.register_blueprint(pages, url_prefix=f'/')
app.register_blueprint(categeries, url_prefix=f'/categeries')
app.register_blueprint(dbconnect, url_prefix=f'{prefix_url_api}/dbconnect')


@app.route('/robots.txt')
def robots_txt():
    robots_content = "User-agent: *\nDisallow: /private/\n"
    return Response(robots_content, mimetype='text/plain')

if __name__ == '__main__':
    app.run()
