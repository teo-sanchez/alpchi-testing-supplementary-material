import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import scipy
from scipy import stats
from scipy.stats import pearsonr
from typing import List
from scipy.stats import spearmanr

# from highlight_text import HighlightText, ax_text, fig_text
# Import data processing functions
# Import dataLoader
from src.data_processing import DataLoader
# Import the Metrics class
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

def swarm_diamond_number_of_test_cases(metrics,
                                        filename: str= "../figures/lbw/fig1_swarm_number_of_test_cases.pdf",
                               ax=None,
                                 **kwargs: dict) -> None:
    # Baseline
    total_annotators = metrics.get_final_number_of_tests_baseline()
    total_annotators.rename(columns={"Total test cases": "Annotators"}, inplace=True)
    # Add column "Role" with "Annotators" values
    total_annotators["Role"] = "Annotators"

    # Tester
    total_testers = metrics.get_final_number_of_tests_per_participant()
    total_testers.rename(columns={"Total test cases": "Testers"}, inplace=True)
    # Add column "Role" with "Testers" values
    total_testers["Role"] = "Testers"

    # Merge the two dataframes
    total = pd.concat([total_annotators, total_testers], ignore_index=True)
    
    # Melt the DataFrame to restructure it for Seaborn
    total = pd.melt(total, id_vars=["participant_id", "Role"], value_vars=["Annotators", "Testers"],
                    var_name="Test_Type", value_name="Count")
    
    # Drop rows with NaN in the Count column (these represent empty values from merging)
    total = total.dropna(subset=["Count"])

    # Peform ANOVA
    annotators_count = total[total["Role"] == "Annotators"]["Count"]
    testers_count = total[total["Role"] == "Testers"]["Count"]
    f_stat, p_value = stats.f_oneway(annotators_count, testers_count)

    # Format ANOVA result with significance stars
    if p_value < 0.001:
        stars = '***'  # Very strong significance
    elif p_value < 0.01:
        stars = '**'   # Strong significance
    elif p_value < 0.05:
        stars = '*'    # Significant
    else:
        stars = ''     # Not significant
    
    # Format p-value to avoid scientific notation
    p_value_str = f"{p_value:.3f}"
    anova_text = f"ANOVA\nF = {f_stat:.2f}\nP-value: {p_value_str}{stars}"
        
    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=(kwargs.get("figsize", (7, 1.7))))

    # Pointplot for the mean
    sns.pointplot(x="Count", y="Role", data=total, 
                  estimator=np.mean, 
                  orient="h", 
                  color=darken_color(colors["addition"]), 
                  markers="d",
                  linestyles="",
                  markersize=kwargs.get("markersize", 8),
                  linewidth=kwargs.get("linewidth", 2),
                  ax=ax)
    
    # # Swarmplot
    sns.swarmplot(x="Count", y="Role", data=total, 
                  size=kwargs.get("markersize", 7), 
                  marker="o", 
                  orient="h", 
                  palette=[colors["addition"]], 
                  ax=ax, 
                  alpha=0.5)

    # Invert the y-axis
    ax.invert_yaxis()

    # Display ANOVA results in the bottom-right corner of the plot with transparent background
    ax.text(0.98, 0.96, anova_text, transform=ax.transAxes, va='top', ha='right',
            backgroundcolor='none', fontsize=8)

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel("Count")
    ax.set_ylabel("")
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')
    

def swarm_diamond_fail_ratio(metrics,
                             filename: str = "../figures/lbw/fig2_swarm_fail_ratio.pdf",
                             ax=None,
                             **kwargs: dict) -> None:
    # Baseline (Annotators)
    total_annotators = metrics.get_fail_ratio_per_participant_baseline()
    total_annotators.rename(columns={"Fail ratio": "Annotators"}, inplace=True)
    total_annotators["Role"] = "Annotators"

    # Testers
    total_testers = metrics.get_fail_ratio_per_participant()
    total_testers.rename(columns={"Fail ratio": "Testers"}, inplace=True)
    total_testers["Role"] = "Testers"

    # Merge the two dataframes
    total = pd.concat([total_annotators, total_testers], ignore_index=True)

    # Melt the DataFrame to restructure it for Seaborn
    total = pd.melt(total, id_vars=["participant_id", "Role"], value_vars=["Annotators", "Testers"],
                    var_name="Test_Type", value_name="Fail Ratio")

    # Drop rows with NaN in the Fail Ratio column (these represent empty values from merging)
    total = total.dropna(subset=["Fail Ratio"])

    # Perform ANOVA
    annotators_fail_ratio = total[total["Role"] == "Annotators"]["Fail Ratio"]
    testers_fail_ratio = total[total["Role"] == "Testers"]["Fail Ratio"]
    f_stat, p_value = stats.f_oneway(annotators_fail_ratio, testers_fail_ratio)

    # Format ANOVA result with significance stars
    if p_value < 0.001:
        stars = '***'  # Very strong significance
    elif p_value < 0.01:
        stars = '**'   # Strong significance
    elif p_value < 0.05:
        stars = '*'    # Significant
    else:
        stars = ''     # Not significant

    # Format p-value to avoid scientific notation
    p_value_str = f"{p_value:.2f}"
    anova_text = f"ANOVA\nF = {f_stat:.2f}\nP-value: {p_value_str}{stars}"

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=(kwargs.get("figsize", (7, 1.5))))

    # Pointplot for the mean fail ratio
    sns.pointplot(x="Fail Ratio", y="Role", data=total, 
                  estimator=np.mean, 
                  orient="h", 
                  color=kwargs.get("color", darken_color(colors["fail"])), 
                  markers="d",
                  linestyles="",
                  markersize=kwargs.get("markersize", 8),
                  linewidth=kwargs.get("linewidth", 2),
                  ax=ax)

    # Swarmplot for individual fail ratios
    sns.swarmplot(x="Fail Ratio", y="Role", data=total, 
                  size=kwargs.get("markersize", 7), 
                  marker="o", 
                  orient="h", 
                  palette=[kwargs.get("color", colors["fail"])], 
                  ax=ax, 
                  alpha=0.5)

    # Invert the y-axis
    ax.invert_yaxis()

    # Display ANOVA results in the bottom-right corner of the plot with transparent background
    ax.text(0.98, 0.05, anova_text, transform=ax.transAxes, va='bottom', ha='right',
            backgroundcolor='none', fontsize=8)

    # Grid and labels
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel("Fail ratio (in %)")
    ax.set_ylabel("")
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')

def swarm_diamond_uncertainty(metrics,
                             filename: str = "../figures/lbw/fig3_swarm_entropy.pdf",
                             ax=None,
                             **kwargs: dict) -> None:
    # * Baseline (Annotators)
    total_annotators = metrics.get_entropy_per_participant_baseline()
    total_annotators.rename(columns={"Entropy": "Annotators"}, inplace=True)
    total_annotators["Role"] = "Annotators"

    # * Testers
    total_testers = metrics.get_entropy_per_participant()
    total_testers.rename(columns={"Entropy": "Testers"}, inplace=True)
    total_testers["Role"] = "Testers"


    # Merge the two dataframes
    total = pd.concat([total_annotators, total_testers], ignore_index=True)

    # Ensure no NaNs in "Mean entropy" column
    total = total.dropna(subset=["Mean entropy"])
    # Drop PID
    total.drop(columns=["participant_id"], inplace=True)

    # Perform ANOVA
    annotators_entropy = total[total["Role"] == "Annotators"]["Mean entropy"]
    testers_entropy = total[total["Role"] == "Testers"]["Mean entropy"]
    f_stat, p_value = stats.f_oneway(annotators_entropy, testers_entropy)

    # Format ANOVA result with significance stars
    if p_value < 0.001:
        stars = '***'  # Very strong significance
    elif p_value < 0.01:
        stars = '**'   # Strong significance
    elif p_value < 0.05:
        stars = '*'    # Significant
    else:
        stars = ''     # Not significant

    # Format p-value to avoid scientific notation
    p_value_str = f"{p_value:.2f}"
    anova_text = f"ANOVA\nF = {f_stat:.2f}\nP-value: {p_value_str}{stars}"


    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=(kwargs.get("figsize", (7, 1.5))))

    # Pointplot for the mean entropy
    sns.pointplot(x="Mean entropy", y="Role", data=total, 
                  estimator=np.mean, 
                  orient="h", 
                  color=kwargs.get("color", darken_color(colors["uncertainty"])), 
                  markers="d",
                  linestyles="",
                  markersize=kwargs.get("markersize", 8),
                  linewidth=kwargs.get("linewidth", 2),
                  ax=ax)

    # Swarmplot for individual entropy values
    sns.swarmplot(x="Mean entropy", y="Role", data=total, 
                  size=kwargs.get("markersize", 7), 
                  marker="o", 
                  orient="h", 
                  palette=[kwargs.get("color", colors["uncertainty"])], 
                  ax=ax, 
                  alpha=0.5)

    # Invert the y-axis
    ax.invert_yaxis()

    # Display ANOVA results in the bottom-right corner of the plot with transparent background
    ax.text(0.98, 0.05, anova_text, transform=ax.transAxes, va='bottom', ha='right',
            backgroundcolor='none', fontsize=8)

    # Grid and labels
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel("Uncertainty via averaged Shannon entropy")
    ax.set_ylabel("")
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')

