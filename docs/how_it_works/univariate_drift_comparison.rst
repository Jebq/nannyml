Choosing Univariate Drift Detection Methods
===========================================

The data experiments presented in this page show how the Univariate Drift Detection methods available in NannyML
respond to data distribution shifts of selected type and magnitude. The main purpose is to build an intuition and
help to chose the right method given the type (categorical vs. continuous) and distribution of the variable that we want
to monitor. Some of
the
distribution shifts introduced are extreme and thus not very likely to happen in a real life scenarios. But again -
we are trying to build and intuition here and part of it is - for example -  to show how big of a shift needs to
happen so that we see a selected distance metric reaching its upper limit etc. In all the experiments described below
we compare two samples of data - one of which we call a *reference* sample and the other an *analysis* sample.


Comparison of Methods for Continuous Variables
----------------------------------------------

Shifting the Mean of the Analysis Data Set
..........................................
In this experiment, we show how each method responds as the mean of the analysis data set moves further away from the mean of the reference data set.
To demonstrate this, the reference data set was sampled from :math:`\mathcal{N}(0,1)`, and the analysis data set was sampled from :math:`\mathcal{N}(M,1)`
where :math:`M = \{0,0.1,0.2,...,7\}`.

We show the confidence intervals for empirical experiments like this one to demonstrate the stability of each method in comparison to the others. The confidence intervals depend
on the  sizes of the reference and analysis samples. These were kept the same for each method within the experiments to
ensure that
the
results are comparable.

In this experiment, the sample size of both the reference and analysis datasets was 1000 observations, and the number
of trials for each value of the mean of the analysis data set was 20.

.. image:: ../_static/univariate-comparison/shifting_mean.svg
    :width: 1400pt

The results illustrate that Wasserstein distance changes proportionally to the mean shift. Jensen-Shannon Distance and
the Kolmogorov-Smirnov Statistic are both relatively
more sensitive to smaller shifts compared to bigger shifts. This means that a shift in the mean of the analysis data set from 0 to 0.1 will cause a bigger change than a change from 5.0 to 5.1.
Hellinger Distance, on the other hand, displays behavior resembling a sigmoid function; Hellinger Distance is not as sensitive to small and large changes to the mean of the analysis data set
compared to shifts of medium size.

Shifting the Standard Deviation of the Analysis Data Set
........................................................
In this experiment, we show how each method responds as the standard deviation of the analysis set increases. The reference data set was sampled from :math:`\mathcal{N}(0, 1)` and the analysis data set
was sampled from :math:`\mathcal{N}(0, \Sigma)` where :math:`\Sigma = \{1, 1.1, 1.2,...,10\}`. The size of both the
reference and analysis data sets was again 1000 observations and the experiment consisted of 20 trials.

.. image:: ../_static/univariate-comparison/shifting_std.svg
    :width: 1400pt

In this case, Wasserstein distance again changes proportionally to the change in standard deviation. Jensen-Shannon
distance, the Kolmogorov-Smirnov D-statistic, and the Hellinger distance exhibit high sensitivity, even
to small changes. However, the Hellinger distance has a slightly *softer* start than the Jensen-Shannon distance and
the Kolmogorov-Smirnov statistic. In this experiment, the main difference between the Jensen-Shannon distance,
the Kolmogorov-Smirnov statistic, and Hellinger distance is that the stability of the measures (illustrated by the
confidence intervals) differs, with Jensen-Shannon distance exhibiting the highest relative stability of the three.


Tradeoffs of The Kolmogorov-Smirnov Statistic
.............................................
The Kolmogorov-Smirnov D-statistic is simply the maximum distance
between the empirical cumulative density functions (ECDFs) of the two analyzed samples. This can lead to cases where
drift
occurring
in one region
of the analysis distribution *hides* drift occurring in other areas. The visualization below shows an example of such
situation.

In this visualization, the reference distribution is a combination of two normal distributions and thus is bimodal. On the top row, labeled Analysis 1, only the right mode of the analysis distribution shifts. On the bottom row, labeled Analysis 2,
both the left mode and the right mode of the analysis distribution shift.

.. image:: ../_static/univariate-comparison/fool_ks.svg
    :width: 1400pt

