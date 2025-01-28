import json


class ReportGenerator:
    def __init__(self, format: str, path: str):
        self.format = format
        self.path = path
        self.generators = {
            "html": self._generate_html,
            "json": self._generate_json,
            "markdown": self._generate_makedown,
        }

    def generate(self, data):
        if self.format not in self.generators:
            raise ValueError(f"Unsupported format: {self.format}")
        return self.generators[self.format](data)

    def _generate_html(self, data):
        """Generate an HTML report of routes and requests with better styling and grouping by method."""
        html_content = """
        <html>
        <head>
            <title>Routes and Requests Report</title>
            <link rel="icon" href="favicon.ico" type="image/x-icon">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    margin: 20px;
                }
                h1 {
                    color: #4CAF50;
                    text-align: center;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                }
                li {
                    margin-bottom: 20px;
                }
                .route {
                    font-size: 22px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                    cursor: pointer;
                }
                .method-group {
                    background-color: #ecf0f1;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 10px;
                    display: none;
                }
                .method-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2980b9;
                    cursor: pointer;
                }
                .hit-count {
                    font-size: 14px;
                    color: #27ae60;
                    font-weight: normal;
                }
                .request-log {
                    background-color: #fff;
                    border-radius: 5px;
                    padding: 10px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 10px;
                }
                .log-item {
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                }
                .log-item:last-child {
                    border-bottom: none;
                }
                .timestamp {
                    color: #888;
                    font-size: 14px;
                }
                .method {
                    font-weight: bold;
                    color: #2980b9;
                }
                .body {
                    font-style: italic;
                    color: #7f8c8d;
                }
            </style>
        </head>
        <body>
            <h1>Routes and Requests Report</h1>
            <ul>
        """

        # Loop through the routes and group logs by HTTP method (GET, POST, etc.)
        for route, logs in data.items():
            html_content += f"<li><div class='route' onclick='toggleMethodGroup(\"{route}\")'>{route}</div>"

            # Group logs by method (GET, POST, etc.)
            method_logs = {}
            for log in logs:
                if log.method not in method_logs:
                    method_logs[log.method] = []
                method_logs[log.method].append(log)

            # Add the method groups with the number of hits
            for method, logs in method_logs.items():
                html_content += f"""
                <div class='method-group' id='{route}_{method}'>
                    <div class='method-title' onclick='toggleMethodLogs(\"{route}_{method}\")'>
                        {method} <span class='hit-count'>Hits: {len(logs)}</span>
                    </div>
                    <div class='request-log'>
                        <ul>
                """

                # List all logs for that method
                for log in logs:
                    body = log.body if isinstance(log.body, str) else json.dumps(log.body, indent=2)
                    html_content += f"""
                    <li class='log-item'>
                        <div><span class='timestamp'>{log.timestamp}</span> - 
                        <span class='method'>{log.method}</span> - 
                        <span class='body'>{body}</span></div>
                    </li>
                    """

                html_content += """
                        </ul>
                    </div>
                </div>
                """

            html_content += "</li>"

        html_content += """
            </ul>

            <script>
            // Function to toggle visibility of method groups (GET, POST, etc.)
            function toggleMethodGroup(route) {
                var groups = document.querySelectorAll('.method-group');
                groups.forEach(function(group) {
                    if (group.id.startsWith(route)) {
                        group.style.display = group.style.display === 'block' ? 'none' : 'block';
                    }
                });
            }

            // Function to toggle visibility of logs under each method
            function toggleMethodLogs(groupId) {
                var methodGroup = document.getElementById(groupId);
                methodGroup.style.display = methodGroup.style.display === 'block' ? 'none' : 'block';
            }

            </script>
        </body>
        </html>
        """

        return html_content

    def _generate_json(self, data):
        import json
        with open(self.path, "w") as file:
            json.dump(data, file)

    def _generate_makedown(self, data):
        with open(self.path, "w") as file:
            file.write(f"# Report\n\n{data}")