def swarm_combined(metrics: Metrics, filename: str = "../figures/lbw/fig1_combined_swarm.pdf", **kwargs: dict) -> None:
    # All three swarms together
    # Create a figure with two subplots
    _, axes = plt.subplots(3, 1, figsize=kwargs.get("figsize", (8, 5)))

    swarm_diamond_number_of_test_cases(metrics, ax=axes[0], **{"figsize": (7,2)})
    swarm_diamond_fail_ratio(metrics, ax=axes[1], **{"figsize": (7,2)})
    swarm_diamond_uncertainty(metrics, ax=axes[2], **{"figsize": (7,2)})

    # Adding subplot labels (a) and (b)
    axes[0].text(kwargs.get("label_x", -0.13), kwargs.get("label_y", 1.1), "a)", transform=axes[0].transAxes, fontsize=14, va='top')
    axes[1].text(kwargs.get("label_x", -0.13), kwargs.get("label_y", 1.1), "b)", transform=axes[1].transAxes, fontsize=14, va='top')
    axes[2].text(kwargs.get("label_x", -0.13), kwargs.get("label_y", 1.1), "c)", transform=axes[2].transAxes, fontsize=14, va='top')

    # Adjust the space between the subplots
    plt.subplots_adjust(hspace=1, wspace=0)

    #Legend outside the plot
    plt.legend(loc='upper left',
                bbox_to_anchor= kwargs.get("bbox_to_anchor", (-0.35, -0.15)),
                frameon=False)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')

def fail_ratio_uncertainty_combined(metrics,
                                    filename: str = "../figures/lbw/fig4_combined_fail_uncertainty.pdf",
                                    **kwargs: dict) -> None:
    
    # Create a figure with two subplots
    _, axes = plt.subplots(2, 1, figsize= kwargs.get("figsize", (7, 4)), gridspec_kw={'height_ratios': kwargs.get("height_ratios", [1.5, 1.5])})

    swarm_diamond_fail_ratio(metrics, ax=axes[0], **{"figsize": (7,2)})
    swarm_diamond_uncertainty(metrics, ax=axes[1], **{"figsize": (7,2)})

    # Adding subplot labels (a) and (b)
    axes[0].text(kwargs.get("label_x", -0.25), kwargs.get("label_y", 1.1), "a)", transform=axes[0].transAxes, fontsize=14, va='top')
    axes[1].text(kwargs.get("label_x", -0.25), kwargs.get("label_y", 1.1), "b)", transform=axes[1].transAxes, fontsize=14, va='top')

    # Adjust the space between the subplots
    plt.subplots_adjust(hspace=kwargs.get("hspace", 1))

    #Legend outside the plot
    plt.legend(loc='upper left',
                bbox_to_anchor= kwargs.get("bbox_to_anchor", (-0.35, -0.15)),
                frameon=False)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')


def timeline_curricula(metrics: Metrics,
                       show_pauses: bool = False,
                       filename: str = "../figures/lbw/fig5_timeline_curricula.pdf",
                       ax=None,
                       **kwargs: dict) -> None:
    # Sort participants by the ratio between number of "add" and number of "check" actions
    check_counts = metrics.get_checks_per_participant()
    added_counts = metrics.get_test_added_per_participant()

    # Merge the two DataFrames to calculate the ratio
    check_counts = pd.merge(check_counts, added_counts, on="participant_id", how="outer").fillna(0)
    check_counts["Ratio"] = check_counts["Total checks"] / check_counts["Total test cases added"]
    check_counts = check_counts.sort_values(by="Ratio", ascending=True)

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
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (12, 4)))

    # Create a color palette
    palette_actions = sns.color_palette([colors["addition"], colors["check"], colors["interaction"]])
    palette_dict = {}
    for i, action in enumerate(selected_actions):
        if isinstance(action, str):
            palette_dict[action.capitalize()] = palette_actions[i]
        else:
            palette_dict["Data browsing and test cases creation"] = palette_actions[i]

    # Plot timeline for each participant
    for i, participant in enumerate(check_counts["participant_id"]):
        ax.axhline(y=i, color="black", linestyle="-", zorder=0, linewidth=4)
        
        # Scatter for each type of action
        for j, action in enumerate(selected_actions):
            y_tweak = (j + 1) * 0.2
            if isinstance(action, str):
                action_df = df_ui[(df_ui["participant_id"] == participant) & (df_ui["action"] == action)]
                ax.scatter(action_df["timestamp"], [i + y_tweak] * len(action_df), 
                           color=palette_dict[action.capitalize()], label=action.capitalize(), 
                           s=kwargs.get("markersize", 10), marker="o" if action == "add" else "v", zorder=100)
            else:
                action_df = df_ui[(df_ui["participant_id"] == participant) & (df_ui["action"].isin(action))]
                ax.scatter(action_df["timestamp"], [i] * len(action_df), 
                           color=palette_dict["Data browsing and test cases creation"], 
                           label="Data browsing and test cases creation", s=kwargs.get("markersize", 1), 
                           zorder=2, marker="s")

        # Plot reflexion times as horizontal segments if show_pauses is True
        if show_pauses:
            reflexion_df = reflexions[reflexions["participant_id"] == participant]
            for _, row in reflexion_df.iterrows():
                ax.plot([row["start_time"], row["start_time"] + row["time_diff"]], [i, i], 
                        color=colors["reflexion"], zorder=1, linewidth=2)

    # Set y-ticks and labels
    ax.set_yticks(np.arange(len(check_counts)))
    ax.set_yticklabels(check_counts["participant_id"])
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Participant ID")
    ax.set_xlim(kwargs.get("xlim", (0, max(df_ui["timestamp"]))))

    # Grid and export
    ax.grid(axis='x', linestyle='--', alpha=0.5, zorder=-10)
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')


def lollipop_iterative(metrics: Metrics,
                       filename: str = "../figures/lbw/fig6_lollipop_iterative.pdf",
                       ax=None,
                       **kwargs: dict) -> List[int]:
    """
    Creates a lollipop plot showing the ratio of "add" to "check" actions per participant.
    Participants are sorted by this ratio.
    """
    # Get the ratio of checks to added test cases per participant using Metrics
    check_counts = metrics.get_ratio_checks_added_per_participant()

    # Sort participants by the ratio
    check_counts = check_counts.sort_values(by="Ratio checks/added", ascending=True)
    sorted_participants = check_counts["participant_id"]

    ratio_range = range(len(sorted_participants))

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (6, 3.5)))

    # Lollipop plot: horizontal lines and points
    ax.hlines(y=ratio_range, xmin=0, xmax=check_counts["Ratio checks/added"], color=colors["check"], alpha=0.7)
    ax.plot(check_counts["Ratio checks/added"], ratio_range, "o", color=colors["check"], markersize=4)

    # Add ticks and axis labels
    ax.yaxis.set_ticks(ratio_range)
    ax.yaxis.set_ticklabels(sorted_participants)
    ax.set_xlabel("Ratio of checks over the total number test cases")
    ax.set_ylabel("Participant ID")
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    # Do not plot the yaxis grid
    ax.grid(axis='y', linestyle='-', alpha=0)

    # Set x-axis limits
    ax.set_xlim(kwargs.get("xlim", [0, max(check_counts["Ratio checks/added"]) + 5]))

    # Save the figure if no axis was passed
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')

    return sorted_participants.tolist()

def swarm_diamond_ratio_checks_number(metrics,
                                        filename: str= "../figures/lbw/fig4_ratio_checks_test_cases.pdf",
                               ax=None,
                                 **kwargs: dict) -> None:
    # Get the ratio of checks to added test cases per participant using Metrics
    check_counts = metrics.get_ratio_checks_added_per_participant()

    # Sort participants by the ratio
    check_counts = check_counts.sort_values(by="Ratio checks/added", ascending=True)

    # Add tester role column
    check_counts["Role"] = "Testers"

    
    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=(kwargs.get("figsize", (7, 1))))

    # Pointplot for the mean
    sns.pointplot(y= "Role", x="Ratio checks/added", data=check_counts, 
                  estimator=np.mean, 
                  orient="h", 
                  color=darken_color(colors["check"]), 
                  markers="d",
                  linestyles="",
                  markersize=kwargs.get("markersize", 8),
                  linewidth=kwargs.get("linewidth", 2),
                  ax=ax)
    
    # # Swarmplot
    sns.swarmplot(y="Role", x="Ratio checks/added", data=check_counts,
                  size=kwargs.get("markersize", 7), 
                  marker="o", 
                  orient="h", 
                  palette=[lighten_color(colors["check"], 0.7)], 
                  ax=ax, 
                  alpha=0.9)

    # Invert the y-axis
    ax.invert_yaxis()

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_xlabel("Ratio of checks over the number of test cases (in %)")
    ax.set_ylabel("")
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')