Looking at columns 1 and 2 that show respectively Jensen-Shannon distance and Hellinger distance, we see that their
value increases as they both compare *similarity* of Empirical Probability Density Functions (EPDFs). **In the
third column,
which visualizes the Kolmogorov-Smirnov statistic, we see that the largest difference between the analysis ECDF and the
reference ECDF remains the same, which makes KS D-statistic insensitive for this type of shift.** The fourth column
shows Wasserstein distance which looks at the area between the reference ECDF and analysis ECDF hence it catches the
shift and its value increases.

Tradeoffs of Jensen-Shannon Distance and Hellinger Distance
...........................................................

Experiment 1
************
Both Jensen-Shannon Distance and Hellinger Distance are in a sense related to the *amount of overlap* between
probability
distributions.
This means that in cases where the *amount of overlap* stays the same but drift increases, neither the Jensen-Shannon
distance nor
the Hellinger distance will detect the change. Such cases are very
rare in practice, but they can occur - for example when two distributions are disjoint to begin with and then move
further away
from one another.
An example of this is shown below:

.. image:: ../_static/univariate-comparison/fool_js_ks_hellinger.svg
    :width: 1400pt

In this example, the reference distribution is a combination of two normal distributions and is thus bimodal. In the
first case (top row), the right
mode of the analysis distribution shifts to the right, and in the second case (bottom row), both modes shift to the
right. In
the
second case, this could
mean that either the left mode shifted over to the right of what was initially the right mode of the analysis or both the left mode and the
right mode of analysis shifted to the right. In either case, this subjectively seems like *more drift*, and neither
Jensen-Shannon distance nor
Hellinger distance catches this, but Wasserstein distance does. This is because Wasserstein distance *measures* the
amount
of *work* required to transform one distribution into the other. In this context, *work* can be thought of
as the amount of probability density multiplied by the distance it has to *travel*.

Experiment 2
************
Since Jensen-Shannon distance and Hellinger distance are related to the *overlap* between distributions, if the
distributions are completely *disjoint*,
then both measures will be maxed out at 1. So, if the distributions begin disjoint and get even further apart, Jensen-Shannon distance and Hellinger will not increase.
On the other hand, since Wasserstein Distance quantifies the distance between distributions, the measure will increase.

.. image:: ../_static/univariate-comparison/disjoint_only_emd.svg
    :width: 1400pt

In this experiment, we double the distance between the reference and analysis, and we see that Jensen-Shannon distance, the Kolmogorov-Smirnov statistic,
and Hellinger distance remain at 1 (their max value), while Wasserstein distance increases proportionally to the distance that the distribution has moved.
This example is more of an edge case, but disjoint distributions can arise in real-world scenarios. For example, when training generative adversarial networks,
this issue can arise, and a common remedy is using a loss function based on Wasserstein Distance.

Tradeoffs of Wasserstein Distance
.................................


Experiment 1
************
As a reminder - Wasserstein distance can be thought of as the *amount of work* (defined as the amount of density
times the distance it must be moved) that it
would take to transform one distribution into the other,
the presence of extreme data points can greatly increase its value. If two distributions are mostly identical, but one
has an outlier, then the work it takes to transport that
small bit of probability density to the other distribution is still significant (small density multiplied by a large distance).

.. image:: ../_static/univariate-comparison/outlier.svg
    :width: 1400pt

In this experiment, we move one data point to increasingly extreme values, and the result is that Wasserstein Distance increase in proportion to the size of that extreme value while the
other methods are not affected. In most cases changes in the overall shape of the distribution are the main focus. If
your data can contain extreme outliers we advise against using Wasserstein distance.

Experiment 2
************
In this experiment, we further exemplify the sensitivity of Wasserstein Distance to extreme values. To do so, we compare a normal distribution to a
Cauchy distribution. The Cauchy distribution has no analytically derivable moments, and generating samples from a random variable distributed
according to the Cauchy distribution will result in a data set with much of its density in a small range but with fat tails. The probability
density function (PDF) in the range :math:`[-10,10]` is visualized below.

.. image:: ../_static/univariate-comparison/outlier.svg
    :width: 1400pt

