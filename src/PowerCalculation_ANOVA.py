from statsmodels.stats.power import FTestAnovaPower

def calculate_sample_size(effect_size, alpha=0.05, power=0.8, groups=2.0):
    """
    Calculate the required sample size for a two-sample t-test.

    Parameters:
    effect_size (float): The expected effect size (Cohen's d).
    alpha (float): The significance level (default is 0.05).
    power (float): The desired power of the test (default is 0.8).
    ratio (float): The ratio of sample sizes between the two groups (default is 1.0).

    Returns:
    int: The required sample size for each group.
    """
    analysis = FTestAnovaPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, k_groups=groups)
    return int(sample_size) + 1  # Round up to the next whole number

sample_size = calculate_sample_size(effect_size=0.5, groups=4)

print(f"Required sample size per group: {sample_size}")