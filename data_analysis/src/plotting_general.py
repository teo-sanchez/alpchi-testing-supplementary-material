import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.lines import Line2D
from scipy import stats
from scipy.stats import pearsonr
from matplotlib.gridspec import GridSpec

from typing import List
import numpy as np
import pandas as pd
from plottable import Table, ColumnDefinition
from plottable.cmap import normed_cmap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec
from scipy.stats import ttest_ind



from src.data_processing import Metrics
import pdb
stop = pdb.set_trace

colors = {
    "deletion": "#ee8e2e",
    "addition": "#007390",
    "fail": "#c90000",
    "check": "#0400ff",
    "interaction": "#e47d24",
    "reflexion": "#acedff",
    "success": "#008400",
    "uncertainty": "#7c3f9d",
    "baseline": "#888888",
}

def darken_color(color, amount=0.7):
    """
    Darkens a given color by a specified amount.
    `amount` should be a value between 0 and 1.
    """
    import matplotlib.colors as mc
    import colorsys

    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

def lighten_color(color, amount=0.7):
    """
    Lightens a given color by a specified amount.
    `amount` should be a value between 0 and 1.
    """
    return darken_color(color, 1 / amount)

def adjust_percentages(percentages):
    """
    Adjusts percentages so they sum to 100 after rounding.
    
    Args:
        percentages (list or np.array): List of unrounded percentages.

    Returns:
        list: Adjusted integers that sum to 100.
    """
    # Step 1: Round down percentages to integers
    rounded = np.floor(percentages).astype(int)
    # Step 2: Calculate the discrepancy
    discrepancy = 100 - rounded.sum()
    # Step 3: Distribute the discrepancy
    fractional_parts = percentages - rounded  # Remaining fractional parts
    adjustment_indices = np.argsort(fractional_parts)[::-1]  # Largest fractions first
    for i in range(abs(discrepancy)):
        if discrepancy > 0:  # Need to add
            rounded[adjustment_indices[i]] += 1
        elif discrepancy < 0:  # Need to subtract
            rounded[adjustment_indices[i]] -= 1
    return rounded.tolist()

# ! 2.1 Overall strategy

def swarm_diamond_number_of_test_cases(metrics: Metrics,
                                       filename: str = None,
                                       ax: matplotlib.axes.Axes = None,
                                       **kwargs: dict) -> None:
    

    # Number of test cases
    data = metrics.get_final_number_of_tests_per_participant().copy()
    data_baseline = metrics.get_final_number_of_tests_per_participant_baseline().copy()

    # Labels for the two groups (customisable via kwargs)
    label_testers = kwargs.get("label_testers", "Testers")
    label_annotators = kwargs.get("label_annotators", "Annotators")
    group_order = kwargs.get("group_order", [label_testers, label_annotators])

    # Add a grouping column so the two datasets plot on separate y ticks
    data["Group"] = label_testers
    data_baseline["Group"] = label_annotators

    # Welch t-test between testers and annotators (because of unequal sample size and probable unequal variances)
    t_stat, p_value = stats.ttest_ind(data["Total test cases"], data_baseline["Total test cases"], equal_var=False)
    print(f"Welch t-test: t={t_stat:.3f}, p={p_value:.3f}")

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (5, 1)))

    
    # Swarmplot
    sns.swarmplot(data=data, 
                  x="Total test cases",
                  y="Group",
                  order=group_order,
                  size=kwargs.get("markersize", 5), 
                  marker="o",
                  orient="h",
                  palette=[lighten_color(colors["addition"], 0.5)],
                  alpha=kwargs.get("alpha_markers", 0.6),
                  ax=ax)
    
    # Swarmplot for baseline
    sns.swarmplot(data=data_baseline, 
                  x="Total test cases",
                  y="Group",
                  order=group_order,
                  size=kwargs.get("markersize", 5), 
                  marker="o",
                  orient="h", 
                  palette=[darken_color(colors["baseline"])],
                  alpha=kwargs.get("alpha_markers", 0.7),
                  ax=ax)
    
    # Point plot for the mean and std
    sns.pointplot(data=data, 
                  x="Total test cases",
                  y="Group",
                  order=group_order,
                  orient="h",
                  estimator=np.mean,
                  markers="d", 
                  linestyles="", 
                  markersize=kwargs.get("markersize", 7),linewidth=kwargs.get("linewidth", 2),
                  color=lighten_color(colors["addition"], 0.8), 
                  ax=ax)
    
    # Point plot for baseline mean and std
    sns.pointplot(data=data_baseline, 
                  x="Total test cases",
                  y="Group",
                  order=group_order,
                  orient="h",
                  estimator=np.mean,
                  markers="d", 
                  linestyles="", 
                  markersize=kwargs.get("markersize", 7),linewidth=kwargs.get("linewidth", 2),
                  color=lighten_color(colors["baseline"], 0.7), 
                  ax=ax)
    
    # Add stats annotation in the top-right corner. Also indicate the type of test
    ax.text(0.99, 0.95, f"Welch t-test p={p_value:.3f}", 
            horizontalalignment='right',
            verticalalignment='top',
            transform=ax.transAxes,
            fontsize=kwargs.get("stats_fontsize", 10))
    
    # Axis labels (with smaller fontsize)
    ax.set_ylabel(kwargs.get("ylabel", "Nb. of tests"), fontsize=kwargs.get("ylabel_fontsize", 10))

    # Fontsize of the y and x ticks
    ax.tick_params(axis='y', labelsize=kwargs.get("ytick_fontsize", 10))
    ax.tick_params(axis='x', labelsize=kwargs.get("xtick_fontsize", 10))

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel(kwargs.get("xlabel", ""))
    if (ax_param is None and filename is not None):
        plt.savefig(filename, bbox_inches='tight')


