import decimal
import math
import numpy as np
import random
from scipy.stats import norm


decimal.getcontext().prec = 800


def bootstrap_simulation(
        list_x: list[float],
        number_of_iterations: int,
        size_of_each_boostraps: int
) -> tuple[float, float]:
    """
    :param list_x: data to bootstrap
    :param number_of_iterations: how many bootstrap samples do we do - the more the better
    :param size_of_each_boostraps: how many individuals k are resampled at each iteration (usually k = len(list_x))

    :return: 2.5 and 97.5 percentiles (which correspond to the estimated CI)
    """
    list_samples_means: list[float] = []
    for iteration_counter in range(number_of_iterations):
        list_samples_one_iteration: list[float] = []
        for sample_counter in range(size_of_each_boostraps):
            list_samples_one_iteration.append(list_x[random.randrange(0, len(list_x))])
        list_samples_means.append(float(np.mean(list_samples_one_iteration)))
    # sort list_samples_means
    list_samples_means.sort()

    x_low = np.percentile(list_samples_means, 2.5)
    x_high = np.percentile(list_samples_means, 97.5)
    return x_low, x_high


def trinomial(n0: int, n1: int, n2: int, k: int) -> decimal.Decimal:
    return decimal.Decimal(math.factorial(k)) / (
        decimal.Decimal(math.factorial(n0))
        *
        decimal.Decimal(math.factorial(n1))
        *
        decimal.Decimal(math.factorial(n2))
    )


def analytic_probability_mean(
    t: int,
    k: int,
    estimated_p_0: decimal.Decimal,
    estimated_p_1: decimal.Decimal,
    estimated_p_2: decimal.Decimal,
) -> decimal.Decimal:
    """
    :return: the analytic probability that the bootstrap mean equals x = t / 2k (P(Xkr = x));
    by resampling a lot, we should get to this distribution.
    """

    somme: decimal.Decimal = decimal.Decimal(0)
    for n2 in range(max(0, t - k), int(t / 2) + 1):
        estimated_p_0 = decimal.Decimal(estimated_p_0)
        estimated_p_1 = decimal.Decimal(estimated_p_1)
        estimated_p_2 = decimal.Decimal(estimated_p_2)

        trinomial_val = trinomial(k + n2 - t, t - 2 * n2, n2, k)

        # the following if statements are to resolve the 0^0 problem c.f. https://stackoverflow.com/questions/71372106
        p0_terme: decimal.Decimal
        if estimated_p_0 == 0 and (k + n2 - t) == 0:
            p0_terme = decimal.Decimal(1)
        else:
            p0_terme = estimated_p_0 ** decimal.Decimal((k + n2 - t))

        p1_terme: decimal.Decimal
        if estimated_p_1 == 0 and (t - 2 * n2) == 0:
            p1_terme = decimal.Decimal(1)
        else:
            p1_terme = estimated_p_1 ** decimal.Decimal((t - 2 * n2))

        p2_terme: decimal.Decimal
        if estimated_p_2 == 0 and n2 == 0:
            p2_terme = decimal.Decimal(1)
        else:
            p2_terme = estimated_p_2 ** decimal.Decimal(n2)

        # adding
        somme += trinomial_val * p0_terme * p1_terme * p2_terme

    return somme


def bootstrap_bca_simulation(
        list_x: list[float],
        estimated_mean: float,
        number_of_iterations: int,
        size_of_each_boostraps: int
) -> tuple[float, float]:
    """
    :param list_x: data to bootstrap
    :param estimated_mean: the mean of the original test sample
    :param number_of_iterations: how many bootstrap samples do we do - the more the better
    :param size_of_each_boostraps: how many individuals k are resampled at each iteration (usually k = len(list_x))

    :return: k1 and k2 percentiles (which correspond to the estimated CI of the Bias-Corrected and Accelerated
             Bootstrap method)
    """
    list_samples_means: list[float] = []
    number_of_times_bootstrap_mean_is_less_than_original_mean: int = 0
    for iteration_counter in range(number_of_iterations):
        list_samples_one_iteration: list[float] = []
        for sample_counter in range(size_of_each_boostraps):
            list_samples_one_iteration.append(list_x[random.randrange(0, len(list_x))])
        mean_of_this_sample: float = float(np.mean(list_samples_one_iteration))
        list_samples_means.append(mean_of_this_sample)
        if mean_of_this_sample/2 < estimated_mean:
            number_of_times_bootstrap_mean_is_less_than_original_mean += 1

    assert number_of_times_bootstrap_mean_is_less_than_original_mean <= number_of_iterations

    # sort list_samples_means
    list_samples_means.sort()

    # compute the bias correction factor z_0_hat
    z_0_hat: float = norm.ppf(
        number_of_times_bootstrap_mean_is_less_than_original_mean / number_of_iterations
    )

    # compute the acceleration factor a_hat
    sum_list_k: float = sum(list_x)

    a_hat_numerator: float = 0
    for k in range(len(list_x)):
        a_hat_numerator += (
            2*estimated_mean - ((sum_list_k - list_x[k]) / (len(list_x) - 1))
        )**3

    a_hat_denominator: float = 0
    for k in range(len(list_x)):
        a_hat_denominator += (
            2*estimated_mean - ((sum_list_k - list_x[k]) / (len(list_x) - 1))
        )**2
    a_hat_denominator = 6*a_hat_denominator**(3/2)

    a_hat: float
    if a_hat_denominator != 0:
        a_hat = a_hat_numerator / a_hat_denominator
    else:
        a_hat = 0

    # compute mu_k1 and mu_k2
    z_alpha_div_2: float = norm.ppf(0.025)
    z_1_minus_alpha_div_2: float = norm.ppf(0.975)

    try:
        mu_k1: float = list_samples_means[
            int(
                round(
                    norm.cdf(
                        z_0_hat + ((z_0_hat + z_alpha_div_2) / (1 - a_hat * (z_0_hat + z_alpha_div_2)))
                    ) * number_of_iterations,
                    0
                )
            )
        ]
    except ValueError:
        mu_k1 = 0
    try:
        mu_k2: float = list_samples_means[
            int(
                round(
                    norm.cdf(
                        z_0_hat + ((z_0_hat + z_1_minus_alpha_div_2) / (1 - a_hat * (z_0_hat + z_1_minus_alpha_div_2)))
                    ) * number_of_iterations,
                    0
                )
            )
        ]
    except ValueError:
        mu_k2 = 1

    return mu_k1, mu_k2
