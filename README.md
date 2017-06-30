# DarwinEye

DarwinEye is a tool for offline visual inspection of evolutionary and swarm optimization algorithms. [Read more about it](https://www.linkedin.com/pulse/conspiracy-darwin-sci-poetry-adailson-filho?published=u)

#How it works

A JSON with the algoritm log must be provided (in a specif format [SOON]), with it DarwinEye will produce a set of graphs/charts for inspecting important aspects of the algorithm process of high dimensional problems, like: Paralel Coordinate, Fitness evolution, Scatter Plot with a special dimension reduction with an variation of sammon's mapping (and it's errors in each epoch).

Dependencies:
- Matplotlib: =< 1.5.3
- Numpy: =< 1.11
- Tkinter