Notably, the general shape of the Cauchy distribution resembles the normal distribution, but there is much more density in the tails.
When increasing the scale parameter, the Cauchy distribution spreads out, and the tails become even denser. The behavior of Wasserstein
distance, Jensen-Shannon distance, Hellinger distance, and the Kolmogorov-Smirnov statistic when the reference sample is drawn from
:math:`\mathcal{N}(0,1)` and the analysis is drawn from :math:`\text{Cauchy}(0,\Gamma)` where :math:`\Gamma = \{0.5, 0.6,...,3\}` is shown below:

.. image:: ../_static/univariate-comparison/cauchy_empirical.svg
    :width: 1400pt

Since Wasserstein distance is sensitive to extreme values, the variance of the measure is high and increases together
with the scale parameter.
Jensen-Shannon distance, the Kolmogorov-Smirnov statistic, and the Hellinger distance are much more stable.

Comparison of Methods for Categorical Variables
-----------------------------------------------

Sensitivity to Sample Size of Different Drift Measures
......................................................

Generally, we would like methods that return the same value for the same magnitude of drift, regardless of the sample
size of
either the reference or
analysis set. Jensen-Shannon distance, Hellinger distance, and L-Infinity distance all exhibit this property, while the Chi-Squared statistic does not. In
cases where the chunks in your analysis may be different sizes, as can be the case when using period-based chunking, we suggest considering this behavior
before you use the chi-squared statistic.

In this experiment, the proportions of each category were held constant in both the reference and analysis data sets. In the reference data set, the relative
frequency of category “a” was always 0.5, the relative frequency of category “b” was also 0.5, and the data set size
was held constant at 2000 observations.
In the analysis data set, the relative frequency of category “a” was always 0.8, the relative frequency of category “b” was always 0.2, and
the data size increased from 100 points to 1000 points, as shown below.

.. image:: ../_static/univariate-comparison/chi2_sample_size.svg
    :width: 1400pt

Behavior When a Category Slowly Disappears
............................................

In this experiment, we show how each method behaves as a category shrinks and eventually disappears.
We start with the reference distribution and slowly shrink category “b” while increasing proportion of category “c” .

.. image:: ../_static/univariate-comparison/cat_disappears.svg
    :width: 1400pt

We see that L-Infinity has linear behavior in relation to the proportion of the categories changing.
In contrast, the Hellinger distance and chi-squared statistic increase slowly at first but more quickly when
the “b” category is about to disappear. This makes them more sensitive to changes in low-frequency categories.

Behavior When Observations from a New Category Occur
......................................................

In this experiment, we show how each method reacts to the slow entry of a new category. To begin with, the
analysis distribution is distributed identically to the reference distribution.

.. image:: ../_static/univariate-comparison/cat_enters.svg
    :width: 1400pt

The interesting things to note in this experiment compared to the previous one is that:

 * Jensen-Shannon is less sensitive when category disappears compare to appearance of a new category,

 * Hellinger distance behaviour when one category disappears looks symmetric to appearance of a new category,

 * Chi-square grows linearly when the new category increases its relative frequency but it grows faster when a
   category disappears.

 * L-infity is symmetric with respect to both situations.


Effect of Sample Size on Different Drift Measures
..................................................

In this experiment, we demonstrate the stability of each method while changing the size of the analysis sample. To demonstrate this,
we first drew a sample of 5000 points from  :math:`\text{Binom}(10,0.5)` to serve as the reference data set. The probability
mass function (PMF) of this distribution looks like this:

.. image:: ../_static/univariate-comparison/binomial_pmf.svg
    :width: 1400pt

Then, to demonstrate the effect of sample size, we drew samples of sizes :math:`\{100, 200, 300,..., 3000\}` , again
from :math:`\text{Binom}(10,0.5)`, to serve as our analysis data sets. We know that there is no distribution shift
between the reference sample and any of the analysis samples because they were all drawn from the same distribution, namely :math:`\text{Binom}(10,0.5)`.
In this way, we can see the impact that sample size has on each of the drift measures. The results are shown below:


.. image:: ../_static/univariate-comparison/binomial_and_sample_size.svg
    :width: 1400pt

Shift as measured by Jensen-Shannon distance, Hellinger distance, and L-infinity distance decreases as the analysis
sample increases in size and thus better represents the distribution. On the other hand, the chi-squared statistic on
average remains the same. This behaviour may be considered beneficial in some cases. Notice also the stability of each
of
the measures.

Effect of the Number of Categories on Different Drift Measures
..............................................................

