import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Environment, FileSystemLoader
from urllib.parse import parse_qs
import os


with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/':
            self.render_template('index.html', {'title': 'Главная'})
        elif path == '/about':
            self.render_template('about.html', {'title': 'О компании', 'team': data['team']})
        elif path == '/services':
            self.render_template('services.html', {'title': 'Услуги', 'services': data['services']})
        elif path == '/contact':
            self.render_template('contact.html', {'title': 'Контакты'})
        elif path.startswith('/media/'):
            self.serve_static_file(path)
        else:
            self.send_error(404, "Page Not Found {}".format(self.path))

    def do_POST(self):
        if self.path == '/contact':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = parse_qs(post_data.decode('utf-8'))

            
            name = post_data.get('name', [''])[0]
            message = post_data.get('message', [''])[0]

            
            print(f"Новое сообщение от {name}: {message}")

            
            context = {
                'title': 'Контакты',
                'message_sent': True,
                'name': name
            }
            self.render_template('contact.html', context)

    def render_template(self, template_name, context):
        
        context['company_name'] = data['company_name']
        template = env.get_template(template_name)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(template.render(context).encode('utf-8'))

    def serve_static_file(self, path):
        file_path = '.' + path
        if os.path.exists(file_path):
            self.send_response(200)
            if path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif path.endswith('.png'):
                self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found {}".format(path))

def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Запуск сервера, адрес и порт: localhost:{port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