def swarm_diamond_fail_ratio(metrics: Metrics,
                                       filename: str = None,
                                       ax: matplotlib.axes.Axes = None,
                                       **kwargs: dict) -> None:
    

    # Fail ratio
    data = metrics.get_fail_ratio_per_participant().copy()
    data_baseline = metrics.get_fail_ratio_per_participant_baseline().copy()

    # Labels for the two groups (customisable via kwargs)
    label_testers = kwargs.get("label_testers", "Testers")
    label_annotators = kwargs.get("label_annotators", "Annotators")
    group_order = kwargs.get("group_order", [label_testers, label_annotators])

    # Add a grouping column so the two datasets plot on separate y ticks
    data["Group"] = label_testers
    data_baseline["Group"] = label_annotators

    # Welch t-test between testers and annotators (because of unequal sample size and probable unequal variances)
    t_stat, p_value = stats.ttest_ind(data["Fail ratio"], data_baseline["Fail ratio"], equal_var=False)
    print(f"Welch t-test: t={t_stat:.3f}, p={p_value:.3f}")

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (5, 1)))

    # Swarmplot
    sns.swarmplot(data=data, 
                  x="Fail ratio",
                  y="Group",
                  order=group_order,
                  size=kwargs.get("markersize", 5), 
                  marker="o",
                  orient="h", 
                  palette=[lighten_color(colors["fail"], 0.7)],
                  alpha=kwargs.get("alpha_markers", 0.7),
                  ax=ax)
    
    # Swarmplot for baseline
    sns.swarmplot(data=data_baseline, 
                  x="Fail ratio",
                  y="Group",
                  order=group_order,
                  size=kwargs.get("markersize", 5), 
                  marker="o",
                  orient="h", 
                  palette=[darken_color(colors["baseline"])],
                  alpha=kwargs.get("alpha_markers", 0.7),
                  ax=ax)
    
    # Point plot for the mean and std
    sns.pointplot(data=data, 
                  x="Fail ratio",
                  y="Group",
                  order=group_order,
                  orient="h", 
                  estimator=np.mean, 
                  markers="d", 
                  linestyles="", 
                  markersize=kwargs.get("markersize", 7),
                  linewidth=kwargs.get("linewidth", 2),
                  color=darken_color(colors["fail"]), 
                  ax=ax)
    
    # Point plot for baseline mean and std
    sns.pointplot(data=data_baseline, 
                  x="Fail ratio",
                  y="Group",
                  order=group_order,
                  orient="h", 
                  estimator=np.mean, 
                  markers="d", 
                  linestyles="", 
                  markersize=kwargs.get("markersize", 7),
                  linewidth=kwargs.get("linewidth", 2),
                  color=lighten_color(colors["baseline"], 0.7),
                  ax=ax)
    
    # Horizontal dashed line for the baseline
    # ax.axvline(fail_ratio_baseline, 
    #            color=colors["baseline"], 
    #            linestyle="--", 
    #            linewidth=1.5,
    #            label="Error rate of the pre-trained model from independant annotators' data")

    # Add stats annotation in the top-right corner. Also indicate the type of test
    ax.text(0.99, 0.28, f"Welch t-test p={p_value:.3f}", 
            horizontalalignment='right',
            verticalalignment='top',
            transform=ax.transAxes,
            fontsize=kwargs.get("stats_fontsize", 10))
    
    # Graph settings
    ax.set_ylabel(kwargs.get("ylabel", "Fail ratio"))

    # Fontsize of the y and x ticks
    ax.tick_params(axis='y', labelsize=kwargs.get("ytick_fontsize", 10))
    ax.tick_params(axis='x', labelsize=kwargs.get("xtick_fontsize", 10))

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel(kwargs.get("xlabel", ""))
    ax.set_xlim(kwargs.get("xlim", (15, 45)))
    ax.set_xticklabels([f"{int(tick)}%" for tick in ax.get_xticks()])
    
    if (ax_param is None and filename is not None):
        plt.legend(loc='upper left', 
               bbox_to_anchor=kwargs.get("bbox_to_anchor", (-0.03, -0.4)),
               frameon=False)
        plt.savefig(filename, bbox_inches='tight')

