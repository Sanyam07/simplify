# ml_funnel

![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)
[![Build Status](https://img.shields.io/travis/with_precedent/ml_funnel.svg)](https://travis-ci.org/with_precedent/ml_funnel) 

The Machine Learning Funnel is a high-level set of tools that allows users to mix and match various preprocessing methods and statistical models. Integrating scikit-learn, category-encoders, imblearn, xgboost, shap, and other modules, users are able to test and implement different "test tubes" in a machine learning funnel and export results for each option selected.

Although scikit-learn has gone a long way toward unifying interfaces with many common machine learning methods, it is still quite clunky in many situations. Present shortcomings include:
1) There is [a needlessly convoluted process](https://github.com/scikit-learn-contrib/sklearn-pandas#transformation-mapping) for implementing transformers on a subset of columns. Whereas many packages include a "cols" argument, [scikit-learn does not](https://medium.com/vickdata/easier-machine-learning-with-the-new-column-transformer-from-scikit-learn-c2268ea9564c).
2) .fit methods do not always work with certain forms of encoding (e.g., [target encoding in category-encoders](https://github.com/scikit-learn-contrib/categorical-encoding/issues/104)) because it does not allow the label data to be passed.
3) Pipeline and FeatureUnion [lack a mix-and-match type grid-search system](https://buildmedia.readthedocs.org/media/pdf/scikit-learn-enhancement-proposals/latest/scikit-learn-enhancement-proposals.pdf) for preprocessing, only for hyperparameter searches.
4) It doesn't directly use pandas dataframes despite various attempts to bridge the gap (e.g., [sklearn_pandas](https://github.com/scikit-learn-contrib/sklearn-pandas)). This can cause confusion and difficulty in keeping feature names attached to columns of data because numpy arrays do not incorporate string names of columns. This is why, for example, default feature_importances graphs do not include the actual feature names.
5) The structuring of scikit-learn compatible preprocessing algorithms to comply with the rigid .fit and .transform methods makes their use sometimes unintuitive.
6) The process for implementing different transformers on different groups of data (test, train, full, validation, etc.) within a Pipeline is [often messy and difficult](https://towardsdatascience.com/preprocessing-with-sklearn-a-complete-and-comprehensive-guide-670cb98fcfb9).
7) Scikit-learn has [no plans to offer GPU support](https://scikit-learn.org/stable/faq.html#will-you-add-gpu-support).

ml_funnel provides a cleaner, universal set of tools to access scikit-learn's many useful methods as well as other open-source packages. The goal is to make machine learning more accessible to a wider user base.

To that end, ml_funnel divides the feature engineering and modeling process into eleven major method steps:

* Scaler: converts numerical features into a common scale, using scikit-learn methods.
* Splitter: divides data into train, test, and/or validation sets once or through k-folds cross-validation, using custom and scikit-learn methods.
* Encoder: converts categorical features into numerical ones, using category-encoders and custom methods.
* Interactor: converts selected categorical features into new polynomial features, using PolynomialEncoder from category-encoders.
* Splicer: creates different subgroups of features to allow for easy comparison between them using a custom method.
* Sampler: synthetically resamples training data for imbalanced data, using imblearn methods, in applying algorithms that struggle with imbalanced data
* Decomposer: reduces features through matrix decomposition and related techniques, using scikit-learn methods.
* Selector: selects features recursively or as one-shot based upon user criteria, using scikit-learn methods.
* Model: implements machine learning algorithms, currently includes xgboost (with GPU optional support) and scikit-learn methods.
* Grid: tests different hyperparameters for the models selected, currently includes RandomizedSearchCV and GridSearchCV (Bayesian methods coming soon).
* Plot: produces helpful graphical representations based upon the model selected, including shap, seaborn, and matplotlib methods.

Users can easily select to use some or all of the above steps in specific cases with one or more methods selected at each stage.

In addition to the methods included, users can easily add additional methods at any stage by calling easy-to-use class methods.

Users can easily select different options using a text settings file (ml_settings.ini) or passing appropriate dictionaries to Funnel. This allows the ml_funnel to be used by beginner and advanced python programmers equally.

For example, using the settings file, a user could implement a funnel of different test tubes simply by listing the strings mapped to different methods:

    [funnel]
    scaler = minmax, robust
    splitter = train_test
    splicer = none
    encoder = target, helmert
    interactor = polynomial
    sampler = smote   
    decomposer = none
    selector = none
    algorithm_type = classifier
    algorithms = xgb, random_forest, logit
    search_method = random
    plots = default

With the above settings, all possible "test tubes" are automatically created using either default or user-specified parameters.

ml_funnel can import hyperparameters (and/or hyperparameter searches) based upon user selections in the settings file as follows:

    [xgb_params]
    booster = gbtree
    objective = binary:logistic
    eval_metric = logloss
    silent = True
    n_estimators = 100, 1000
    max_depth = 5, 30
    learning_rate = 0.001, 1.0
    subsample = 0.4, 0.6
    colsample_bytree = 0.4, 0.6
    colsample_bylevel = 0.4, 0.6
    min_child_weight = 0.5, 1.5
    gamma = 0.0, 0.1
    alpha = 0.5, 1

In the above case, anywhere two values are listed separated by a comma, ml_funnel automatically implements a hyperparameter search between those values (using either randint or uniform from scipy.stats, depending upon the data type). If just one hyperparameter is listed, it stays fixed throughout the tests. Further, the hyperparameters are automatically linked to the 'xgb' model by including that prefix to '_params' in the settings file.

ml_funnel currently supports NVIDIA GPU modeling for xgboost and will implement it for other incorporated models with built-in GPU support.

In addition to the implementation of the steps above, summary statistics and results (appropriate to the models) are exported to user-selected formats in either dynamically created or selected paths.
