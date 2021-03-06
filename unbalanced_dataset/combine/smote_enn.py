"""Class to perform over-sampling using SMOTE and cleaning using ENN."""
from __future__ import print_function
from __future__ import division

from sklearn.utils import check_X_y

from ..over_sampling import SMOTE
from ..under_sampling import EditedNearestNeighbours
from ..base_sampler import BaseSampler


class SMOTEENN(BaseSampler):
    """Class to perform over-sampling using SMOTE and cleaning using ENN.

    Parameters
    ----------
    ratio : str or float, optional (default='auto')
            If 'auto', the ratio will be defined automatically to balanced
        the dataset. Otherwise, the ratio will corresponds to the
        number of samples in the minority class over the the number of
        samples in the majority class.

    random_state : int or None, optional (default=None)
        Seed for random number generation.

    verbose : bool, optional (default=True)
        Boolean to either or not print information about the
        processing.

    k : int, optional (default=5)
        Number of nearest neighbours to used to construct synthetic
        samples.

    m : int, optional (default=10)
        Number of nearest neighbours to use to determine if a minority
        sample is in danger.

    out_step : float, optional (default=0.5)
        Step size when extrapolating.

    kind_smote : str, optional (default='regular')
        The type of SMOTE algorithm to use one of the following
        options: 'regular', 'borderline1', 'borderline2', 'svm'

    nn_method : str, optional (default='exact')
        The nearest neighbors method to use which can be either:
        'approximate' or 'exact'. 'approximate' will use LSH Forest while
        'exact' will be an exact search.

    size_ngh : int, optional (default=3)
        Size of the neighbourhood to consider to compute the average
        distance to the minority point samples.

    kind_sel : str, optional (default='all')
        Strategy to use in order to exclude samples.

        - If 'all', all neighbours will have to agree with the samples of
        interest to not be excluded.
        - If 'mode', the majority vote of the neighbours will be used in
        order to exclude a sample.

    n_jobs : int, optional (default=-1)
        Number of threads to run the algorithm when it is possible.

    Attributes
    ----------
    ratio_ : str or float, optional (default='auto')
        If 'auto', the ratio will be defined automatically to balanced
        the dataset. Otherwise, the ratio will corresponds to the number
        of samples in the minority class over the the number of samples
        in the majority class.

    rs_ : int or None, optional (default=None)
        Seed for random number generation.

    min_c_ : str or int
        The identifier of the minority class.

    max_c_ : str or int
        The identifier of the majority class.

    stats_c_ : dict of str/int : int
        A dictionary in which the number of occurences of each class is
        reported.

    Notes
    -----
    The method is presented in [1]_.

    This class does not support mutli-class.

    References
    ----------
    .. [1] G. Batista, R. C. Prati, M. C. Monard. "A study of the behavior of
       several methods for balancing machine learning training data," ACM
       Sigkdd Explorations Newsletter 6 (1), 20-29, 2004.

    """

    def __init__(self, ratio='auto', random_state=None, verbose=True,
                 k=5, m=10, out_step=0.5, kind_smote='regular',
                 nn_method='exact', size_ngh=3, kind_enn='all', n_jobs=-1,
                 **kwargs):

        """Initialise the SMOTE ENN object.

        Parameters
        ----------
        ratio : str or float, optional (default='auto')
            If 'auto', the ratio will be defined automatically to balanced
            the dataset. Otherwise, the ratio will corresponds to the
            number of samples in the minority class over the the number of
            samples in the majority class.

        random_state : int or None, optional (default=None)
            Seed for random number generation.

        verbose : bool, optional (default=True)
            Boolean to either or not print information about the
            processing.

        k : int, optional (default=5)
            Number of nearest neighbours to used to construct synthetic
            samples.

        m : int, optional (default=10)
            Number of nearest neighbours to use to determine if a minority
            sample is in danger.

        out_step : float, optional (default=0.5)
            Step size when extrapolating.

        kind_smote : str, optional (default='regular')
            The type of SMOTE algorithm to use one of the following
            options: 'regular', 'borderline1', 'borderline2', 'svm'

        nn_method : str, optional (default='exact')
            The nearest neighbors method to use which can be either:
            'approximate' or 'exact'. 'approximate' will use LSH Forest while
            'exact' will be an exact search.

        size_ngh : int, optional (default=3)
            Size of the neighbourhood to consider to compute the average
            distance to the minority point samples.

        kind_sel : str, optional (default='all')
            Strategy to use in order to exclude samples.

            - If 'all', all neighbours will have to agree with the samples of
            interest to not be excluded.
            - If 'mode', the majority vote of the neighbours will be used in
            order to exclude a sample.

        n_jobs : int, optional (default=-1)
            Number of threads to run the algorithm when it is possible.

        Returns
        -------
        None

        """
        super(SMOTEENN, self).__init__(ratio=ratio, random_state=random_state,
                                       verbose=verbose)

        self.sm = SMOTE(ratio=ratio, random_state=random_state,
                        verbose=verbose, k=k, m=m, out_step=out_step,
                        kind=kind_smote, nn_method=nn_method, n_jobs=n_jobs,
                        **kwargs)

        self.enn = EditedNearestNeighbours(random_state=random_state,
                                           verbose=verbose,
                                           size_ngh=size_ngh,
                                           kind_sel=kind_enn, n_jobs=n_jobs)

    def fit(self, X, y):
        """Find the classes statistics before to perform sampling.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            Matrix containing the data which have to be sampled.

        y : ndarray, shape (n_samples, )
            Corresponding label for each sample in X.

        Returns
        -------
        self : object,
            Return self.

        """
        # Check the consistency of X and y
        X, y = check_X_y(X, y)

        super(SMOTEENN, self).fit(X, y)

        # Fit using SMOTE
        self.sm.fit(X, y)

        return self

    def transform(self, X, y):
        """Resample the dataset.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            Matrix containing the data which have to be sampled.

        y : ndarray, shape (n_samples, )
            Corresponding label for each sample in X.

        Returns
        -------
        X_resampled : ndarray, shape (n_samples_new, n_features)
            The array containing the resampled data.

        y_resampled : ndarray, shape (n_samples_new)
            The corresponding label of `X_resampled`

        """
        # Check the consistency of X and y
        X, y = check_X_y(X, y)

        super(SMOTEENN, self).transform(X, y)

        # Transform using SMOTE
        X, y = self.sm.transform(X, y)

        # Fit and transform using ENN
        return self.enn.fit_transform(X, y)
