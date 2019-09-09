
from dataclasses import dataclass

from sklearn.cluster import (AffinityPropagation, AgglomerativeClustering,
                             Birch, DBSCAN, KMeans, MeanShift,
                             SpectralClustering)
from sklearn.svm import OneClassSVM

from .algorithm import Algorithm


@dataclass
class Clusterer(Algorithm):
    """Applies machine learning algorithms based upon user selections."""


    technique : str = ''
    parameters : object = None
    auto_prepare : bool = True
    name : str = 'clusterer'

    def __post_init__(self):

        super().__post_init__()
        return self

    def _set_defaults(self):
        self.options = {'affinity' : AffinityPropagation,
                        'agglomerative' : AgglomerativeClustering,
                        'birch' : Birch,
                        'dbscan' : DBSCAN,
                        'kmeans' : KMeans,
                        'mean_shift' : MeanShift,
                        'spectral' : SpectralClustering,
                        'svm_linear' : OneClassSVM,
                        'svm_poly' : OneClassSVM,
                        'svm_rbf' : OneClassSVM,
                        'svm_sigmoid' : OneClassSVM}
        return self