def swarm_diamond_ratio_checks_added(metrics: Metrics,
                                        filename: str = None,
                                        ax: matplotlib.axes.Axes = None,
                                        **kwargs: dict) -> None:
    
    # Ratio checks added
    data = metrics.get_ratio_checks_added_per_participant()
    ax_param = ax
    # Rename x-axis label

    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (5, 0.5)))
    
    # Swarmplot
    sns.swarmplot(data,
                    x="Ratio checks/added",
                    size=kwargs.get("markersize", 5),
                    marker="o",
                    orient="h",
                    palette=[lighten_color(colors["check"], 0.7)],
                    alpha=kwargs.get("alpha_markers", 0.7),
                    ax=ax)
    
    # Point plot for the mean and std
    sns.pointplot(data,
                    x="Ratio checks/added",
                    orient="h",
                    estimator=np.mean,
                    markers="d",
                    linestyles="",
                    markersize=kwargs.get("markersize", 7),
                    linewidth=kwargs.get("linewidth", 2),
                    color=darken_color(colors["check"]),
                    ax=ax)
    
    # Invert the y-axis
    ax.invert_yaxis()

    # Set the only x tick's label
    ax.set_yticks([0])
    ax.set_yticklabels(["Testers"], fontsize=kwargs.get("ytick_fontsize", 10))

    # Fontsize of the y and x ticks
    ax.tick_params(axis='y', labelsize=kwargs.get("ytick_fontsize", 10))
    ax.tick_params(axis='x', labelsize=kwargs.get("xtick_fontsize", 10))

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel("")
    ax.set_ylabel("Check\n frequency", fontsize=kwargs.get("ylabel_fontsize", 10))
    ax.set_xticklabels([f"{int(tick)}%" for tick in ax.get_xticks()])
    if (ax_param is None and filename is not None):
        plt.savefig(filename, bbox_inches='tight')