def timeline_lollipop_combined(metrics: Metrics,
                                 filename: str = "../figures/lbw/fig7_combined_timeline_lollipop.pdf",
                                 **kwargs: dict) -> None:
     # Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=kwargs.get("figsize", (16, 5)),
                             gridspec_kw={'width_ratios': kwargs.get("width_ratios", [3, 1])}, sharey=True)
    
    # Timeline curricula (actions over time)
    timeline_curricula(metrics, ax=axes[0], **{"figsize": (7, 4)})
    
    # Lollipop plot (ratio of add to check actions)
    sorted_participants = lollipop_iterative(metrics, ax=axes[1], **{"figsize": (5, 5)})
    
    # Add subplot labels (a) and (b)
    axes[0].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "a)", transform=axes[0].transAxes,
                 fontsize=16, va='top')
    axes[1].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "b)", transform=axes[1].transAxes,
                 fontsize=16, va='top')

    # Remove y-axis label for the lollipop plot to avoid redundancy
    axes[1].set_ylabel("")

    # Adjust the space between the subplots
    plt.subplots_adjust(wspace=kwargs.get("wspace", 0.05))

    # Custom legend outside the plot
    custom_lines = [matplotlib.lines.Line2D([0], [0], color=colors["addition"], marker='o', linestyle='None'),
                    matplotlib.lines.Line2D([0], [0], color=colors["check"], marker='o', linestyle='None'),
                    matplotlib.lines.Line2D([0], [0], color=colors["interaction"], marker='s', linestyle='None')]

    axes[0].legend(custom_lines,
                   ['Addition of a test case', 'Check test cases', 'Input browsing/searching'],
                   loc='upper left', bbox_to_anchor=(0.1, 1.09), frameon=False, ncol=4)

    # Save the figure
    plt.savefig(filename, bbox_inches='tight')

def scatter_fail_ratio_uncertainty(metrics: Metrics,
                             filename: str= "../figures/lbw/fig8_scatter_fail_uncertainty.pdf",
                             ax=None,
                             **kwargs: dict) -> None:
    # Get fail ratio and uncertainty
    fail_ratio = metrics.get_fail_ratio_per_participant()
    entropy = metrics.get_entropy_per_participant()

    # Ensure participant_id is a column, not an index
    if "participant_id" not in fail_ratio.columns:
        fail_ratio = fail_ratio.reset_index()
    if "participant_id" not in entropy.columns:
        entropy = entropy.reset_index()
    
    # Merge the dataframes
    data = pd.merge(fail_ratio, entropy, on='participant_id', how='inner')

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))
    
    # Scatter plot with linear regression
    sns.regplot(data=data, x="Mean entropy", y="Fail ratio", ax=ax, color=colors["fail"])

    # Compute Pearson correlation and linear regression
    correlation, p_value = pearsonr(data["Mean entropy"], data["Fail ratio"])
    slope, intercept, _, _, _ = stats.linregress(data["Mean entropy"], data["Fail ratio"])
    r2 = round(correlation ** 2, 2)

    # Determine significance stars based on p-value
    stars = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''

    # Add regression stats to the plot
    ax.text(0.05, 0.95, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
            transform=ax.transAxes, va='top')
    
    # Set labels and limits
    ax.set_xlabel("Averaged Shannon entropy")
    ax.set_ylabel("Fail ratio (in %)")
    ax.set_xlim(kwargs.get("xlim", (0.5, 1.2)))
    ax.set_ylim(kwargs.get("ylim", (0, 100)))
    ax.grid(axis='both', linestyle='--', alpha=0.5)

    # Save the figure
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')


def scatter_uncertainty_total_tests(metrics: Metrics,
                                     filename: str = ""

def scatter_iterative_total_tests(metrics: Metrics,
                                      filename: str = "../figures/lbw/fig8_scatter_iterative_total_tests.pdf",
                                      ax=None,
                                      **kwargs: dict) -> None:
    # Get metrics data
    final_tests = metrics.get_final_number_of_tests_per_participant()
    ratio_checks_added = metrics.get_ratio_checks_added_per_participant()

    # Merge the dataframes
    data = pd.merge(final_tests, ratio_checks_added, on='participant_id', how='inner')

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))

    # Scatter plot with linear regression
    sns.regplot(data=data, x="Ratio checks/added", y="Total test cases", ax=ax, color=colors["addition"])

    # Compute Pearson correlation and linear regression
    correlation, p_value = pearsonr(data["Ratio checks/added"], data["Total test cases"])
    slope, intercept, _, _, _ = stats.linregress(data["Ratio checks/added"], data["Total test cases"])
    r2 = round(correlation ** 2, 2)

    # Determine significance stars based on p-value
    stars = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''

    # Add regression stats to the plot
    ax.text(0.55, 0.95, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
            transform=ax.transAxes, va='top')

    # Set labels and limits
    # ax.set_xlabel("Ratio of checks over the total number of test cases (in %)")
    ax.set_xlabel("")
    ax.set_ylabel("Final number of test cases")
    ax.set_xlim(kwargs.get("xlim", (0, 101)))
    ax.set_ylim(kwargs.get("ylim", (0, max(data["Total test cases"]) + 20)))
    ax.grid(axis='both', linestyle='--', alpha=0.5)

    # Save the figure
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')
        
def scatter_iterative_fail_ratio(metrics: Metrics,
                                 filename: str = "../figures/lbw/fig9_scatter_iterative_fail_ratio.pdf",
                                 ax=None,
                                 **kwargs: dict) -> None:
    # Get fail ratio and ratio of checks to adds
    fail_ratio = metrics.get_fail_ratio_per_participant()
    ratio_checks_added = metrics.get_ratio_checks_added_per_participant()

    # Ensure participant_id is a column, not an index
    if "participant_id" not in fail_ratio.columns:
        fail_ratio = fail_ratio.reset_index()
    if "participant_id" not in ratio_checks_added.columns:
        ratio_checks_added = ratio_checks_added.reset_index()

    # Merge the dataframes
    data = pd.merge(fail_ratio, ratio_checks_added, on='participant_id', how='inner')

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))

    # Scatter plot with linear regression
    sns.regplot(data=data, x="Ratio checks/added", y="Fail ratio", ax=ax, color=colors["fail"])

    # Compute Pearson correlation and linear regression
    correlation, p_value = pearsonr(data["Ratio checks/added"], data["Fail ratio"])
    slope, intercept, _, _, _ = stats.linregress(data["Ratio checks/added"], data["Fail ratio"])
    r2 = round(correlation ** 2, 2)

    # Determine significance stars based on p-value
    stars = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''

    # Add regression stats to the plot
    ax.text(0.4, 0.95, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
            transform=ax.transAxes, va='top')

    # Set labels and limits
    ax.set_xlabel("")
    ax.set_ylabel("Fail ratio (in %)")
    ax.set_xlim(kwargs.get("xlim", (0, 101)))
    ax.set_ylim(kwargs.get("ylim", (0, 100)))
    ax.grid(axis='both', linestyle='--', alpha=0.5)

    # Save the figure
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')

def scatter_iterative_uncertainty(metrics: Metrics,
                                  filename: str = "../figures/lbw/fig10_scatter_iterative_uncertainty.pdf",
                                  ax=None,
                                  **kwargs: dict) -> None:
    # Get entropy and ratio of checks to adds
    entropy = metrics.get_entropy_per_participant()  # Already returns participant_id as a column
    ratio_checks_added = metrics.get_ratio_checks_added_per_participant()

    # Ensure participant_id is a column, not an index
    if "participant_id" not in entropy.columns:
        entropy = entropy.reset_index()
    if "participant_id" not in ratio_checks_added.columns:
        ratio_checks_added = ratio_checks_added.reset_index()

    # Merge the dataframes
    data = pd.merge(entropy, ratio_checks_added, on='participant_id', how='inner')

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))

    # Scatter plot with linear regression
    sns.regplot(data=data, x="Ratio checks/added", y="Mean entropy", ax=ax, color=colors["uncertainty"])

    # Compute Pearson correlation and linear regression
    correlation, p_value = pearsonr(data["Ratio checks/added"], data["Mean entropy"])
    slope, intercept, _, _, _ = stats.linregress(data["Ratio checks/added"], data["Mean entropy"])
    r2 = round(correlation ** 2, 2)

    # Determine significance stars based on p-value
    stars = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''

    # Add regression stats to the plot
    ax.text(0.4, 0.05, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
            transform=ax.transAxes, va='bottom')

    # Set labels and limits
    # ax.set_xlabel("Ratio of checks over the total number of test cases (in %)")
    ax.set_xlabel("")
    ax.set_ylabel("Averaged Shannon entropy")
    ax.set_xlim(kwargs.get("xlim", (0, 101)))
    ax.set_ylim(kwargs.get("ylim", (0, max(data["Mean entropy"]) + 0.1)))
    ax.grid(axis='both', linestyle='--', alpha=0.5)

    # Save the figure
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')




def iterativeness_combined(metrics: Metrics, filename: str = "../figures/lbw/fig11_combined_iterativeness.pdf", **kwargs: dict) -> None:
    # Create a gridspec layout for two rows: first row full width, second row two columns
    fig = plt.figure(figsize=kwargs.get("figsize", (7, 4.5)))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 3], hspace=0.4)

    # First plot: full width on top
    ax1 = fig.add_subplot(gs[0, :])
    swarm_diamond_ratio_checks_number(metrics, ax=ax1, **{"figsize": (14, 2)})

    # Second row: two scatter plots side by side
    ax2 = fig.add_subplot(gs[1, 0])
    scatter_iterative_fail_ratio(metrics, ax=ax2, **{"figsize": (7, 5)})

    ax3 = fig.add_subplot(gs[1, 1])
    scatter_iterative_uncertainty(metrics, ax=ax3, **{"figsize": (7, 5)})
    # Adjust the space between the subplots from ax3
    plt.subplots_adjust(wspace=0.3, hspace=2)


    # Add subplot labels
    ax1.text(kwargs.get("label_x", -0.05), kwargs.get("label_y", 1.15), "a)", transform=ax1.transAxes, fontsize=16, va='top')
    ax2.text(kwargs.get("label_x", -0.3), kwargs.get("label_y", 1.05), "b)", transform=ax2.transAxes, fontsize=16, va='top')
    ax3.text(kwargs.get("label_x", -0.25), kwargs.get("label_y", 1.05), "c)", transform=ax3.transAxes, fontsize=16, va='top')

    # Clean up the bottom row (remove unnecessary spines and ticks)
    for ax in [ax1, ax2, ax3]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # Add a shared xlabel below the bottom row
    xlabel_text = kwargs.get("xlabel", "Ratio of checks over the total number of test cases (in %)")
    fig.supxlabel(xlabel_text, fontsize=10, y=0.02)  # Adjust 'y' for the vertical position of the label


    # Save the figure
    plt.savefig(filename, bbox_inches='tight')
    plt.show()


