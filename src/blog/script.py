import numpy as np
from matplotlib import pyplot as plt

plt.grid()
plt.plot(x := np.linspace(0, 1), x, 'k--', linewidth=0.5)
plt.plot(x := np.linspace(0, 1), y := [3.75 * xx * (1 - xx) for xx in x])
plt.title('Logistic map, $r=3.75$')
plt.xlim([0, 1])
plt.xlabel('$x_n$')
plt.ylabel('$x_{n+1}$')
plt.ylim([0, 1])

rands = [0.1]
for _ in range(6):
    # print(rands[-1])
    rands.append(3.75 * rands[-1] * (1 - rands[-1]))
    plt.arrow(
        x=rands[-2],
        dx=0,
        y=rands[-2],
        dy=rands[-1] - rands[-2],
        width=0.001,
        head_width=0.008,
        color='black',
        zorder=100
    )
    plt.arrow(
        y=rands[-1],
        dy=0,
        x=rands[-2],
        dx=rands[-1] - rands[-2],
        head_width=0.008,
        head_length=0.004,
        color='black',
        zorder=100
    )

    # plt.hlines(
    #     rands[-1],
    #     xmin=rands[-2],
    #     xmax=rands[-1],
    #     linestyles='dotted',
    #     linewidth=1.1,
    #     color='black')

# plt.scatter(rands[:-1], rands[1:], color='red')
plt.show()
