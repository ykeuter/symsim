import numpy as np
from bokeh.layouts import layout
from bokeh.plotting import figure, curdoc
from bokeh.models import Button, Slider, ColumnDataSource
from symsim import World

SIZE = 10
WINDOWSIZE = 3
PRODRATE = .1
CONSUMRATE = .1
STRENGTH = 1
NUMSTEPS = 1000

PLOTSIZE = 600

np.random.seed(0)
w = World(SIZE, PRODRATE, CONSUMRATE, STRENGTH, WINDOWSIZE)
rx, ry = np.nonzero(w.resourceGrid)
ax, ay = np.nonzero(w.agentGrid)
data = [{'rx': rx, 'ry': ry, 'ax': ax, 'ay': ay}]
for i in xrange(NUMSTEPS):
    w.step()
    rx, ry = np.nonzero(w.resourceGrid)
    ax, ay = np.nonzero(w.agentGrid)
    data.append({'rx': rx, 'ry': ry, 'ax': ax, 'ay': ay})

p = figure(x_range=(-.5, SIZE - .5),
        y_range=(-.5, SIZE - .5),
        plot_width=PLOTSIZE,
        plot_height=PLOTSIZE,
        tools='', toolbar_location=None,
        x_axis_location=None,
        y_axis_location=None,
        background_fill_color='blue')
p.grid.grid_line_color = None

source1 = ColumnDataSource(dict(x=data[0]['rx'], y=data[0]['ry']))
source2 = ColumnDataSource(dict(x=data[0]['ax'], y=data[0]['ay']))
p.rect('x', 'y', 1, 1, source=source1, color='green')
p.rect('x', 'y', 1, 1, source=source2, color='red')

def animate_update():
    slider.value = (slider.value + 1) % len(data)


def slider_update(attrname, old, new):
    source1.data = dict(x=data[slider.value]['rx'], y=data[slider.value]['ry'])
    source2.data = dict(x=data[slider.value]['ax'], y=data[slider.value]['ay'])

slider = Slider(start=0, end=len(data) - 1, value=0, step=1, title="Step")
slider.on_change('value', slider_update)


def animate():
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)

button = Button(label='► Play', width=60)
button.on_click(animate)

layout = layout([[p], [slider, button]])

curdoc().add_root(layout)
