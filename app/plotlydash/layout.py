"""Plotly Dash HTML layout override."""

html_layout = '''
<!DOCTYPE html>
    <html>
        <head>
            <style>  
            </style>  
            {%metas%}
            <title>{%title%}</title>
            {%css%}
        </head>
        <header>
        </header>
        <body>
            {%app_entry%}
            <header >
                {%config%}
                {%scripts%}
                {%renderer%}
            </header>
        </body>
    </html>
'''