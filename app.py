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

pgrid = figure(x_range=(-.5, SIZE - .5),
        y_range=(-.5, SIZE - .5),
        plot_width=PLOTSIZE,
        plot_height=PLOTSIZE,
        tools='', toolbar_location=None,
        x_axis_location=None,
        y_axis_location=None,
        background_fill_color='blue')
pgrid.grid.grid_line_color = None
resgriddata = ColumnDataSource(dict(x=data[0]['rx'], y=data[0]['ry']))
agentgriddata = ColumnDataSource(dict(x=data[0]['ax'], y=data[0]['ay']))
pgrid.rect('x', 'y', 1, 1, source=resgriddata, color='green')
pgrid.rect('x', 'y', 1, 1, source=agentgriddata, color='red')

phealth = figure(title='Population health')
phealth.line(range(len(strength)), strength, legend='avg strength')
phealth.line(range(len(age)), age, legend='avg age', color='orange')
healthsource = ColumnDataSource(dict(x=[0], strength=[strength[0]],
    age=[age[0]]))
phealth.circle('x', 'strength', source=healthsource)
phealth.circle('x', 'age', source=healthsource, color='orange')

pgrowth = figure(title='Population growth')
pgrowth.line(range(len(popsize)), popsize, legend='population size')
pgrowth.line(range(len(kills)), kills, color='orange', legend='number of kills')
pgrowth.line(range(len(offspring)), offspring, color='green', legend='number of births')
growthsource = ColumnDataSource(dict(x=[0], popsize=[popsize[0]],
    kills=[kills[0]], offspring=[offspring[0]]))
pgrowth.circle('x', 'popsize', source=growthsource)
pgrowth.circle('x', 'kills', source=growthsource, color='orange')
pgrowth.circle('x', 'offspring', source=growthsource, color='green')

pprofile = figure(title='Population profile', x_axis_label='kills',
        y_axis_label='offspring')
profilesource = ColumnDataSource(dict(age=data[0]['age'],
    strength=data[0]['strength'], kills=data[0]['kills'],
    offspring=data[0]['offspring']))
pprofile.circle('kills', 'offspring', source=profilesource)

def animate_update():
    slider.value = (slider.value + 1) % len(data)


def slider_update(attrname, old, new):
    i = slider.value
    resgriddata.data = dict(x=data[i]['rx'], y=data[i]['ry'])
    agentgriddata.data = dict(x=data[i]['ax'], y=data[i]['ay'])
    healthsource.data = dict(x=[i], strength=[strength[i]],
        age=[age[i]])
    growthsource.data = dict(x=[i], popsize=[popsize[i]],
        kills=[kills[i]], offspring=[offspring[i]])
    profilesource.data = dict(age=data[i]['age'],
        strength=data[i]['strength'], kills=data[i]['kills'],
        offspring=data[i]['offspring'])


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

layout = layout([[pgrid],
    [slider, button],
    [pgrowth], [phealth], [pprofile]])

curdoc().add_root(layout)
