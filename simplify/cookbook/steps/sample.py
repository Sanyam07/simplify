
from dataclasses import dataclass

from imblearn.combine import SMOTEENN, SMOTETomek
from imblearn.over_sampling import ADASYN, RandomOverSampler, SMOTE, SMOTENC
from imblearn.under_sampling import AllKNN, ClusterCentroids, NearMiss
from imblearn.under_sampling import RandomUnderSampler

from .step import Step


@dataclass
class Sample(Step):
    """Contains resampling algorithms used in the siMpLify package."""

    technique : str = 'none'
    parameters : object = None

    def __post_init__(self):
        super().__post_init__()
        self.techniques = {'adasyn' : ADASYN,
                           'cluster' : ClusterCentroids,
                           'knn' : AllKNN,
                           'near_miss' : NearMiss,
                           'random_over' : RandomOverSampler,
                           'random_under' : RandomUnderSampler,
                           'smote' : SMOTE,
                           'smotenc' : SMOTENC,
                           'smoteenn' :  SMOTEENN,
                           'smotetomek' : SMOTETomek}
        self.defaults = {'sampling_strategy' : 'auto'}
        return self

    def _add_parameters(self, x, columns):
        if self.technique in ['smotenc']:
            if self.columns:
                cat_features = self._get_indices(x, columns)
                self.parameters.update({'categorical_features' : cat_features})
            else:
                error = 'SMOTENC resampling requires categorical_features'
                raise RuntimeError(error)
        return self

    def blend(self, codex, columns = None):
        if self.technique != 'none':
            if self.verbose:
                print('Resampling data with', self.technique, 'technique')
            if not columns:
                columns = []
            self.runtime_parameters = {'random_state' : self.seed}
            self.initialize()
            self._add_parameters(codex.x, columns)
            self._store_feature_names(codex.x_train, codex.y_train)
            resampled_x, resampled_y = self.algorithm.fit_resample(
                    codex.x_train, codex.y_train)
            codex.x_train, codex.y_train = self._get_feature_names(
                    resampled_x, resampled_y)
        return codex

    def fit(self, x, y, columns = None):
        self.initialize()
        self._add_parameters(x, columns)
        return self

    def transform(self, x, y):
        return self.algorithm.fit_resample(x, y)

    def fit_transform(self, x, y):
        self.fit(x, y)
        return self.transform(x, y)
