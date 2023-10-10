## Imports
import argparse
import decimal
import numpy as np
import os
import random
import time

from csv import writer
from matplotlib import pyplot as plt
from scipy import stats
from scipy.stats import norm

from aux_f import bootstrap_simulation, analytic_probability_mean, bootstrap_bca_simulation

decimal.getcontext().prec = 800


if __name__ == "__main__":
    ###
    ### Initialisation
    ###

    # Scores (-1: below, 0: inside the CI, 1: above)
    bootstrap_5_score: int = 0
    bootstrap_last_score: int = 0
    bootstrap_analytical_score: int = 0
    bootstrap_bca_5_score: int = 0
    bootstrap_bca_last_score: int = 0
    clt_slutsky_score: int = 0
    t_distribution_score: int = 0

    print("---")
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1998)
    parser.add_argument("--test_set_size", type=int, default=1000)
    parser.add_argument("--p0", type=float, default=0.05)
    parser.add_argument("--p1", type=float, default=0.20)
    parser.add_argument("--p2", type=float, default=0.75)
    parser.add_argument("--figures", type=bool, default=False)
    """
    When using Python's argparse library, the bool type doesn't really work well for command-line arguments because it
    treats any non-empty string as True.
    Therefore, unless you want it to be True, don't specify it.
    """

    args = parser.parse_args()
    seed: int = args.seed
    print("Seed:", seed)
    test_set_size: int = args.test_set_size  # n
    print("Test Set Size:", test_set_size)
    p0: float = args.p0
    print("p0:", p0)
    p1: float = args.p1
    print("p1:", p1)
    p2: float = args.p2
    print("p2:", p2)

    ###
    ### Random seed
    ###
    random.seed(seed)

    ###
    ### True parameters
    ###
    if p0 + p1 + p2 != 1:
        print("Error 0: p0 + p1 + p2 is not equal to 1")
        exit()
    # here we know the values but we actually don't in real life!
    mu: float = (0 * p0 + 1 * p1 + 2 * p2)/2
    print("True mean:", round(mu, 5))  # mu is what we are looking for

    if args.figures:
        try:
            os.mkdir(f"figures/{p0}-{p1}-{p2}")
        except FileExistsError:
            pass
        except Exception as e:
            print(e)
            exit()

    ###
    ### Main
    ###
    resampling_set_size: int = test_set_size  # k
    # because we want to estimate the CI of the announced estimated mean
    # which was estimated on the whole test dataset

    list_x: list[int] = []  # sample (test_set)
    for _ in range(test_set_size):
        random_number = random.random()
        if random_number < p0:
            x = 0
        elif random_number < p0 + p1:
            x = 1
        else:
            x = 2
        list_x.append(x)

    estimated_p_0: decimal.Decimal = decimal.Decimal(list_x.count(0)) / decimal.Decimal(test_set_size)
    estimated_p_1: decimal.Decimal = decimal.Decimal(list_x.count(1)) / decimal.Decimal(test_set_size)
    estimated_p_2: decimal.Decimal = decimal.Decimal(list_x.count(2)) / decimal.Decimal(test_set_size)
    estimated_mean: float = float(np.mean(list_x))/2
    estimated_std: float = float(np.std(list_x, ddof=1))/2  # ddof = 1 because of Bessel's correction
    print("estimated p0:", estimated_p_0)  # should be close to p0
    print("estimated p1:", estimated_p_1)  # should be close to p1
    print("estimated p2:", estimated_p_2)  # should be close to p2
    print("estimated mean:", round(estimated_mean, 5))
    print("estimated standard deviation:", round(estimated_std, 5))

    #
    # Naked estimated and true mean graphs
    #
    if args.figures:
        plt.axhline(y=mu, color='#841D37', linestyle='-', label="True mean")
        plt.axhline(y=estimated_mean, color='#841D37', linestyle='-', label="Estimated mean", alpha=0.5)

        plt.xlabel('Number of boostrap iterations')
        plt.ylabel(u"\u03bc")
        plt.title('n = ' + str(test_set_size) + ', k = ' + str(resampling_set_size))
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

        # x&y axis limits
        plt.xlim(0, 5000)
        plt.ylim(mu - 0.4, mu + 0.4)

        plt.savefig(
            f"figures{os.sep}{p0}-{p1}-{p2}{os.sep}output_naked_seed{seed}_n{test_set_size}.png",
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()

    #
    # CLTSlutsky CI
    #
    # Finding the z-value for the right tail (97.5% quantile)
    z_0_025: float = norm.ppf(1 - 0.025)
    z09750_10_digits: float = round(z_0_025, 10)

    lower_bound_CLTslutsky_10_digits = estimated_mean - z09750_10_digits * (
        estimated_std / np.sqrt(test_set_size)
    )
    upper_bound_CLTslutsky_10_digits = estimated_mean + z09750_10_digits * (
        estimated_std / np.sqrt(test_set_size)
    )

    ## Plotting CLTSlutsky CI
    if args.figures:
        plt.axhline(y=mu, color='#841D37', linestyle='-', label="True mean")
        plt.axhline(y=estimated_mean, color='#841D37', linestyle='-', label="Estimated mean", alpha=0.5)

        plt.axhline(y=lower_bound_CLTslutsky_10_digits, color='#ABA194', linestyle='--', label="Gaussian lower bound")
        plt.axhline(y=upper_bound_CLTslutsky_10_digits, color='#ABA194', linestyle='--', label="Gaussian upper bound")

        # x&y axis limits
        plt.xlim(0, 5000)
        plt.ylim(estimated_mean - 0.37, estimated_mean + 0.37)

        plt.xlabel('Number of boostrap iterations')
        plt.ylabel(u"\u03bc")
        plt.title('n = ' + str(test_set_size) + ', k = ' + str(resampling_set_size))
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')


        plt.savefig(
            f"figures{os.sep}"
            f"{p0}-{p1}-{p2}{os.sep}"
            f"output_gaussian_seed{seed}_n{test_set_size}.png",
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()

    if lower_bound_CLTslutsky_10_digits <= mu <= upper_bound_CLTslutsky_10_digits:
        clt_slutsky_score = 0
    elif mu < lower_bound_CLTslutsky_10_digits:
        clt_slutsky_score = -1
    elif mu > upper_bound_CLTslutsky_10_digits:
        clt_slutsky_score = 1
    else:
        raise ValueError("clt_slutsky_score should be -1, 0 or 1")

    #
    # Student's t distribution with n-1 degrees of freedom
    #
    t09750_10_digits: float = stats.t(df=test_set_size).ppf((0.025, 0.975))[1]
    lower_bound_Student_10_digits = estimated_mean - t09750_10_digits * (
        estimated_std / np.sqrt(test_set_size)
    )
    upper_bound_Student_10_digits = estimated_mean + t09750_10_digits * (
        estimated_std / np.sqrt(test_set_size)
    )

    ### Plotting CLTSlutsky CI + Student's t CI
    if args.figures:
        plt.axhline(y=mu, color='#841D37', linestyle='-', label="True mean")
        plt.axhline(y=estimated_mean, color='#841D37', linestyle='-', label="Estimated mean", alpha=0.5)

        plt.axhline(
            y=lower_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian lower bound",
        )
        plt.axhline(
            y=upper_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian upper bound",
        )

        plt.axhline(
            y=lower_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution lower bound",
        )
        plt.axhline(
            y=upper_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution upper bound",
        )

        # x&y axis limits
        plt.xlim(0, 5000)
        plt.ylim(estimated_mean - 0.37, estimated_mean + 0.37)

        plt.xlabel("Number of boostrap iterations")
        plt.ylabel(u"\u03bc")
        plt.title(
            "n = "
            + str(test_set_size)
            + ", k = "
            + str(resampling_set_size)
        )
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")

        plt.savefig(
            f"figures/"
            f"{p0}-{p1}-{p2}/"
            f"output_gaussian_tDistribution_seed{seed}_n{test_set_size}.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    if lower_bound_Student_10_digits <= mu <= upper_bound_Student_10_digits:
        t_distribution_score = 0
    elif mu < lower_bound_Student_10_digits:
        t_distribution_score = -1
    elif mu > upper_bound_Student_10_digits:
        t_distribution_score = 1
    else:
        raise ValueError("t_distribution_score should be -1, 0 or 1")

    #
    # Percentile Bootstrap
    #
    # Compute the CI of the estimated mean using bootstrap
    list_xlow: list[float] = []
    list_xhigh: list[float] = []
    if args.figures:
        bootstrap_number_of_iterations = range(1, 5002, 25)
        print("bootstrap_5_score correspond à", bootstrap_number_of_iterations[5], "bootstrap resamples")
        print("bootstrap_last_score correspond à", bootstrap_number_of_iterations[-1], "bootstrap resamples")
    else:
        bootstrap_number_of_iterations = [100, 5000]
        print("bootstrap_5_score correspond à", bootstrap_number_of_iterations[0], "bootstrap resamples")
        print("bootstrap_last_score correspond à", bootstrap_number_of_iterations[-1], "bootstrap resamples")

    iterations: int
    for iterations in bootstrap_number_of_iterations:
        result = bootstrap_simulation(list_x, iterations, resampling_set_size)
        list_xlow.append(result[0]/2)
        list_xhigh.append(result[1]/2)


    # Analytical formula of what distribution the boostrap means should converge to and using this distribution
    # to infer the CI of the estimated mean
    # analytic lower bound
    cumulated_probability: decimal.Decimal = decimal.Decimal(0)
    t = -1  # aussi appelé 2kx dans le papier, représente la partie numérateur de x ∈ {0, 1/2k, ..., 2k/2k = 1}
    while cumulated_probability <= 2.5 / 100:
        t += 1
        cumulated_probability += analytic_probability_mean(
            t, resampling_set_size, estimated_p_0, estimated_p_1, estimated_p_2
        )
        # print(t, cumulated_probability)
        if t >= 2 * resampling_set_size and cumulated_probability < 2.5 / 100:
            # should not happen
            print("Error 1: t >= 2*resampling_set_size")
            exit()
    # the t we will get will be the first one such that P(X_kr<=t/2k) >= 2.5/100 which is by definition the
    # 0.025th quantile which is what we are looking for for the lower bound
    analytic_lower_bound = t / (2*resampling_set_size)
    # analytic upper bound
    while cumulated_probability <= 97.5 / 100:
        t += 1
        cumulated_probability += analytic_probability_mean(
            t, resampling_set_size, estimated_p_0, estimated_p_1, estimated_p_2
        )
        # print(t, cumulated_probability)
        if t >= 2 * resampling_set_size and cumulated_probability < 97.5 / 100:
            # should not happen
            print("Error 2: t >= 2*resampling_set_size")
            exit()
    analytic_upper_bound = t / (2*resampling_set_size)
    # the t we will get will be the first one such that P(X_kr<=t/2k) >= 97.5/100 which is by definition the
    # 0.975th quantile which is what we are looking for for the upper bound

    # Figure with computed Percentile bootstrap CI + CLTSlutsky CI + Student's t CI
    if args.figures:
        plt.axhline(y=mu, color='#841D37', linestyle='-', label="True mean")
        plt.axhline(y=estimated_mean, color='#841D37', linestyle='-', label="Estimated mean", alpha=0.5)

        plt.plot(
            bootstrap_number_of_iterations,
            list_xlow,
            color="black",
            label="Stochastic Bootstrap lower bound",
            alpha=0.5
        )
        plt.plot(
            bootstrap_number_of_iterations,
            list_xhigh,
            color="#235789",
            label="Stochastic Bootstrap upper bound",
            alpha=0.5
        )

        plt.axhline(
            y=lower_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian lower bound",
        )
        plt.axhline(
            y=upper_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian upper bound",
        )

        plt.axhline(
            y=lower_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution lower bound",
        )
        plt.axhline(
            y=upper_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution upper bound",
        )

        # x&y axis limits
        plt.xlim(0, 5000)
        plt.ylim(estimated_mean - 0.37, estimated_mean + 0.37)

        plt.xlabel('Number of boostrap iterations')
        plt.ylabel(u"\u03bc")
        plt.title('n = ' + str(test_set_size) + ', k = ' + str(resampling_set_size))
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

        plt.savefig(
            f"figures{os.sep}{p0}-{p1}-{p2}{os.sep}"
            f"output_gaussian_tDistribution_pbootstrap_seed{seed}_n{test_set_size}.png",
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()

    if args.figures:
        if list_xlow[5] <= mu <= list_xhigh[5]:
            bootstrap_5_score = 0
        elif mu < list_xlow[5]:
            bootstrap_5_score = -1
        elif mu > list_xhigh[5]:
            bootstrap_5_score = 1
        else:
            raise ValueError("bootstrap_5_score should be -1, 0 or 1")
    else:
        if list_xlow[0] <= mu <= list_xhigh[0]:
            bootstrap_5_score = 0
        elif mu < list_xlow[0]:
            bootstrap_5_score = -1
        elif mu > list_xhigh[0]:
            bootstrap_5_score = 1
        else:
            raise ValueError("bootstrap_5_score should be -1, 0 or 1")
    if list_xlow[-1] <= mu <= list_xhigh[-1]:
        bootstrap_last_score = 0
    elif mu < list_xlow[-1]:
        bootstrap_last_score = -1
    elif mu > list_xhigh[-1]:
        bootstrap_last_score = 1
    else:
        raise ValueError("bootstrap_last_score should be -1, 0 or 1")

    # Figure with analytic Percentile bootstrap CI + computed Percentile bootstrap CI + CLTSlutsky CI + Student's t CI
    if args.figures:
        plt.axhline(y=mu, color='#841D37', linestyle='-', label="True mean")
        plt.axhline(y=estimated_mean, color='#841D37', linestyle='-', label="Estimated mean", alpha=0.5)

        plt.plot(
            bootstrap_number_of_iterations,
            list_xlow,
            color="black",
            label="Stochastic Percentile Bootstrap lower bound",
            alpha=0.5
        )
        plt.axhline(
            y=analytic_lower_bound,
            color='black',
            linestyle='--',
            label="Analytic Percentile Bootstrap lower bound"
        )
        plt.plot(
            bootstrap_number_of_iterations,
            list_xhigh,
            color="#235789",
            label="Stochastic Percentile Bootstrap upper bound",
            alpha=0.5
        )
        plt.axhline(
            y=analytic_upper_bound,
            color="#235789",
            linestyle='--',
            label="Analytic Percentile Boostrap upper bound"
        )

        plt.axhline(
            y=lower_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian lower bound",
        )
        plt.axhline(
            y=upper_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian upper bound",
        )

        plt.axhline(
            y=lower_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution lower bound",
        )
        plt.axhline(
            y=upper_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution upper bound",
        )

        # x&y axis limits
        plt.xlim(0, 5000)
        plt.ylim(estimated_mean - 0.37, estimated_mean + 0.37)

        plt.xlabel('Number of boostrap iterations')
        plt.ylabel(u"\u03bc")
        plt.title('n = ' + str(test_set_size) + ', k = ' + str(resampling_set_size))
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

        plt.savefig(
            f"figures{os.sep}"
            f"{p0}-{p1}-{p2}{os.sep}"
            f"output_gaussian_tDistribution_pbootstrap_analytic_seed{seed}_n{test_set_size}.png",
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()

    if analytic_lower_bound <= mu <= analytic_upper_bound:
        bootstrap_analytical_score = 0
    elif mu < analytic_lower_bound:
        bootstrap_analytical_score = -1
    elif mu > analytic_upper_bound:
        bootstrap_analytical_score = 1
    else:
        raise ValueError("bootstrap_analytical_score should be -1, 0 or 1")

    #
    # Bias-Corrected and Accelerated Bootstrap Method
    #
    # Compute the CI of the estimated mean using the Bias-Corrected and Accelerated Bootstrap Method
    list_bca_xlow: list[float] = []
    list_bca_xhigh: list[float] = []
    if args.figures:
        bootstrap_bca_number_of_iterations = range(1, 5002, 25)
        print("bootstrap_bca_5_score correspond à", bootstrap_bca_number_of_iterations[5], "bootstrap resamples")
        print("bootstrap_bca_last_score correspond à", bootstrap_bca_number_of_iterations[-1], "bootstrap resamples")
    else:
        bootstrap_bca_number_of_iterations = [100, 5000]
        print("bootstrap_bca_5_score correspond à", bootstrap_bca_number_of_iterations[0], "bootstrap resamples")
        print("bootstrap_bca_last_score correspond à", bootstrap_bca_number_of_iterations[-1], "bootstrap resamples")

    iterations: int
    for iterations in bootstrap_bca_number_of_iterations:
        result = bootstrap_bca_simulation(list_x, estimated_mean, iterations, resampling_set_size)
        list_bca_xlow.append(result[0]/2)
        list_bca_xhigh.append(result[1]/2)


    # Figure with analytic Percentile bootstrap CI + computed Percentile bootstrap CI + CLTSlutsky CI + Student's t CI
    # + computed BCA bootstrap CI
    if args.figures:
        plt.axhline(y=mu, color='#841D37', linestyle='-', label="True mean")
        plt.axhline(y=estimated_mean, color='#841D37', linestyle='-', label="Estimated mean", alpha=0.5)

        plt.plot(
            bootstrap_number_of_iterations,
            list_xlow,
            color="black",
            label="Stochastic Bootstrap lower bound",
            alpha=0.5
        )
        plt.plot(
            bootstrap_number_of_iterations,
            list_xhigh,
            color="#235789",
            label="Stochastic Bootstrap upper bound",
            alpha=0.5
        )

        plt.axhline(
            y=analytic_lower_bound,
            color='black',
            linestyle='--',
            label="Analytic Percentile Bootstrap lower bound"
        )
        plt.axhline(
            y=analytic_upper_bound,
            color="#235789",
            linestyle='--',
            label="Analytic Percentile Boostrap upper bound"
        )

        plt.axhline(
            y=lower_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian lower bound",
        )
        plt.axhline(
            y=upper_bound_CLTslutsky_10_digits,
            color="#ABA194",
            linestyle="--",
            label="Gaussian upper bound",
        )

        plt.axhline(
            y=lower_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution lower bound",
        )
        plt.axhline(
            y=upper_bound_Student_10_digits,
            color="#E4D6A7",
            linestyle="--",
            label="t distribution upper bound",
        )

        plt.plot(
            bootstrap_number_of_iterations,
            list_bca_xlow,
            color="#A8D5A8",
            linestyle="--",
            label="BCA lower bound",
        )
        plt.plot(
            bootstrap_number_of_iterations,
            list_bca_xhigh,
            color="#006400",
            linestyle="--",
            label="BCA upper bound",
        )

        # x&y axis limits
        plt.xlim(0, 5000)
        plt.ylim(estimated_mean - 0.37, estimated_mean + 0.37)

        plt.xlabel('Number of boostrap iterations')
        plt.ylabel(u"\u03bc")
        plt.title('n = ' + str(test_set_size) + ', k = ' + str(resampling_set_size))
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

        plt.savefig(
            f"figures{os.sep}{p0}-{p1}-{p2}{os.sep}"
            f"output_gaussian_tDistribution_pbootstrap_analytic_bca_seed{seed}_n{test_set_size}.png",
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()

    if args.figures:
        if list_bca_xlow[5] <= mu <= list_bca_xhigh[5]:
            bootstrap_bca_5_score = 0
        elif mu < list_bca_xlow[5]:
            bootstrap_bca_5_score = -1
        elif mu > list_bca_xhigh[5]:
            bootstrap_bca_5_score = 1
        else:
            raise ValueError("bootstrap_bca_5_score should be -1, 0 or 1")
    else:
        if list_bca_xlow[0] <= mu <= list_bca_xhigh[0]:
            bootstrap_bca_5_score = 0
        elif mu < list_bca_xlow[0]:
            bootstrap_bca_5_score = -1
        elif mu > list_bca_xhigh[0]:
            bootstrap_bca_5_score = 1
        else:
            raise ValueError("bootstrap_bca_5_score should be -1, 0 or 1")
    if list_bca_xlow[-1] <= mu <= list_bca_xhigh[-1]:
        bootstrap_bca_last_score = 0
    elif mu < list_bca_xlow[-1]:
        bootstrap_bca_last_score = -1
    elif mu > list_bca_xhigh[-1]:
        bootstrap_bca_last_score = 1
    else:
        raise ValueError("bootstrap_bca_last_score should be -1, 0 or 1")

    scores = [
        round(mu, 4),
        test_set_size,
        seed,
        bootstrap_bca_5_score,
        bootstrap_bca_last_score,
        bootstrap_5_score,
        bootstrap_last_score,
        bootstrap_analytical_score,
        clt_slutsky_score,
        t_distribution_score,
    ]

    time.sleep(random.random()/2)

    with open("scores.csv", "a", newline="") as csvfile:
        writer_object = writer(csvfile)
        writer_object.writerow(scores)
        csvfile.close()