def fig1_swarm_combined(metrics= Metrics,
                        filename: str="./fig1_swarm_combined.pdf",
                        **kwargs: dict) -> None:
    
    # Create a figure with two subplots
    _, axes = plt.subplots(3, 1, figsize= kwargs.get("figsize", (7, 3)), gridspec_kw={'height_ratios': kwargs.get("height_ratios", [1, 1, 1])})

    # Plot figures
    swarm_diamond_number_of_test_cases(metrics, ax=axes[0], **kwargs)
    swarm_diamond_ratio_checks_added(metrics, ax=axes[1], **kwargs)
    swarm_diamond_fail_ratio(metrics, ax=axes[2], **kwargs)

    # Adding subplot labels (a) and (b)
    axes[0].text(kwargs.get("label_x", -0.23), kwargs.get("label_y", 1.2), "a)",
                 transform=axes[0].transAxes, fontsize=16, va='top')    
    axes[1].text(kwargs.get("label_x", -0.23), kwargs.get("label_y", 1.2), "b)",
                 transform=axes[1].transAxes, fontsize=16, va='top')
    axes[2].text(kwargs.get("label_x", -0.23), kwargs.get("label_y", 1.2), "c)",
                    transform=axes[2].transAxes, fontsize=16, va='top')
    
    # Adjust the space between the subplots
    plt.subplots_adjust(hspace=kwargs.get("hspace", 0.5))

    # Custom Legend
    legend_elements = [
        Line2D([0], [0], 
               marker='o', 
               color='w', 
               markerfacecolor='grey', 
               markersize=7, 
               label='Individuals'),
        Line2D([0], [0], 
               marker='d', 
               color='grey', 
               markersize=8, 
               linewidth=2,
               label='Average and std. across individuals'),
        Line2D([0], [0], 
               color=colors["baseline"], 
               linestyle='--', 
               linewidth=2, 
               label="Error rate of pre-trained model from independant annotators' data")
    ]

    plt.legend(handles=legend_elements, 
               loc='upper left', 
               ncols=1,
               bbox_to_anchor=kwargs.get("bbox_to_anchor", (-0.27, -0.)),
               frameon=False)
    
    plt.savefig(filename, bbox_inches='tight')


def table_tests_per_category_with_baseline(metrics: Metrics,
                            filename: str = "./fig2_table_per_category_with_baseline.pdf",
                            ax: matplotlib.axes.Axes = None,
                            **kwargs: dict) -> dict:
    """
    Returns Gini statistics and t-test results.
    """

    # * Instantiate the figure
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7.5, 2.2)))

    # * Load data
    data_testers = metrics.get_final_number_of_tests_per_participant_per_class()
    data_annotators = metrics.get_final_number_of_tests_per_participant_per_class_baseline()

    data_testers.index.name = "Category"
    data_annotators.index.name = "Category"

    # Convert counts to percentages (column-wise)
    data_testers = data_testers.div(data_testers.sum(axis=0), axis=1)
    data_annotators = data_annotators.div(data_annotators.sum(axis=0), axis=1)

    # * Gini impurity
    def compute_gini(x):
        return 1 - np.sum(x ** 2) if x.sum() > 0 else np.nan

    gini_testers = data_testers.apply(compute_gini, axis=0)
    gini_annotators = data_annotators.apply(compute_gini, axis=0)

    # * Welch t-test
    t_stat, p_value = ttest_ind(
        gini_testers.dropna(),
        gini_annotators.dropna(),
        equal_var=False
    )

    # * Sort columns by Gini
    testers_sorted = gini_testers.sort_values().index
    annotators_sorted = gini_annotators.sort_values().index

    data_testers = data_testers[testers_sorted]
    data_annotators = data_annotators[annotators_sorted]

    data_testers.columns = [f"{c}" for c in data_testers.columns]
    data_annotators.columns = [f"A{c}" for c in data_annotators.columns]

    # * Compute averages
    avg_testers = data_testers.mean(axis=1).rename("Avg. testers")
    avg_annotators = data_annotators.mean(axis=1).rename("Avg. annotators")

    # * Combine full table
    full_data = pd.concat(
        [data_testers, avg_testers, data_annotators, avg_annotators],
        axis=1
    )

    # * Global colormap normalization
    flattened = pd.Series(full_data.values.flatten()) * 100
    cmap = LinearSegmentedColormap.from_list("viridis", plt.cm.viridis.colors)
    global_cmap = normed_cmap(flattened, cmap, num_stds=3)

    # * Column definitions
    columns = []

    for col in data_testers.columns:
        columns.append(
            ColumnDefinition(
                col,
                formatter="{:.0f}",
                cmap=global_cmap,
                textprops={"fontsize": 8, "ha": "center"},
                group="Testers",
                width=0.3
            )
        )

    columns.append(
        ColumnDefinition(
            "Avg. testers",
            formatter="{:.0f}",
            cmap=global_cmap,
            textprops={"fontsize": 8, "ha": "center"},
            title="Avg.",
            border="right",
            width=0.8,
        )
    )

    for col in data_annotators.columns:
        columns.append(
            ColumnDefinition(
                col,
                formatter="{:.0f}",
                cmap=global_cmap,
                textprops={"fontsize": 8, "ha": "center"},
                group="Annotators",
                width=0.3
            )
        )

    columns.append(
        ColumnDefinition(
            "Avg. annotators",
            formatter="{:.0f}",
            cmap=global_cmap,
            textprops={"fontsize": 8, "ha": "center"},
            title="Avg.",
            width=0.8,
        )
    )

    # Convert to %
    full_data = full_data * 100
    for col in full_data.columns:
        full_data[col] = adjust_percentages(full_data[col])

    # * Build table
    table = Table(full_data, column_definitions=columns)
    table.figure.tight_layout(pad=1)

    if filename:
        table.figure.savefig(filename, bbox_inches="tight")
    else:
        plt.show()

    return {
        "gini_testers": gini_testers,
        "gini_annotators": gini_annotators,
        "gini_ttest": {
            "t": t_stat,
            "p": p_value,
        },
    }

