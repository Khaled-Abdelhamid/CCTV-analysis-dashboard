from bokeh.plotting import figure, show, output_notebook
from bokeh.models import Range1d, Rect, ImageURL, ColumnDataSource, Grid, HoverTool, Circle
output_notebook() 

url = ['http://raw.githubusercontent.com/colour-science/colour/develop/colour/plotting/resources/CIE_1931_Chromaticity_Diagram_CIE_1931_2_Degree_Standard_Observer.png']

source = ColumnDataSource(data=dict(url=[url,]))

hover = HoverTool(tooltips=[("(x,y)", "($x, $y)"), ], point_policy='follow_mouse', rend)

fig = figure(title='CIE 1931 Chromaticity Diagram',
             x_range=Range1d(start=0, end=0.8),
             y_range=Range1d(start=0, end=0.9),
             plot_width=450,
             plot_height=400,
             tools = [hover, 'reset']
            )

fig.image_url(x=0.0, 
              y=1.0, 
              h=1.0, 
              w=1.0, 
              url="url", 
              name='cie',
              source=source,
              level='image')

fig.scatter([.1,.2,.3],[.4,.5,.6], fill_color="red", name='points')

show(fig)