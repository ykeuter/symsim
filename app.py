import numpy as np
from bokeh.layouts import row, layout, column, Spacer, gridplot
from bokeh.plotting import figure, curdoc
from bokeh.models import Button, Slider, ColumnDataSource, DataRange1d, LinearAxis
from symsim import World

SIZE = 10
WINDOWSIZE = 3
PRODRATE = .1
CONSUMRATE = .1
STRENGTH = 1
NUMSTEPS = 10000

np.random.seed(0)
w = World(SIZE, PRODRATE, CONSUMRATE, STRENGTH, WINDOWSIZE)
rx, ry = np.nonzero(w.resourceGrid)
ax, ay = np.nonzero(w.agentGrid)
data = [{'rx': rx, 'ry': ry, 'ax': ax, 'ay': ay,
    'age': [a.age for a in w.situatedAgents],
    'strength': [a.strength for a in w.situatedAgents],
    'kills': [a.kills for a in w.situatedAgents],
    'offspring': [a.offspring for a in w.situatedAgents]}]
kills = [0]
offspring = [0]
for i in xrange(NUMSTEPS):
    o, k = w.step()
    rx, ry = np.nonzero(w.resourceGrid)
    ax, ay = np.nonzero(w.agentGrid)
    data.append({'rx': rx, 'ry': ry, 'ax': ax, 'ay': ay,
        'age': [a.age for a in w.situatedAgents],
        'strength': [a.strength for a in w.situatedAgents],
        'kills': [a.kills for a in w.situatedAgents],
        'offspring': [a.offspring for a in w.situatedAgents]})
    kills.append(k)
    offspring.append(o)
strength = [sum(d['strength']) / len(d['strength']) for d in data]
age = [sum(d['age']) / len(d['age']) for d in data]
popsize = [len(d['age']) for d in data]

pgrid = figure(x_range=(-.5, SIZE - .5), title='Simulation',
        y_range=(-.5, SIZE - .5),
        plot_width=100,
        plot_height=100,
        tools='', toolbar_location=None,
        x_axis_location=None,
        y_axis_location=None,
        background_fill_color='blue')
pgrid.grid.grid_line_color = None
resgriddata = ColumnDataSource(dict(x=data[-1]['rx'], y=data[-1]['ry']))
agentgriddata = ColumnDataSource(dict(x=data[-1]['ax'], y=data[-1]['ay']))
pgrid.rect('x', 'y', 1, 1, source=resgriddata, color='green')
pgrid.rect('x', 'y', 1, 1, source=agentgriddata, color='red')

timesource = ColumnDataSource(dict(x=[len(strength) - 1], strength=[strength[-1]],
    age=[age[-1]], popsize=[popsize[-1]], kills=[kills[-1]],
        offspring=[offspring[-1]]))

phealth = figure(title='Health', width=200, height=100)
phealth.line(range(len(strength)), strength, legend='avg strength')
phealth.line(range(len(age)), age, legend='avg age', color='orange')
phealth.circle('x', 'strength', source=timesource)
phealth.circle('x', 'age', source=timesource, color='orange')
phealth.legend.location = 'top_left'

pgrowth = figure(title='Growth', width=200, height=100, x_range=phealth.x_range)
pgrowth.extra_y_ranges['y2'] = DataRange1d()
pgrowth.add_layout(LinearAxis(y_range_name='y2'), 'right')
r1 = pgrowth.line(range(len(popsize)), popsize, legend='population size')
r2 = pgrowth.line(range(len(kills)), kills, color='orange', y_range_name='y2',
        legend='number of kills',)
r3 = pgrowth.line(range(len(offspring)), offspring, color='green',
        y_range_name='y2', legend='number of births')
pgrowth.y_range.renderers = [r1]
pgrowth.extra_y_ranges['y2'].renderers = [r2, r3]
pgrowth.circle('x', 'popsize', source=timesource)
pgrowth.circle('x', 'kills', source=timesource, color='orange', y_range_name='y2')
pgrowth.circle('x', 'offspring', source=timesource, color='green', y_range_name='y2')
pgrowth.legend.location = 'top_left'

pprofile = figure(title='Profile', x_axis_label='kills',
        y_axis_label='offspring', width=100, height=100,
        toolbar_location='below', toolbar_sticky=False)
profilesource = ColumnDataSource(dict(age=data[-1]['age'],
    strength=data[-1]['strength'], kills=data[-1]['kills'],
    offspring=data[-1]['offspring']))
pprofile.scatter('kills', 'offspring', source=profilesource)

def animate_update():
    slider.value = (slider.value + 1) % len(data)


def slider_update(attrname, old, new):
    i = slider.value
    resgriddata.data = dict(x=data[i]['rx'], y=data[i]['ry'])
    agentgriddata.data = dict(x=data[i]['ax'], y=data[i]['ay'])
    timesource.data = dict(x=[i], strength=[strength[i]],
        age=[age[i]], popsize=[popsize[i]], kills=[kills[i]],
        offspring=[offspring[i]])
    profilesource.data = dict(age=data[i]['age'],
        strength=data[i]['strength'], kills=data[i]['kills'],
        offspring=data[i]['offspring'])


slider = Slider(start=0, end=len(data) - 1, value=len(data) - 1, step=1, title="Step")
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

timeplots = gridplot([[pgrowth], [phealth]], responsive=True,
        toolbar_location='below')
layout = layout([[slider, button],
    [pgrid, pprofile, timeplots]], responsive=True)

curdoc().add_root(layout)
curdoc().title = "SymSim"
