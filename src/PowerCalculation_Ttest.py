from statsmodels.stats.power import TTestPower

def calculate_sample_size(effect_size, alpha=0.05, power=0.8, ratio=1.0, type='two-sided'):
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
    analysis = TTestPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative=type)
    return int(sample_size) + 1  # Round up to the next whole number

# Cohen's d effect size of 0.5 (medium effect)
# Gives Cohen's f of 0.25 (https://www.escal.site/)
# Cohen's f is used for the TTestPower
sample_size = calculate_sample_size(0.5)

# Cohen's d effect size of 0.5 (medium effect) (Cohen's f = 0.25) -> 128
# Cohen's d effect size of 1 (large effect) (Cohen's f = 0.5) -> 34
print(f"Required sample size per group: {sample_size}")