def scatter_combined(metrics: Metrics, filename: str = "../figures/lbw/fig11_combined_scatter.pdf", **kwargs: dict) -> None:
    # Create a figure with three subplots
    _, axes = plt.subplots(1, 3, figsize=kwargs.get("figsize", (14, 4)))

    scatter_iterative_total_tests(metrics, ax=axes[0], **{"figsize": (7, 5)})
    scatter_iterative_fail_ratio(metrics, ax=axes[1], **{"figsize": (7, 5)})
    scatter_iterative_uncertainty(metrics, ax=axes[2], **{"figsize": (7, 5)})

    # Adding subplot labels (a), (b), and (c)
    axes[0].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.09), "a)", transform=axes[0].transAxes,
                 fontsize=16, va='top')
    axes[1].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.09), "b)", transform=axes[1].transAxes,
                 fontsize=16, va='top')
    axes[2].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.09), "c)", transform=axes[2].transAxes,
                 fontsize=16, va='top')

    # Adjust the space between the subplots
    plt.subplots_adjust(wspace=kwargs.get("wspace", 0.3))

    # Save the figure
    plt.savefig(filename, bbox_inches='tight')

def scatter_survey_metric(metrics: Metrics, question_keyword: str, metric: str, 
                          pid_list=None,
                          ordered_categories=None,
                          filename: str = "../figures/lbw/scatter_survey_metric.pdf",
                          color_str: str = "fail",
                          ax=None,
                          **kwargs: dict) -> None:
    """
    Plots a scatter plot with Likert-scale responses (x-axis) and the selected metric (y-axis).
    
    Parameters:
    - metrics: Metrics class containing data
    - question_keyword: Key to access the questionnaire column (e.g., "Ability to understand")
    - metric: Metric to plot (e.g., "Ratio checks/added", "Total test cases", "Fail ratio")
    - pid_list: List of participant IDs to include in the plot.
    - ordered_categories: List of Likert-scale categories in the desired order.
    - filename: Path to save the plot.
    - ax: Matplotlib axis for plotting.
    - kwargs: Additional customization parameters (e.g., figsize, markersize).
    """
    # Mapping for display purposes
    mapping_questions = {
        "Understand predictions": "After completing the experiment, I understand the reasoning behind the classifier's predictions.",
        "Alignment with expectations": "The predictions of the classifier align with my understanding of machine learning image classification.",
        "Reliable predictions": "I feel that the predictions provided by the satellite image classifier are reliable.",
        "Trust retrained model": "I would trust the retrained satellite image classifier more if it were updated based on the test set I created.",
        "Unpredictable reaction": "The system reacts unpredictably.",
        "Ability to understand": "I was able to understand why the image classifier made mistakes.",
        "Real world app trust": "I would trust the system if it was deployed in a real-world application.",
        "Accurate classifier": "Overall, the image classifier is accurate.",
        "Factors influencing prioritization": "Which of the following factors mostly influenced your choice of which classes to prioritize, as the testing progressed?",
        "Gender": "Which gender do you identify with?",
        "Rate expertise": "How would you rate your expertise in machine learning?",
        "Age: [01]": "How old are you?",
    }

    # Get display text for the question
    question_display_text = mapping_questions.get(question_keyword, question_keyword)

    # Get questionnaire responses and metrics
    questionnaire = metrics.data["questionnaire"][["participant_id", question_keyword]].dropna()

    # Filter based on pid_list if provided
    if pid_list is not None:
        questionnaire = questionnaire[questionnaire["participant_id"].isin(pid_list)]

    # Convert questionnaire responses to categorical type with ordered categories
    if ordered_categories is not None:
        questionnaire[question_keyword] = pd.Categorical(questionnaire[question_keyword],
                                                         categories=ordered_categories,
                                                         ordered=True)

    # Get the corresponding metric data
    if metric == "Ratio checks/added":
        metric_data = metrics.get_ratio_checks_added_per_participant()
    elif metric == "Total test cases":
        metric_data = metrics.get_final_number_of_tests_per_participant()
    elif metric == "Fail ratio":
        metric_data = metrics.get_fail_ratio_per_participant()
    elif metric == "Number of fails uncovered":
        metric_data = metrics.get_number_of_fails_per_participant()
    else:
        raise ValueError(f"Invalid metric: {metric}. Please choose from 'Ratio checks/added', 'Total test cases', or 'Fail ratio'.")

    # Merge the questionnaire responses with the metric data
    data = pd.merge(questionnaire, metric_data, on="participant_id")

    ax_param = ax
    if ax is None:
        _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 3)))

    # Point plot for the means (no lines)
    # Calculate mean and standard deviation for each category
    # stats = data.groupby(question_keyword)[metric].agg(["mean", "std"]).reset_index()

    # # Plot diamonds for the mean and error bars for the standard deviation
    # ax.errorbar(x=stats[question_keyword].cat.codes, y=stats["mean"], yerr=stats["std"],
    #             fmt='D', markersize=7, color=darken_color(colors[color_str]), ecolor=darken_color(colors[color_str]), capsize=3)

    # Scatter plot with categorical x-axis (Likert-scale)
    sns.stripplot(data=data, x=metric, y=question_keyword, ax=ax, size=kwargs.get("markersize", 8),
                  jitter=False, color=lighten_color(colors[color_str], 0.7), alpha=0.7)

    # invert axis for better readability
    ax.invert_yaxis()

    # Set labels and title
    ax.set_title(question_display_text)
    ax.set_ylabel("")
    ax.set_xlabel(metric)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Horizontal grid lines
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)
    
    # Save the figure
    if ax_param is None:
        plt.savefig(filename, bbox_inches='tight')   

def survey_metric_correlation(metrics: Metrics, question_keyword: str, metric: str, 
                            pid_list=None, ordered_categories=None) -> None:
    """
    Computes and prints Spearman's rank correlation between survey responses and a performance metric.

    Parameters:
    - metrics: Metrics class containing data
    - question_keyword: Key to access the questionnaire column (e.g., "Ability to understand")
    - metric: Metric to correlate (e.g., "Ratio checks/added", "Total test cases", "Fail ratio")
    - pid_list: List of participant IDs to include in the correlation.
    - ordered_categories: List of Likert-scale categories in the desired order.
    """
    # Mapping for display purposes
    mapping_questions = {
        "Understand predictions": "After completing the experiment, I understand the reasoning behind the classifier's predictions.",
        "Alignment with expectations": "The predictions of the classifier align with my understanding of machine learning image classification.",
        "Reliable predictions": "I feel that the predictions provided by the satellite image classifier are reliable.",
        "Trust retrained model": "I would trust the retrained satellite image classifier more if it were updated based on the test set I created.",
        "Unpredictable reaction": "The system reacts unpredictably.",
        "Ability to understand": "I was able to understand why the image classifier made mistakes.",
        "Real world app trust": "I would trust the system if it was deployed in a real-world application.",
        "Accurate classifier": "Overall, the image classifier is accurate.",
    }

    # Get display text for the question
    question_display_text = mapping_questions.get(question_keyword, question_keyword)

    # Get questionnaire responses and metrics
    questionnaire = metrics.data["questionnaire"][["participant_id", question_keyword]].dropna()

    # Filter based on pid_list if provided
    if pid_list is not None:
        questionnaire = questionnaire[questionnaire["participant_id"].isin(pid_list)]

    # Convert questionnaire responses to categorical type with ordered categories
    if ordered_categories is not None:
        questionnaire[question_keyword] = pd.Categorical(questionnaire[question_keyword],
                                                            categories=ordered_categories,
                                                            ordered=True)

    # Get the corresponding metric data
    if metric == "Ratio checks/added":
        metric_data = metrics.get_ratio_checks_added_per_participant()
    elif metric == "Total test cases":
        metric_data = metrics.get_final_number_of_tests_per_participant()
    elif metric == "Fail ratio":
        metric_data = metrics.get_fail_ratio_per_participant()
    elif metric == "Number of fails uncovered":
        metric_data = metrics.get_number_of_fails_per_participant()
    elif metric == "Mean entropy":
        metric_data = metrics.get_entropy_per_participant()
    else:
        raise ValueError(f"Invalid metric: {metric}. Please choose from 'Ratio checks/added', 'Total test cases', or 'Fail ratio'.")

    # Merge the questionnaire responses with the metric data
    data = pd.merge(questionnaire, metric_data, on="participant_id")

    # Calculate Spearman's correlation
    correlation, p_value = spearmanr(data[question_keyword].cat.codes, data[metric])

    # Print results
    print(f"Spearman's Correlation (rho) between '{question_display_text}' and '{metric}':\n {correlation:.4f}, p-value: {p_value:.4f}")      