def table_tests_per_category(metrics: Metrics,
                            filename: str="./fig2_table_per_category.pdf",
                            ax: matplotlib.axes.Axes = None,
                            **kwargs: dict) -> None:

    # * Instanciate the figure
    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7.5, 2.2)))  # Adjust width for additional column

    # * Compute per-class test case distribution
    # Classes as rows and participants as columns
    data = metrics.get_final_number_of_tests_per_participant_per_class()

    # Rename Label into Category
    data.index.name = "Category"
    
    # Convert counts to percentages for each column
    data = data.div(data.sum(axis=0), axis=1)

    # Compute distribution across all testers (row-wise mean)
    class_distribution = data.mean(axis=1).rename("Avg. (%)")

    # Compute Gini impurity index for each participant (column)
    def compute_gini(x):
        if x.sum() > 0:
            return 1 - np.sum(x**2)
        return np.nan  # Handle columns with invalid data (e.g., all zeros)
    
    gini_index = data.apply(compute_gini, axis=0)

    # Sort participants (columns) by Gini impurity score
    sorted_columns = gini_index.sort_values(ascending=True).index
    sorted_data = data[sorted_columns]

    # Rename sorted columns to "p1", "p2", etc.
    sorted_data.columns = [f"P{col}" for col in sorted_data.columns]

    # Combine the sorted data with the "Avg." column
    data_with_avg = pd.concat([sorted_data, class_distribution], axis=1)

    # Flatten the data into a single series for global normalization
    flattened_data = pd.Series(data_with_avg.values.flatten())

    # Define colormap for heatmap (viridis is colorblind-friendly)
    cmap = LinearSegmentedColormap.from_list("viridis", plt.cm.viridis.colors)

    # Generate a normalized colormap function based on global data
    global_cmap = normed_cmap(flattened_data * 100, cmap, num_stds=3)

    # Create column definitions using the global colormap
    columns = []

    # Add grouped participant columns
    group_name = "Test case distribution per participant (in %)"
    for col in sorted_data.columns:
        columns.append(
            ColumnDefinition(
                col,
                formatter="{:.0f}",
                cmap=global_cmap,
                textprops={
                    "fontsize": kwargs.get("value_fontsize", 8),  # Reduce font size
                    "ha": "center",  # Add circle styling
                },
                title=col,  # Centered title
                group=group_name,  # Assign group name
            )
        )

    # Add the "Avg." column at the end with font size customization
    columns.append(
        ColumnDefinition(
            "Avg. (%)",
            formatter="{:.0f}",
            cmap=global_cmap,
            textprops={
                "fontsize": kwargs.get("value_fontsize", 9),
                "ha": "center",
            },
            title="Avg. (%)",  # Set column title
            border="left",  # Bold vertical line to separate this column
            width=kwargs.get("last_column_width", 2),
        )
    )
    # * Fail ratio from testers

    fail_ratio = metrics.get_fail_ratio_per_class()
    # Use the "Label" column as the index
    fail_ratio.set_index("Label", inplace=True)

    data_with_avg_and_error = pd.concat([data_with_avg, fail_ratio], axis=1)

    # Rename index to Category
    data_with_avg_and_error.index.name = "Category"

    # * Add columns for the "Fail ratio" and "Error rate" with custom colormaps

    # Transform to percentage and round in int to be sure it sums to 1
    data_with_avg_and_error.drop(columns=["Fail ratio"], inplace=True)
    data_with_avg_and_error = data_with_avg_and_error * 100
    data_with_avg_and_error = data_with_avg_and_error
    for col in data_with_avg_and_error.columns:
        if (col[0] == "P" or col[0] == "Avg. (%)"):
            data_with_avg_and_error[col] = adjust_percentages(data_with_avg_and_error[col])
    # Create the table
    table = Table(
        data_with_avg_and_error,
        column_definitions=columns,
    )

    # Plot and save the table
    table.figure.tight_layout(pad=1)
    if filename:
        table.figure.savefig(filename, bbox_inches="tight")
    else:
        plt.show()