In this experiment, we show how the number of categories affects each method. The setup of
this experiment is as follows: First, we defined a set :math:`M = \{2,3,4,...,60\}`, and for each :math:`m` in :math:`M`, we
drew a sample from :math:`\text{Binom}(m, 0.5)` of 5000 points to serve as the reference data set. We then
drew a sample of 1000 points again from the same distribution :math:`\text{Binom}(m, 0.5)` to serve as the analysis
data set (so not actual
data distribution shift).
We then calculated
the difference between the reference data and analysis data as measured by Jensen-Shannon distance, Hellinger
distance,
L-infinity distance, and the Chi-squared statistic. The results are shown below:

.. image:: ../_static/univariate-comparison/binom_and_num_cats.svg
    :width: 1400pt

We see an increase in the Jensen-Shannon distance, Hellinger distance, and the chi-squared statistic as the number of categories
increases because the small differences in the frequencies in each category due to sampling effects are summed up. Thus, the more
terms in the sum, the higher the value. On the other hand, L-infinity distance does not increase because it only looks at the largest
change in frequency of all the categories. For intuition, a visualization of the Hellinger distance and the L-infinity distance is shown
below when the number of categories is 61 (i.e., :math:`\text{Binom(60, 0.5}`)).

.. image:: ../_static/univariate-comparison/hellinger_vs_linf.svg
    :width: 1400pt

When dealing with
data sets with many categories, using the L-infinity distance may help to reduce false-positive alerts.

Comparison of Drift Methods on Data Sets with Many Categories
.............................................................

In cases with many categories, it can be difficult to significant shift if it only occurs in a few categories. This is
because some methods
(like Jensen-Shannon distance, Hellinger distance, and the chi-squared statistic) sum a transformation of the difference between
the relative frequency of each category. Sampling effects can cause small differences in the frequency of each category, but when summed
together, these small differences can hide important changes that occur in only a few categories. L-infinity distance
only looks at the
largest change in relative frequency among all the categories. It thus doesn't sum up all of the small, negligible differences caused by sampling error.

Here we show an experiment that highlights this behavior. There are three important samples in this experiment, namely the reference sample, an analysis
sample with no real drift (i.e. the sample is drawn from the same distribution), and an analysis set with severe drift in only one category. The
reference and analysis set without drift were drawn from the uniform distribution with 200 categories. The analysis set with severe drift was
constructed by drawing a sample from the uniform distribution with 200 categories, then adding more occurrences of the 100th category. The sample
size of each of the three sets was 7000 points. A visualization of the empirical probability mass function can be seen below.

.. image:: ../_static/univariate-comparison/uniform.svg
    :width: 1400pt

We see that each of the three distributions looks similar, aside from a major drift in category 100 in the analysis sample with severe drift. We can
compare the values that each method returns for the difference between the reference sample and the analysis sample without drift, and the reference
sample and the analysis sample with severe drift in one category, as seen below:

.. image:: ../_static/univariate-comparison/horizontal_bar.svg
    :width: 1400pt

We see that the sampling effects (the small differences in the frequencies of each category) hide the significant shift
when using Jensen-Shannon distance,
Hellinger distance. On the other hand, L-infinity shows a
significant difference between the two.

Results Summary (TLDR)
----------------------

Methods for Continuous Variables
................................

**We suggest Jensen-Shannon distance or Wasserstein distance for continuous features.**
While there is no one-size-fits-all method, both of these methods perform well in many cases, and generally, if drift occurs, these methods will catch it.

There are three main differences between these two measures. First, Jensen-Shannon distance will always be in the range :math:`[0, 1]`, whereas Wasserstein distance
has a range of :math:`[0, \infty)`. Second, Jensen-Shannon distance tends to be more sensitive to small drifts, meaning that it will likely raise more false alarms
than Wasserstein distance, but it might be more successful in catching meaningful low-magnitude drifts. And third, Wasserstein distance tends to be more
sensitive to outliers than Jensen-Shannon distance.

Methods For Categorical Variables
.................................
**For categorical features, we recommend Jensen-Shannon distance or L-Infinity distance if you have many categories.**
Both methods perform well in most cases, exhibit few downsides, and are bounded in the range :math:`[0,1]`. In cases
where there are many categories, and you care about changes to even one category, we suggest L-Infinity distance.