# def swarm_number_of_test_cases(df_ui: UserInteractions, 
#                                filename: str= "../figures/general/fig1.1_swarm_number_of_test_cases.pdf", 
#                                ax=None,
#                                **kwargs: dict) -> None:

#     # Number of test cases added in total
#     deleted = get_number_of_test_deleted_per_participant(df_ui)

#     # Number of test cases at the end of the session
#     final_number_of_tests = get_final_number_of_tests_per_participant(df_ui)


#     final = pd.merge(deleted, final_number_of_tests, on="participant_id", how="outer").fillna(0)
#     final.drop(columns=["participant_id"], inplace=True)

    
#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=(kwargs.get("figsize", (7, 1.5))))

#     # Swarmplot
#     sns.swarmplot(final, size=kwargs.get("markersize", 6), marker="o", orient="h", palette=[colors["deletion"], colors["addition"]], ax=ax)
    
#     # Invert the y-axis
#     ax.invert_yaxis()

#     ax.grid(axis='x', linestyle='--', alpha=0.7)
#     ax.set_xlabel("Count")
#     ax.set_ylabel("")
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')

# def diamond_swarm_fail_rate(df_test: TestSet,
#                             df_baseline: TestSet,
#                             filename: str= "../figures/general/fig1.2_swarm_fail_rate.pdf",
#                             ax=None,
#                             **kwargs: dict) -> None:
#     # Fail ratio per participant
#     fail_ratio_per_participant = get_fail_ratio_per_participant(df_test)
#     # Mean and std
#     # mean_fail_ratio = fail_ratio_per_participant.mean()
#     # std_fail_ratio = fail_ratio_per_participant.std()

#     fail_ratio_baseline_per_participant = get_fail_ratio_baseline_per_participant(df_baseline)
#     # # Mean and std
#     # mean_fail_ratio_baseline = fail_ratio_baseline_per_participant.mean()
#     # std_fail_ratio_baseline = fail_ratio_baseline_per_participant.std()
    
#     #Merge into single dataFrame and add a column for the type of data
#     # ! fail_ratio_per_participant has no column "Fail ratio" but no name for the column
#     df = pd.DataFrame(fail_ratio_per_participant).reset_index()
#     df["Role"] = "Interactive testers"
#     df_baseline = pd.DataFrame(fail_ratio_baseline_per_participant)
#     df_baseline["Role"] = "Independent annotators"

#     df = pd.concat([df, df_baseline])
#     stop()
#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=(kwargs.get("figsize", (7, 1.5))))
    

#     stop()
# def swarm_fail_rate(df_test: TestSet, 
#                     df_baseline: TestSet,
#                     filename: str= "../figures/general/fig1.2_swarm_number_of_test_cases.pdf", 
#                     ax=None,
#                     **kwargs: dict) -> None:
#     # Fail ratio per participant
#     fail_ratio_per_participant = get_fail_ratio_per_participant(df_test)
#     #
#     # Fail ratio per participant, baseline
#     fail_ratio_per_participant_baseline = get_fail_ratio_baseline(df_baseline)
    

    
#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=(kwargs.get("figsize", kwargs.get("figsize", (7, 1.5)))))
    
#     # Swarmplot
#     sns.swarmplot(fail_ratio_per_participant, size=kwargs.get("markersize", 6), marker="o", orient="h", c=colors["fail"], ax=ax)

#     plt.axvline(x=fail_ratio_per_participant_baseline, color=colors["fail"], linestyle='--', label="Error rate of the pre-trained model from independant annotators")
#     plt.grid(axis='x', linestyle='--', alpha=0.7)
#     ax.set_xlabel("Percentage (%)")
#     ax.set_yticklabels(["Fail ratio of participants'\ntest set"])
#     if ax_param is None:
#         plt.legend(loc='upper left', 
#                bbox_to_anchor=kwargs.get("bbox_to_anchor", (-0.35, -0.3)),
#                frameon=False)
#         plt.savefig(filename, bbox_inches='tight')


# def fig1_swarm_combined(df_test: TestSet, 
#                         df_ui: UserInteractions, 
#                         filename: str="../figures/general/fig1_swarm_combined.pdf", 
#                         **kwargs: dict) -> None:
    
#     # Create a figure with two subplots
#     _, axes = plt.subplots(2, 1, figsize= kwargs.get("figsize", (7, 3)), gridspec_kw={'height_ratios': kwargs.get("height_ratios", [1.5, 1])})

#     swarm_number_of_test_cases(df_ui, ax=axes[0], **{"figsize": (7,1.5)})
#     swarm_fail_rate(df_test, ax=axes[1], **{"figsize": (7,1)})

#     # Adding subplot labels (a) and (b)
#     axes[0].text(kwargs.get("label_x", -0.35), kwargs.get("label_y", 1.1), "a)",
#                  transform=axes[0].transAxes, fontsize=16, va='top')    
#     axes[1].text(kwargs.get("label_x", -0.35), kwargs.get("label_y", 1.1), "b)",
#                  transform=axes[1].transAxes, fontsize=16, va='top')
    
#     # Adjust the space between the subplots
#     plt.subplots_adjust(hspace=kwargs.get("hspace", 0.6))

#     #Legend outside the plot
#     plt.legend(loc='upper left', 
#                bbox_to_anchor= kwargs.get("bbox_to_anchor", (-0.35, -0.15)),
#                frameon=False)
#     plt.savefig(filename, bbox_inches='tight')


# def violin_fail_ratio_per_class(df_test: TestSet,
#                                 filename: str = "../figures/general/fig2.1_violin_fail_ratio_per_class.pdf",
#                                 ax = None,
#                                 **kwargs: dict) -> list:
#     # Fail ratio per participant per class
#     fail_ratio_per_participant_per_class = get_fail_ratio_per_participant_per_class(df_test)
   
#     # Sorting labels by mean fail ratio
#     mean_fail_ratio = fail_ratio_per_participant_per_class.groupby("Label")["Fail ratio"].mean().sort_values(ascending=False)
#     sorted_labels = mean_fail_ratio.index.to_list()
#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 8)))

#     # Create a fixed color palette mapping
#     unique_labels = df_test["Label"].unique()
#     original_palette = sns.color_palette("viridis", n_colors=len(unique_labels))
#     palette_dict = dict(zip(sorted_labels, original_palette))
#     darker_palette_dict = {label: darken_color(color, kwargs.get("darken", 0.8)) for label, color in palette_dict.items()}



#     # Violin plot with the fail ratio per class per participant
#     sns.violinplot(data=fail_ratio_per_participant_per_class,
#                   y="Label", 
#                   x="Fail ratio",
#                   hue="Label",
#                   order = sorted_labels,
#                   orient="h",
#                   palette= palette_dict,
#                   inner=None,
#                   alpha = kwargs.get("alpha", 0.5),
#                   ax = ax
#     )

#     # Swarmplot for individual participant
#     sns.swarmplot(data=fail_ratio_per_participant_per_class,
#                   y="Label", 
#                   x="Fail ratio",
#                   hue="Label",
#                   order=sorted_labels,
#                   orient="h",
#                   marker="o",
#                   palette= darker_palette_dict,
#                   size=kwargs.get("markersize", 7),
#                   alpha = kwargs.get("alpha_markers", 0.6),
#                   ax = ax
#     )

#     # Mean per class
#     sns.pointplot(data=fail_ratio_per_participant_per_class,
#                   y="Label",
#                   x="Fail ratio",
#                   order=sorted_labels,
#                   linestyle="none",
#                   estimator=np.mean,
#                   color='white',
#                   markers="d",
#                   ax=ax)
    

#     ax.set_xlabel("Test set fails' ratio (%)")
#     ax.set_xlim(kwargs.get("xlim", (-2, 101)))
#     ax.set_xticks(np.arange(0, 101, 10))
#     ax.grid(axis='x', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')
#     return sorted_labels

# def violin_entropy_per_class(df_test: TestSet,
#                       sorted_labels: list,
#                       filename: str = "../figures/general/fig2.2_violin_entropy.pdf",
#                       ax = None,
#                       **kwargs: dict) -> None:
    
#     # Filter out the entropy per class
#     entropy = df_test[["participant_id", "Label", "Entropy"]]
    
    
#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 8)))
    
#     # Create a fixed color palette mapping
#     unique_labels = df_test["Label"].unique()
#     original_palette = sns.color_palette("viridis", n_colors=len(unique_labels))
#     palette_dict = dict(zip(sorted_labels, original_palette))
#     darker_palette_dict = {label: darken_color(color, kwargs.get("darken", 0.8)) for label, color in palette_dict.items()}

#     # Violin plot with the entropy per class per participant
#     sns.violinplot(data=entropy,
#                   y="Label", 
#                   x="Entropy",
#                   hue="Label",
#                   order = sorted_labels,
#                   orient="h",
#                   palette= palette_dict,
#                   inner=None,
#                   alpha = kwargs.get("alpha", 0.5),
#                   ax = ax
#     )

#     # Swarmplot for individual participant
#     sns.swarmplot(data=entropy,
#                   y="Label", 
#                   x="Entropy",
#                   hue="Label",
#                   order=sorted_labels,
#                   orient="h",
#                   marker="o",
#                   palette= darker_palette_dict,
#                   size=kwargs.get("markersize", 3),
#                   alpha = kwargs.get("alpha_markers", 0.6),
#                   ax = ax
#     )