def timeline_curricula(metrics: Metrics,
                        pids: List[int] = None,
                        show_pauses: bool = False,
                        filename: str = "./fig5_timeline_curricula.pdf",
                        ax=None,
                        **kwargs: dict) -> None:
    # Sort participants by the ratio between number of "add" and number of "check" actions
    check_counts = metrics.get_checks_per_participant()
    added_counts = metrics.get_test_added_per_participant()

    # Merge the two DataFrames to calculate the ratio
    check_counts = pd.merge(check_counts, added_counts, on="participant_id", how="outer").fillna(0)
    check_counts["Ratio"] = check_counts["Total checks"] / check_counts["Total test cases added"]
    check_counts = check_counts.sort_values(by="Ratio", ascending=True)

    # Filter participants based on `pids`
    if pids is not None:
        check_counts = check_counts[check_counts["participant_id"].isin(pids)]

    # Get user interactions
    df_ui = metrics.data["user_interactions"]

    # Selected actions for timeline
    selected_actions = ["add", "check", ["drag", "zoom", "center", "randomize"]]
    selected_actions_flattened = [action for sublist in selected_actions for action in (sublist if isinstance(sublist, list) else [sublist])]

    # Reflexion time (pauses longer than a threshold)
    reflexions = metrics.get_reflection_time(threshold=10, selected_actions=selected_actions_flattened)

    # Create the figure
    ax_param = ax
    if ax is None:
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (5, 4*len(pids)/15)))

    # Create a color palette
    palette_actions = sns.color_palette(["#0A9000", colors["check"], colors["interaction"]])
    palette_dict = {}
    for i, action in enumerate(selected_actions):
        if isinstance(action, str):
            palette_dict[action.capitalize()] = palette_actions[i]
        else:
            palette_dict["Image browsing"] = palette_actions[i]

    # Plot timeline for each participant
    for i, participant in enumerate(check_counts["participant_id"]):
        ax.axhline(y=i, color="black", linestyle="-", zorder=0, linewidth=5)
        
        # Scatter for each type of action
        for j, action in enumerate(selected_actions):
            y_tweak = (j + 1.1) * 0.07
            if isinstance(action, str):
                action_df = df_ui[(df_ui["participant_id"] == participant) & (df_ui["action"] == action)]
                ax.scatter(action_df["timestamp"], [i + y_tweak] * len(action_df), 
                           color=palette_dict[action.capitalize()], label= "One test created" if action == "add" else "Tests checked",
                           s=kwargs.get("markersize", 20), marker="|" if action == "add" else "|", zorder=100)
            else:
                action_df = df_ui[(df_ui["participant_id"] == participant) & (df_ui["action"].isin(action))]
                ax.scatter(action_df["timestamp"], [i] * len(action_df), 
                           color=palette_dict["Image browsing"], 
                           label="Image browsing", s=kwargs.get("markersize", 8), 
                           zorder=2, marker="|")

        # Plot reflexion times as horizontal segments if show_pauses is True
        if show_pauses:
            reflexion_df = reflexions[reflexions["participant_id"] == participant]
            for _, row in reflexion_df.iterrows():
                ax.plot([row["start_time"], row["start_time"] + row["time_diff"]], [i, i], 
                        color=colors["reflexion"], zorder=1, linewidth=3)

    # Set y-ticks and labels
    ax.set_xlim(kwargs.get("xlim", (0, 30)))
    ax.set_ylim([-0.018, 0.25])

    # Remove frame and y-ticks
    ax.spines['left'].set_visible(False)
    ax.spines["top"].set_visible(False) 
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_visible(False)


    # Remove x-ticks and labels

    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')

