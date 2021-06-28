import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator, AutoMinorLocator
from sklearn.decomposition import PCA
from ims import BaseModel


class PCA_Model(BaseModel):
    
    def __init__(self, dataset, scaling_method=None, **kwargs):
        """
        Wrapper class for scikit learn PCA.
        Adds plots for explained variance ratio,
        loadings and scatter plots of components.

        Parameters
        ----------
        dataset : varies
            Dataset or Spectra

        scaling_method : str, optional
            'standard', 'auto', 'pareto' and 'var' are valid arguments,
            by default None
        """
        super().__init__(dataset, scaling_method)
        self.pca = PCA(**kwargs).fit(self.X)
        self.pc = self.pca.transform(self.X)
        if self.scaling_method is not None and scaling_method != 'standard':
            self.loadings = self.pca.components_ / self.weights
        else:
            self.loadings = self.pca.components_

    def __repr__(self):
        return f'''PCA:
{self.dataset.name},
{self.scaling_method} scaling
'''

    def scatter_plot(self, PC_x=1, PC_y=2, width=9, height=8,
                     hue="Label", style="Label", label=False):
        """
        Scatter plot of principal components

        Parameters
        ----------
        PC_x : int, optional
            PC x axis, by default 1

        PC_y : int, optional
            PC y axis, by default 2

        width : int, optional
            plot width in inches, by default 8

        height : int, optional
            plot height in inches, by default 7
            
        hue : str, optional
            color markers either by 'Label' or by 'Sample',
            by default 'Label'
            
        style : str, optional
            marker style either by 'Label' or by 'Sample',
            by default 'Label'
            
        label : bool, optional
            label data points with sample name,
            by default False

        Returns
        -------
        matplotlib figure
        """
        expl_var = []
        for i in range(1, self.pca.n_components_ + 1):
            expl_var.append(round(self.pca.explained_variance_ratio_[i-1] * 100, 1))
        
        pc_df = pd.DataFrame(
            data=self.pc,
            columns=[f"PC {x}" for x in range(1, self.pca.n_components_ + 1)]
        )
        pc_df['Sample'] = self.dataset.samples
        pc_df['Label'] = self.dataset.labels

        with plt.style.context("seaborn"):
            fig, ax = plt.subplots(figsize=(width, height))
            sns.scatterplot(
                ax=ax,
                x=f"PC {PC_x}",
                y=f"PC {PC_y}",
                data=pc_df,
                hue=hue,
                style=style,
                s=100
            )

            plt.legend(frameon=True, fancybox=True, facecolor="white")
            plt.xlabel(f"PC {PC_x} ({expl_var[PC_x-1]} % of variance)")
            plt.ylabel(f"PC {PC_y} ({expl_var[PC_y-1]} % of variance)")
            
            if label:
                for i, point in pc_df.iterrows():
                    ax.text(point[f"PC {PC_x}"], point[f"PC {PC_y}"],
                            point["Sample"])

        return fig

    def loadings_plot(self, PC=1, color_range=0.1, width=9, height=10):
        """
        Plots loadings of a principle component with the original retention
        and drift time coordinates.

        Parameters
        ----------
        PC : int, optional
            principal component, by default 1

        color_range : int, optional
            color_scale ranges from - color_range to + color_range
            centered at 0

        width : int, optional
            plot width in inches, by default 9

        height : int, optional
            plot height in inches, by default 10

        Returns
        -------
        matplotlib.pyplot.figure
        """        
        # use retention and drift time axis from the first spectrum
        ret_time = self.dataset[0].ret_time
        drift_time = self.dataset[0].drift_time

        loading_pc = self.loadings[PC-1, :].reshape(len(ret_time),
                                                    len(drift_time))

        fig, ax = plt.subplots(figsize=(width, height))

        plt.imshow(
            loading_pc,
            origin="lower",
            aspect="auto",
            cmap="RdBu_r",
            vmin=(-color_range),
            vmax=color_range
            )

        plt.colorbar()

        xlocs, _ = plt.xticks()
        ylocs, _ = plt.yticks()

        rt_ticks = [round(ret_time[int(i)]) for i in ylocs[1:-1]]
        dt_ticks = [round(drift_time[int(i)], 1) for i in xlocs[1:-1]]

        plt.xticks(xlocs[1:-1], dt_ticks)
        plt.yticks(ylocs[1:-1], rt_ticks)

        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        
        plt.xlabel(self.dataset[0]._drift_time_label, fontsize=12)
        plt.ylabel("Retention Time [s]", fontsize=12)
        plt.title(f"PCA Loadings of PC {PC}", fontsize=16)
        return fig

    def scree_plot(self, width=9, height=8, style="seaborn"):
        """
        Plots the explained variance ratio per principal component
        and cumulatively.

        Returns
        -------
        matplotlib.pyplot.figure
        """        
        x = [*range(1, self.pca.n_components_ + 1)]
        y = self.pca.explained_variance_ratio_

        with plt.style.context(style):
            fig, ax = plt.subplots(figsize=(width, height))
            
            for axis in [ax.xaxis, ax.yaxis]:
                axis.set_major_locator(MaxNLocator(integer=True))
            
            plt.xticks(x)
            plt.xlabel("Principal Component", fontsize=12)
            plt.ylabel("Explainded variance ratio [%]", fontsize=12)
            
            ax.plot(x, np.cumsum(y) * 100, label="cumulative")
            ax.plot(x, y * 100, label="per PC")
            
            plt.legend(frameon=True, fancybox=True, facecolor="white")

        return fig