#     # Mean per class
#     sns.pointplot(data=entropy,
#                   y="Label",
#                   x="Entropy",
#                   order=sorted_labels,
#                   linestyle="none",
#                   estimator=np.mean,
#                   color='white',
#                   markers="d",
#                   ax=ax)
    
#     ax.set_xlabel("Entropy")
#     ax.set_xlim(kwargs.get("xlim", (0, 3)))
#     ax.grid(axis='x', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')

# def point_distribution_per_class(df_test: TestSet,
#                                      sorted_labels: list,
#                                      filename: str = "../figures/general/fig2.3_point_distribution_per_class.pdf",
#                                      ax = None,
#                                      **kwargs: dict) -> None:
#     # TODO : Check if the absence of test cases for a class is handled correctly (set to 0)
        
#     # Number of test cases per class per participant
#     total_per_participant_per_class = get_final_number_of_tests_per_participant_per_class(df_test)

#     # If no item for a class and participant, set the number of test cases to 0
#     for label in sorted_labels:
#         for participant in total_per_participant_per_class["participant_id"].unique():
#             if not total_per_participant_per_class[(total_per_participant_per_class["participant_id"] == participant) & (total_per_participant_per_class["Label"] == label)].empty:
#                 continue
    
#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 8)))
    
#     # Create a fixed color palette mapping
#     unique_labels = df_test["Label"].unique()
#     original_palette = sns.color_palette("viridis", n_colors=len(unique_labels))
#     palette_dict = dict(zip(sorted_labels, original_palette))
#     darker_palette_dict = {label: darken_color(color, kwargs.get("darken", 0.8)) for label, color in palette_dict.items()}

#     # Swarmplot with the number of test cases per class per participant
#     sns.swarmplot(data=total_per_participant_per_class,
#                     y="Label", 
#                     x="Total test cases",
#                     hue="Label",
#                     order = sorted_labels,
#                     orient="h",
#                     palette= palette_dict,
#                     size=kwargs.get("markersize", 7),
#                     alpha = kwargs.get("alpha_markers", 0.6),
#                     marker="o",
#                     ax = ax
#         )
    
#     # Mean per class
#     sns.pointplot(data=total_per_participant_per_class,
#                     y="Label",
#                     x="Total test cases",
#                     hue="Label",
#                     order=sorted_labels,
#                     linestyle="none",
#                     estimator=np.mean,
#                     palette=darker_palette_dict,
#                     markers="d",
#                     ax=ax)

#     ax.set_xlabel("Number of test cases")
#     ax.set_xlim(kwargs.get("xlim", (0, 26)))
#     ax.grid(axis='x', linestyle='--', alpha=0.5)


#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')




# def fig2_violin_combined(df_test: TestSet, 
#                          filename: str="../figures/general/fig2_violin_combined.pdf", 
#                          **kwargs: dict) -> None:
    
#     # Create a figure with two subplots
#     fig, axes = plt.subplots(1, 3, figsize= kwargs.get("figsize", (15, 7)), gridspec_kw={'width_ratios': kwargs.get("width_ratios", [1, 1, 1])})

#     sorted_labels = violin_fail_ratio_per_class(df_test, ax=axes[0], **{"figsize": (7,8)})
#     violin_entropy_per_class(df_test, sorted_labels, ax=axes[1], **{"figsize": (7,8)})
#     point_distribution_per_class(df_test, sorted_labels, ax=axes[2], **{"figsize": (7,8)})

#     # Adding subplot labels (a) and (b)
#     axes[0].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.05), "a)", transform=axes[0].transAxes, fontsize=16, va='top')
#     axes[1].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.05), "b)", transform=axes[1].transAxes, fontsize=16, va='top')
#     axes[2].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.05), "c)", transform=axes[2].transAxes, fontsize=16, va='top')

#     # Adjust the space between the subplots
#     plt.subplots_adjust(wspace=kwargs.get("wspace", 0.085))

#     # Remove yticks labels from the second and third plot
#     for ax in axes[1:]:
#         ax.set_yticklabels([])
#         ax.set_ylabel("")



#     #Legend outside the plot
#     plt.legend(loc='upper left', 
#                bbox_to_anchor= kwargs.get("bbox_to_anchor", (-0.35, -0.15)),
#                frameon=False)
    
#     plt.savefig(filename, bbox_inches='tight')
    

# def timeline_curricula(df_ui: UserInteractions,
#                        show_pauses: bool = False,
#                        filename: str="../figures/general/timeline_curricula.pdf",
#                        ax=None,
#                        **kwargs: dict) -> None:

#     # Sort participants by the ratio between number of "add" and number of "check" actions
#     check_counts = df_ui[df_ui["action"] == "check"].groupby("participant_id").size().reset_index(name='Number of checks').astype(int)

#     # Get the number of "add" action per participant
#     added = df_ui[df_ui["action"] == "add"].groupby("participant_id").size().reset_index(name='Test cases added').astype(int)

#     # Ratio between number of "add" and number of "check" actions
#     check_counts["Test cases added"] = added["Test cases added"]

#     # Calculate the ratio
#     check_counts["Ratio"] = check_counts["Number of checks"] / check_counts["Test cases added"]
    
#     # Sort the participants by the ratio
#     check_counts = check_counts.sort_values(by="Ratio", ascending=True)

#     # Create timelines for each participants (x-axis: time, y-axis: participant, sorted by the ratio)
#     # Horizontal line + markers for the different actions

#     selected_actions = ["add", "check", ["drag", "zoom", "center", "randomize"]]
#     selected_actions_flattened = [action for sublist in selected_actions for action in (sublist if isinstance(sublist, list) else [sublist])]

#     # Reflexion time = period of time > 10 seconds without any actions from selected_actions
#     reflexions = get_reflexion_time(df_ui, 10, selected_actions_flattened)
    

#     # Create a figure
#     ax_param = ax
#     if ax is None:
#         fig, ax = plt.subplots(figsize=kwargs.get("figsize", (12, 4)))

#     # Create a color palette
#     palette_actions = sns.color_palette([ colors["addition"], colors["check"], colors["interaction"]])

#     palette_dict = {}
#     for i in range(len(selected_actions)):
#         if isinstance(selected_actions[i], str):
#             palette_dict[selected_actions[i].capitalize()] = palette_actions[i]
#         else:
#             palette_dict["Data browsing and test cases creation"] = palette_actions[i]
    
#     # Create an horizontal black line for each participant (sorted by the ratio)
#     for i, participant in enumerate(check_counts["participant_id"]):
#         ax.axhline(y=i, color="black", linestyle="-", zorder=0, linewidth=4)
#         # Scatter for each type of action
#         for j, action in enumerate(selected_actions):
#             if isinstance(action, str):
#                 y_tweak = (j + 1) * 0.2
#                 action_df = df_ui[(df_ui["participant_id"] == participant) & (df_ui["action"] == action)]
#                 ax.scatter(action_df["timestamp"], [i + y_tweak]*len(action_df) , color=palette_dict[action.capitalize()], label=action.capitalize(), s=kwargs.get("markersize", 10), marker= "o" if action == "add" else "v", zorder=100)
#             else:
#                 action_df = df_ui[(df_ui["participant_id"] == participant) & (df_ui["action"].isin(action))]
#                 ax.scatter(action_df["timestamp"], [i]*len(action_df), color=palette_dict["Data browsing and test cases creation"], label="Data browsing and test cases creation", s=kwargs.get("markersize", 1), zorder=2, marker="s")

#         # Reflexion times = segments
#         if show_pauses:
#             reflexion_df = reflexions[reflexions["participant_id"] == participant]
#             for _, row in reflexion_df.iterrows():
#                 # Avoid border effect 
#                 ax.plot([row["start_time"], row["start_time"] + row["time_diff"]], [i, i], color=colors["reflexion"], zorder=1, linewidth=2)
    
#     # Set the yticks labels
#     ax.set_yticks(np.arange(len(check_counts)))
#     ax.set_yticklabels(check_counts["participant_id"])
#     ax.set_xlabel("Time (minutes)")
#     ax.set_ylabel("Participant ID")
#     ax.set_xlim(kwargs.get("xlim", (0, max(df_ui["timestamp"]))))

#     # Grid in background
#     ax.grid(axis='x', linestyle='--', alpha=0.5, zorder=-10)
#     # Export the figure
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')
    
    


# def lollipop_iterative(df_ui: UserInteractions,
#                           filename: str="../figures/general/lollipop_iterative.pdf",
#                           ax=None,
#                           **kwargs: dict) -> None:
    
#     # Sort participants by the ratio between number of "add" and number of "check" actions
#     check_counts = get_number_of_test_checked_per_participant(df_ui)

#     # Get the number of "add" action per participant
#     added = df_ui[df_ui["action"] == "add"].groupby("participant_id").size().reset_index(name='Test cases added').astype(int)

#     # Ratio between number of "add" and number of "check" actions
#     check_counts["Test cases added"] = added["Test cases added"]

#     # Calculate the ratio
#     check_counts["Ratio of test cases' addition/check"] = check_counts["Total test cases checked"] / check_counts["Test cases added"]

#     # Sort the participants by the ratio
#     check_counts = check_counts.sort_values(by="Ratio of test cases' addition/check", ascending=True)
#     sorted_participants = check_counts["participant_id"]