def combined_timeline(metrics: Metrics,
                      pids: List[int] = [8, 9],
                      show_pauses: bool = False,
                      filename: str = "./fig6_combined_timeline.pdf",
                      axes=None,
                      **kwargs: dict) -> None:
    if axes is None:
        # Default behavior: create new figure and axes
        _, axes = plt.subplots(1, 2, figsize=kwargs.get("figsize", (8, 4/15)),
                                gridspec_kw={'width_ratios': kwargs.get("width_ratios", [1, 1])})

    # Plot figures on the provided axes
    timeline_curricula(metrics, pids=[pids[0]], ax=axes[0], **kwargs)
    timeline_curricula(metrics, pids=[pids[1]], ax=axes[1], **kwargs)

    # Adjust the space between the subplots
    axes[0].figure.subplots_adjust(wspace=kwargs.get("wspace", 0.1))

    # Reduce fontsize of the x-ticks labels
    for ax in axes:
        ax.tick_params(axis='x', labelsize=kwargs.get("xtick_fontsize", 10))

    # Add overall xlabel (in the middle)
    axes[0].text(1.05, -1.9, "Time (in minutes)", ha='center', transform=axes[0].transAxes, fontsize=kwargs.get("xlabel_fontsize", 10))

    # Custom Legend Order
    handles, labels = axes[0].get_legend_handles_labels()
    custom_order = [1, 0, 2]  # Change the order: third item first, then first, then second
    axes[0].legend([handles[i] for i in custom_order], 
                   [labels[i] for i in custom_order],
                   loc='upper left',
                   ncol=1,
                   bbox_to_anchor=kwargs.get("bbox_to_anchor", (-0.64, 1.3)),
                   frameon=False,
                   fontsize=kwargs.get("legend_fontsize", 8))

    if axes is None:
        plt.savefig(filename, bbox_inches='tight')

    

