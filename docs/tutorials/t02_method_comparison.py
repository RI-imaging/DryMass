import matplotlib.pylab as plt
import numpy as np


def dot_boxplot(ax, data, colors, labels, **kwargs):
    """Combined box and scatter plot"""
    box_list = []

    for ii in range(len(data)):
        # set same random state for every scatter plot
        rs = np.random.RandomState(42).get_state()
        np.random.set_state(rs)
        y = data[ii]
        x = np.random.normal(ii+1, 0.15, len(y))
        plt.plot(x, y, 'o', alpha=0.5, color=colors[ii])
        box_list.append(y)

    ax.boxplot(box_list,
               sym="",
               medianprops={"color": "black", "linestyle": "solid"},
               widths=0.3,
               labels=labels,
               **kwargs)
    plt.grid(axis="y")


if __name__ == "__main__":
    ri_data = [
        np.loadtxt("sphere_image_rytov-sc_statistics.txt", usecols=(1,)),
        np.loadtxt("sphere_image_rytov_statistics.txt", usecols=(1,)),
        np.loadtxt("sphere_image_projection_statistics.txt", usecols=(1,)),
        np.loadtxt("sphere_edge_projection_statistics.txt", usecols=(1,)),
        ]
    colors = ["#E48620", "#DE2400", "#6e559d", "#048E00"]
    labels = ["image rytov-sc", "image rytov",
              "image projection", "edge projection"]

    plt.figure(figsize=(8, 5))
    ax = plt.subplot(111, title="HL60 (DHM)")
    ax.set_ylabel("refractive index")
    dot_boxplot(ax=ax, data=ri_data, colors=colors, labels=labels)
    plt.tight_layout()
    plt.show()