#     ratio_range = range(0, len(sorted_participants))

#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (5, 5)))

#     # The horizontal plot is made using the hline function
#     ax.hlines(y=ratio_range, xmin=0, xmax=check_counts["Ratio of test cases' addition/check"])
#     ax.plot(check_counts["Ratio of test cases' addition/check"], ratio_range, "o")

#     # Add ticks and axis names
#     ax.yaxis.set_ticks(ratio_range)
#     ax.yaxis.set_ticklabels(sorted_participants)
#     ax.set_xlabel("Ratio of test cases' addition/check")
#     ax.set_ylabel("Participant ID")
#     ax.grid(axis='x', linestyle='--', alpha=0.5)

#     ax.set_xlim(kwargs.get("xlim", [0, max(check_counts["Ratio of test cases' addition/check"])+ 0.1] ))

#     # Save the figure
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')
#     return sorted_participants

# def fig3_curricula(df_ui: UserInteractions,
#                     filename: str="../figures/general/fig3_curricula.pdf",
#                     **kwargs: dict) -> None:
     
#     # Create a figure with two subplots
#     fig, axes = plt.subplots(1, 2, figsize= kwargs.get("figsize", (16, 5)), gridspec_kw={'width_ratios': kwargs.get("width_ratios", [3, 1])}, sharey=True)
    
#     timeline_curricula(df_ui, ax=axes[0], **{"figsize": (7, 4)})
#     sorted_participants = lollipop_iterative(df_ui, ax=axes[1], **{"figsize": (5, 5)})
    
#     # Adding subplot labels (a) and (b)
#     axes[0].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "a)", transform=axes[0].transAxes, fontsize=16, va='top')
#     axes[1].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "b)", transform=axes[1].transAxes, fontsize=16, va='top')

#     axes[1].set_ylabel("")
    
#     # Adjust the space between the subplots
#     plt.subplots_adjust(wspace=kwargs.get("wspace", 0.05))

#     #Custom legend outside the plot
#     # Create a custom legend
#     custom_lines = [matplotlib.lines.Line2D([0], [0], color=colors["addition"], marker='o', linestyle='None'),
#                     matplotlib.lines.Line2D([0], [0], color=colors["check"], marker='o', linestyle='None'),
#                     matplotlib.lines.Line2D([0], [0], color=colors["interaction"], marker='s', linestyle='None')]

#     axes[0].legend(custom_lines, ['Addition of a test case', 'Check test cases', 'Input browsing/searching', 'Reflexion'], loc='upper left', bbox_to_anchor=(0.1, 1.09), frameon=False, ncol=4)

    
#     # Save the figure
#     plt.savefig(filename, bbox_inches='tight')


# ! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# def scatter_iterative_fail_ratio(df_test: TestSet,
#                                  df_ui: UserInteractions,
#                                 filename: str="../figures/general/scatter_iterative_fail_ratio.pdf",
#                                 ax=None,
#                                 **kwargs: dict) -> None:
    
#     # Fail ratio per participant
#     fails_ratio = get_fail_ratio_per_participant(df_test)

#     # Number of test cases added in total
#     added = get_number_of_test_added_per_participant(df_ui)
#     # Number of check
#     check = get_number_of_test_checked_per_participant(df_ui)

#     # Ratio between number of "add" and number of "check" actions
#     check["Test cases added"] = added["Total test cases added"]
#     check["Ratio of test cases' added/checked"] = check["Total test cases checked"] / check["Test cases added"] * 100

#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))
    
#     # Scatter plot and linreg using sns
#     sns.regplot(data=check, x="Ratio of test cases' added/checked", y=fails_ratio, ax=ax)
#     # Plot statistics on the graph (R2, + linear regression function y = ax + b)
#     correlation, p_value = pearsonr(check["Ratio of test cases' added/checked"], fails_ratio)
#     r2 = round(correlation ** 2, 2)
#     slope, intercept, r_value, p_val, std_err = stats.linregress(check["Ratio of test cases' added/checked"], fails_ratio)

#     slope = round(np.corrcoef(check["Ratio of test cases' added/checked"], fails_ratio)[0, 1], 2)
#     intercept = round(np.mean(fails_ratio), 2)
    
    
#     # Determining the number of stars based on p-value
#     if p_value < 0.001:
#         stars = '***'  # Very strong significance
#     elif p_value < 0.01:
#         stars = '**'   # Strong significance
#     elif p_value < 0.05:
#         stars = '*'    # Significant
#     else:
#         stars = ''     # Not significant

#     # Displaying correlation, p-value, and regression line equation
#     ax.text(0.05, 0.95, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {round(slope, 2)}x + {round(intercept, 2)}",
#         transform=ax.transAxes, fontsize=12, va='top')

#     # Set the labels
#     ax.set_xlabel("Ratio of test cases' added/checked (in %)")
#     ax.set_ylabel("Test cases' fail ratio (in %)")
#     ax.set_xlim(kwargs.get("xlim", (0, 101)))
#     ax.set_ylim(kwargs.get("ylim", (0, 100)))
#     ax.grid(axis='both', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')

# def scatter_iterative_number_of_tests(df_ui: UserInteractions,
#                                 filename: str="../figures/general/scatter_iterative_fail_ratio.pdf",
#                                 ax=None,
#                                 **kwargs: dict) -> None:
#     # Number of test cases added in total (added - removed) per participant
#     added = get_number_of_test_added_per_participant(df_ui)
#     # Number of test cases deleted
#     deleted = get_number_of_test_deleted_per_participant(df_ui)

#     merged_count = get_final_number_of_tests_per_participant(df_ui)

#     merged_count = pd.merge(pd.DataFrame(added), pd.DataFrame(deleted), on='participant_id', how='outer').fillna(0)

#     # Number of test cases at the end of the session
#     merged_count["Final number of test cases"] = merged_count["Total test cases added"] - merged_count["Total test cases deleted"].astype(int)

    
#     # Number of check
#     final = df_ui[df_ui["action"] == "check"].groupby("participant_id").size().reset_index(name='Number of checks').astype(int)

#     # Ratio between number of "add" and number of "check" actions
#     final["Test cases added"] = added["Total test cases added"]
#     final["Ratio of test cases' added/checked"] = final["Number of checks"] / final["Test cases added"] * 100

#     final["Final number of test cases"] = merged_count["Final number of test cases"]

#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))

#     # Scatter plot and linreg using sns
#     sns.regplot(data=final, x="Ratio of test cases' added/checked", y="Final number of test cases", ax=ax)

#     # Computing Pearson correlation and p-value
#     correlation, p_value = pearsonr(final["Ratio of test cases' added/checked"], final["Final number of test cases"])
#     slope, intercept, r_value, p_val, std_err = stats.linregress(final["Ratio of test cases' added/checked"], final["Final number of test cases"])
#     r2 = round(correlation ** 2, 2)

#     # Determining the number of stars based on p-value
#     if p_value < 0.001:
#         stars = '***'  # Very strong significance
#     elif p_value < 0.01:
#         stars = '**'   # Strong significance
#     elif p_value < 0.05:
#         stars = '*'    # Significant
#     else:
#         stars = ''     # Not significant

#     # Displaying correlation, p-value, and regression line equation
#     ax.text(0.08, 0.95, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
#             transform=ax.transAxes, fontsize=12, va='top')

#     # Set the labels
#     ax.set_xlabel("Ratio of test cases' added/checked (in %)")
#     ax.set_ylabel("Final number of test cases")
#     ax.set_xlim(kwargs.get("xlim", (0, 101)))
#     ax.set_ylim(kwargs.get("ylim", (0, max(final["Final number of test cases"])+20)))
#     ax.grid(axis='both', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')

# def scatter_mental_model_number_of_test_cases_created(df_ui: UserInteractions,
#                                       df_questionnaire: QuestionnaireAnswers,
#                                         filename: str="../figures/general/scatter_iterative_fail_ratio.pdf",
#                                         ax=None,
#                                         **kwargs: dict) -> None:
#     # X axis : mental model score in df_questionnaire
#     # Y axis : number of test cases created in df_ui

#     # Number of test cases added in total (added - removed) per participant
#     added = get_number_of_test_added_per_participant(df_ui)
#     # Number of test cases deleted
#     deleted = get_number_of_test_deleted_per_participant(df_ui)
#     # Number of test cases at the end of the session
#     merged_count = pd.merge(pd.DataFrame(added), pd.DataFrame(deleted), on='participant_id', how='outer').fillna(0)
#     merged_count["Final number of test cases"] = merged_count["Total test cases added"] - merged_count["Total test cases deleted"].astype(int)

#     # Mental model score
#     mental_model = df_questionnaire[["Participant ID: ID", "Mental model score"]]
#     mental_model.rename(columns={"Participant ID: ID": "participant_id"}, inplace=True)
#     # Merge with the number of test cases

#     merged_count = pd.merge(merged_count, mental_model, on="participant_id", how="inner").fillna(0)

#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))
    
#     # Scatter plot and linreg using sns
#     sns.regplot(data=merged_count, x="Mental model score", y="Final number of test cases", ax=ax)

#     # Computing Pearson correlation and p-value
#     correlation, p_value = pearsonr(merged_count["Mental model score"], merged_count["Final number of test cases"])
#     slope, intercept, r_value, p_val, std_err = stats.linregress(merged_count["Mental model score"], merged_count["Final number of test cases"])
#     r2 = round(correlation ** 2, 2)