def fig1_swarm_combined(metrics=Metrics,
                           filename="./fig1_swarm_combined.pdf",
                           **kwargs):
    
    # Create a flexible GridSpec layout
    fig = plt.figure(figsize=kwargs.get("figsize", (6, 4)))
    gs = gridspec.GridSpec(5, 2, height_ratios=kwargs.get("height_ratios", [0.7, 0.5, 0.25, 0.0, 0.7]))

    # Create subplots for the first, second, and fourth rows
    ax1 = fig.add_subplot(gs[0, :])  # Row 1, spans both columns
    ax2 = fig.add_subplot(gs[1, :])  # Row 2, spans both columns
    ax5 = fig.add_subplot(gs[4, :])  # Row 4, spans both columns

    # Create two subplots for the third row
    ax3_left = fig.add_subplot(gs[2, 0])  # Row 3, left column
    ax3_right = fig.add_subplot(gs[2, 1])  # Row 3, right column


    # Plot figures
    swarm_diamond_number_of_test_cases(metrics, ax=ax1, **kwargs)
    swarm_diamond_ratio_checks_added(metrics, ax=ax2, **kwargs)
    combined_timeline(metrics, axes=[ax3_left, ax3_right], **kwargs)
    swarm_diamond_fail_ratio(metrics, ax=ax5, **kwargs)

    # Adding subplot labels (a) and (b)
    ax1.text(kwargs.get("label_x", -0.29), kwargs.get("label_y", 1.2), "a)",
             transform=ax1.transAxes, fontsize=16, va='top')    
    ax2.text(kwargs.get("label_x", -0.29), kwargs.get("label_y", 1.2), "b)",
             transform=ax2.transAxes, fontsize=16, va='top')
    # ax3_left.text(kwargs.get("label_x", -0.50), kwargs.get("label_y", 1.2), "c)",
                #   transform=ax3_left.transAxes, fontsize=16, va='top')
    ax5.text(kwargs.get("label_x", -0.29), kwargs.get("label_y", 1.2), "c)",
             transform=ax5.transAxes, fontsize=16, va='top')

    # Adjust the space between the subplots
    fig.subplots_adjust(hspace=kwargs.get("hspace", 1))


    # Arrow for P8
    start_p8 = [0.155, 0.61]
    end_p8 = [0.22, 0.47]
    tweak_p8 = [-0.03, 0.08]
    arrow_p8 = FancyArrowPatch(start_p8, end_p8,
                            connectionstyle="arc3,rad=-0.3",  # Adjust the bend of the arrow
                            arrowstyle="<->",
                            color=colors["check"],
                            mutation_scale=10,  # Arrowhead size
                            lw=1)  # Line width
    
    fig.text((start_p8[0] + end_p8[0]) / 2 + tweak_p8[0],
                (start_p8[1] + end_p8[1]) / 2 + tweak_p8[1],
                "P8", 
                ha="center", fontsize=10, color=colors["check"])
    
    # Arrow for P9
    start_p9 = [0.87, 0.59]
    end_p9 = [0.8, 0.47]
    tweak_p9 = [0.04, 0.09]
    arrow_p9 = FancyArrowPatch(start_p9, end_p9,
                            connectionstyle="arc3,rad=0.3",  # Adjust the bend of the arrow
                            arrowstyle="<->",
                            color=colors["check"],
                            mutation_scale=10,  # Arrowhead size
                            lw=1)  # Line width
    fig.text((start_p9[0] + end_p9[0]) / 2 + tweak_p9[0],
                (start_p9[1] + end_p9[1]) / 2 + tweak_p9[1],
                "P9", 
                ha="center", fontsize=10, color=colors["check"])
    
    fig.add_artist(arrow_p8)
    fig.add_artist(arrow_p9)

    # Add annotation near the arrow
    # fig.text((start_display[0] + end_display[0]) / 2, 
    #          (start_display[1] + end_display[1]) / 2 + 0.02, 
    #          "This is an annotation", 
    #          ha="center", fontsize=10, color="red")



    # Custom Legend
    legend_elements = [
        Line2D([0], [0], 
               marker='o', 
               color='w', 
               markerfacecolor='grey', 
               markersize=7, 
               label='Individuals'),
        Line2D([0], [0], 
               marker='d', 
               color='grey', 
               markersize=8, 
               linewidth=2,
               label='Average and standard deviation'),
    ]
    custom_order = [0, 1]  # Change the order: third item first, then first, then second
    # text font should be 10
    fig.legend(handles=[legend_elements[i] for i in custom_order],
               loc='upper center', 
               ncols=2,
               bbox_to_anchor=kwargs.get("bbox_to_anchor", (0.5, 0.96)),
               frameon=False,
               fontsize=10)
    
    plt.savefig(filename, bbox_inches='tight')
