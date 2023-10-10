import decimal

from aux_f import analytic_probability_mean, bootstrap_simulation

def analytic_probability_mean_testing(
        resampling_set_size: int,
        estimated_p_0: decimal.Decimal,
        estimated_p_1: decimal.Decimal,
        estimated_p_2: decimal.Decimal
) -> None:
    cumulated_probability: decimal.Decimal = decimal.Decimal(0)
    for t in range(0, 2*resampling_set_size + 1):
        cumulated_probability += analytic_probability_mean(
            t,
            resampling_set_size,
            estimated_p_0,
            estimated_p_1,
            estimated_p_2
        )
    assert cumulated_probability == 1


def test_different_p_and_n() -> None:
    analytic_probability_mean_testing(
        5,
        decimal.Decimal(5)/decimal.Decimal(100),
        decimal.Decimal(5)/decimal.Decimal(100),
        decimal.Decimal(90)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        30,
        decimal.Decimal(5)/decimal.Decimal(100),
        decimal.Decimal(5)/decimal.Decimal(100),
        decimal.Decimal(90)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        50,
        decimal.Decimal(5)/decimal.Decimal(100),
        decimal.Decimal(5)/decimal.Decimal(100),
        decimal.Decimal(90)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        400,
        decimal.Decimal(1)/decimal.Decimal(100),
        decimal.Decimal(1)/decimal.Decimal(100),
        decimal.Decimal(98)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        5,
        decimal.Decimal(7)/decimal.Decimal(100),
        decimal.Decimal(3)/decimal.Decimal(100),
        decimal.Decimal(90)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        30,
        decimal.Decimal(7)/decimal.Decimal(100),
        decimal.Decimal(3)/decimal.Decimal(100),
        decimal.Decimal(90)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        50,
        decimal.Decimal(7)/decimal.Decimal(100),
        decimal.Decimal(3)/decimal.Decimal(100),
        decimal.Decimal(90)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        400,
        decimal.Decimal(7)/decimal.Decimal(100),
        decimal.Decimal(1)/decimal.Decimal(100),
        decimal.Decimal(92)/decimal.Decimal(100),
    )
    analytic_probability_mean_testing(
        1000,
        decimal.Decimal(7)/decimal.Decimal(100),
        decimal.Decimal(1)/decimal.Decimal(100),
        decimal.Decimal(92)/decimal.Decimal(100),
    )


def test_bootstrap_simulation() -> None:
    x_low, x_high = bootstrap_simulation([1]*1000, 1000, 1000)
    assert x_low == 1
    assert x_high == 1

    x_low, x_high = bootstrap_simulation([1]*100, 2000, 100)
    assert x_low == 1
    assert x_high == 1