#     # Determining the number of stars based on p-value
#     if p_value < 0.001:
#         stars = '***'
#     elif p_value < 0.01:
#         stars = '**'
#     elif p_value < 0.05:
#         stars = '*'
#     else:
#         stars = ''
    
#     # Displaying correlation, p-value, and regression line equation
#     ax.text(0.08, 0.95, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
#             transform=ax.transAxes, fontsize=12, va='top')
    
#     # Set the labels
#     ax.set_xlabel("Mental model score")
#     ax.set_ylabel("Final number of test cases")
#     ax.set_xlim(kwargs.get("xlim", (1.75, 5.25)))
#     ax.set_ylim(kwargs.get("ylim", (-10, max(merged_count["Final number of test cases"])+20)))
#     ax.grid(axis='both', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')

# def scatter_mental_model_ratio_added_checked(df_ui: UserInteractions,
#                                              df_questionnaire: QuestionnaireAnswers,
#                                             filename: str="../figures/general/scatter_iterative_fail_ratio.pdf",
#                                             ax=None,
#                                             **kwargs: dict) -> None:
#     # X axis : mental model score in df_questionnaire
#     # Y axis : ratio of test cases added/checked in df_ui

#     # Number of test cases added in total (added - removed) per participant
#     added = get_number_of_test_added_per_participant(df_ui)
#     # Number of test cases deleted
#     deleted = get_number_of_test_deleted_per_participant(df_ui)
#     # Number of test cases at the end of the session
#     merged_count = pd.merge(pd.DataFrame(added), pd.DataFrame(deleted), on='participant_id', how='inner').fillna(0)
#     merged_count["Final number of test cases"] = merged_count["Total test cases added"] - merged_count["Total test cases deleted"].astype(int)
    
#     # Number of check
#     final = df_ui[df_ui["action"] == "check"].groupby("participant_id").size().reset_index(name='Number of checks').astype(int)

#     # Ratio between number of "add" and number of "check" actions
#     final["Test cases added"] = added["Total test cases added"]

#     final["Ratio of test cases' added/checked"] = final["Number of checks"] / final["Test cases added"] * 100

#     final["Final number of test cases"] = merged_count["Final number of test cases"]

#     # Mental model score
#     mental_model = df_questionnaire[["Participant ID: ID", "Mental model score"]]
#     mental_model.rename(columns={"Participant ID: ID": "participant_id"}, inplace=True)
#     # Merge with the number of test cases

#     merged_count = pd.merge(final, mental_model, on="participant_id", how="inner").fillna(0)

#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))

#     # Scatter plot and linreg using sns green color
#     sns.regplot(data=merged_count, x="Mental model score", y="Ratio of test cases' added/checked", ax=ax, color=colors["success"])

#     # Computing Pearson correlation and p-value
#     correlation, p_value = pearsonr(merged_count["Mental model score"], merged_count["Ratio of test cases' added/checked"])
#     slope, intercept, r_value, p_val, std_err = stats.linregress(merged_count["Mental model score"], merged_count["Ratio of test cases' added/checked"])
#     r2 = round(correlation ** 2, 2)

#     # Determining the number of stars based on p-value
#     if p_value < 0.001:
#         stars = '***'
#     elif p_value < 0.01:
#         stars = '**'    
#     elif p_value < 0.05:
#         stars = '*'
#     else:
#         stars = ''
    
#     # Displaying correlation, p-value, and regression line equation
#     ax.text(0.08, 0.85, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
#             transform=ax.transAxes, fontsize=12, va='top')
    
#     # Set the labels
#     ax.set_xlabel("Mental model score")
#     ax.set_ylabel("Ratio of test cases' added/checked (in %)")
#     ax.set_xlim(kwargs.get("xlim", (1.75, 5.25)))
#     ax.set_ylim(kwargs.get("ylim", (-20, 105))
#     )

#     ax.grid(axis='both', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')

# def scatter_mental_model_fail_ratio(df_test: TestSet,
#                             df_questionnaire: QuestionnaireAnswers,
#                             filename: str="../figures/general/mental_model_fail_ratio.pdf",
#                             ax=None,
#                             **kwargs: dict) -> None:
#     # X axis : mental model score in df_questionnaire
#     # Y axis : number of test cases created in df_ui

#     # Fail ratio per participant as a Series
#     fails_ratio = get_fail_ratio_per_participant(df_test)
    
#     # Create a columnn participant_id and Fail ratio
#     fails_ratio = pd.DataFrame(fails_ratio).reset_index()
#     fails_ratio.rename(columns={"index": "participant_id", 0: "Fail ratio"}, inplace=True) 
    
    
#     # Mental model score
#     mental_model = df_questionnaire[["Participant ID: ID", "Mental model score"]]
#     mental_model.rename(columns={"Participant ID: ID": "participant_id"}, inplace=True)
#     # Merge with the number of test cases
#     merged_count = pd.merge(fails_ratio, mental_model, on="participant_id", how="inner").fillna(0)

#     ax_param = ax
#     if ax is None:
#         _, ax = plt.subplots(figsize=kwargs.get("figsize", (7, 5)))
    
#     # Scatter plot and linreg using sns
#     sns.regplot(data=merged_count, x="Mental model score", y="Fail ratio", ax=ax, color=colors["fail"])

#     # Computing Pearson correlation and p-value
#     correlation, p_value = pearsonr(merged_count["Mental model score"], merged_count["Fail ratio"])
#     slope, intercept, r_value, p_val, std_err = stats.linregress(merged_count["Mental model score"], merged_count["Fail ratio"])
#     r2 = round(correlation ** 2, 2)

#     # Determining the number of stars based on p-value
#     if p_value < 0.001:
#         stars = '***'
#     elif p_value < 0.01:
#         stars = '**'    
#     elif p_value < 0.05:
#         stars = '*'
#     else:
#         stars = ''
    
#     # Displaying correlation, p-value, and regression line equation
#     ax.text(0.08, 0.3, f"R² = {r2}\nP-value: {p_value:.3f}{stars}\ny = {slope:.2f}x + {intercept:.2f}",
#             transform=ax.transAxes, fontsize=12, va='top')

#     # Set the labels
#     ax.set_xlabel("Mental model score")
#     ax.set_ylabel("Fail ratio (in %)")
#     ax.set_xlim(kwargs.get("xlim", (1.75, 5.25)))
#     ax.set_ylim(kwargs.get("ylim", (10, 45)))
#     ax.grid(axis='both', linestyle='--', alpha=0.5)
#     if ax_param is None:
#         plt.savefig(filename, bbox_inches='tight')
    



        

    

# def fig4_iterative(df_test: TestSet, 
#                         df_ui: UserInteractions,
#                         filename: str="../figures/general/fig4_iterative.pdf", 
#                         **kwargs: dict) -> None:

#     # Create a figure with two subplots
#     fig, axes = plt.subplots(1, 2, figsize= kwargs.get("figsize", (12, 5)), gridspec_kw={'width_ratios': kwargs.get("width_ratios", [1, 1])}, sharex=True)

#     # Set ylim to 60
#     scatter_iterative_fail_ratio(df_test, df_ui, ax=axes[0], **{"figsize": (5, 5), "ylim": (10, 50)})
    

#     scatter_iterative_number_of_tests(df_ui, ax=axes[1], **{"figsize": (5, 5)})

#     # Adding subplot labels (a) and (b)
#     axes[0].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "a)", transform=axes[0].transAxes, fontsize=16, va='top')
#     axes[1].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "b)", transform=axes[1].transAxes, fontsize=16, va='top')

#     # Adjust the space between the subplots
#     plt.subplots_adjust(wspace=kwargs.get("wspace", 0.2))

#     # Save the figure
#     plt.savefig(filename, bbox_inches='tight')


# def fig5_mental_model(df_test: TestSet, 
#                         df_ui: UserInteractions,
#                         df_questionnaire: QuestionnaireAnswers,
#                         filename: str="../figures/general/fig5_mental_model.pdf", 
#                         **kwargs: dict) -> None:

#     # 3 horizontal subplots for the scatter plots
#     fig, axes = plt.subplots(1, 3, figsize= kwargs.get("figsize", (16, 5)), gridspec_kw={'width_ratios': kwargs.get("width_ratios", [1, 1, 1])}, sharex=True)

#     scatter_mental_model_number_of_test_cases_created(df_ui=df_ui, df_questionnaire=df_questionnaire, ax=axes[0], **{"figsize": (5, 5)})
#     scatter_mental_model_ratio_added_checked(df_ui=df_ui, df_questionnaire=df_questionnaire, ax=axes[1], **{"figsize": (5, 5)})
#     scatter_mental_model_fail_ratio(df_test=df_test, df_questionnaire=df_questionnaire, ax=axes[2], **{"figsize": (5, 5)})

#     # Adding subplot labels (a) and (b)
#     axes[0].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "a)", transform=axes[0].transAxes, fontsize=16, va='top')
#     axes[1].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "b)", transform=axes[1].transAxes, fontsize=16, va='top')
#     axes[2].text(kwargs.get("label_x", 0), kwargs.get("label_y", 1.07), "c)", transform=axes[2].transAxes, fontsize=16, va='top')

#     # Adjust the space between the subplots
#     plt.subplots_adjust(wspace=kwargs.get("wspace", 0.2))

#     # Save the figure
#     plt.savefig(filename, bbox_inches='tight')





    