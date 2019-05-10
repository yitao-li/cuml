# Copyright (c) 2019, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest
import cudf
import numpy as np
import pandas as pd
from cuml import Lasso as cuLasso
from sklearn.linear_model import Lasso
from cuml.linear_model import ElasticNet as cuElasticNet
from sklearn.linear_model import ElasticNet
from cuml.test.utils import array_equal
from sklearn.datasets import make_regression


@pytest.mark.parametrize('datatype', [np.float32, np.float64])
@pytest.mark.parametrize('X_type', ['dataframe', 'ndarray'])
@pytest.mark.parametrize('lr', [0.1, 0.001])
@pytest.mark.parametrize('algorithm', ['cyclic', 'random'])
@pytest.mark.parametrize('nrows', [pytest.param(20, marks=pytest.mark.unit),
                                   pytest.param(500000,
                                                marks=pytest.mark.stress),
                                   pytest.param(5000,
                                                marks=pytest.mark.quality)])
@pytest.mark.parametrize('ncols', [pytest.param(3, marks=pytest.mark.unit),
                                   pytest.param(1000,
                                                marks=pytest.mark.stress),
                                   pytest.param(100,
                                                marks=pytest.mark.quality)])
@pytest.mark.parametrize('n_info', [pytest.param(2, marks=pytest.mark.unit),
                                    pytest.param(500,
                                                 marks=pytest.mark.stress),
                                    pytest.param(50,
                                                 marks=pytest.mark.quality)])
def test_lasso(datatype, X_type, lr, algorithm,
               nrows, ncols, n_info):

    train_rows = np.int32(nrows*0.8)
    X, y = make_regression(n_samples=nrows, n_features=ncols,
                           n_informative=n_info, random_state=0)

    X_test = np.asarray(X[train_rows:, 0:]).astype(datatype)
    X_train = np.asarray(X[0:train_rows, :]).astype(datatype)
    y_train = np.asarray(y[0:train_rows, ]).astype(datatype)

    sk_lasso = Lasso(alpha=np.array([lr]), fit_intercept=True,
                     normalize=False, max_iter=1000,
                     selection=algorithm, tol=1e-10)
    sk_lasso.fit(X_train, y_train)

    cu_lasso = cuLasso(alpha=np.array([lr]), fit_intercept=True,
                       normalize=False, max_iter=1000,
                       selection=algorithm, tol=1e-10)

    if X_type == 'dataframe':
        y_train = pd.DataFrame({'fea0': y_train[0:, ]})
        X_train = pd.DataFrame(
            {'fea%d' % i: X_train[0:, i] for i in range(X_train.shape[1])})
        X_test = pd.DataFrame(
            {'fea%d' % i: X_test[0:, i] for i in range(X_test.shape[1])})
        X_cudf = cudf.DataFrame.from_pandas(X_train)
        X_cudf_test = cudf.DataFrame.from_pandas(X_test)
        y_cudf = y_train.values
        y_cudf = y_cudf[:, 0]
        y_cudf = cudf.Series(y_cudf)
        cu_lasso.fit(X_cudf, y_cudf)
        cu_predict = cu_lasso.predict(X_cudf_test).to_array()

    elif X_type == 'ndarray':

        cu_lasso.fit(X_train, y_train)
        cu_predict = cu_lasso.predict(X_test).to_array()

    sk_predict = sk_lasso.predict(X_test)
    assert array_equal(sk_predict, cu_predict, 1e-1, with_sign=True)


@pytest.mark.parametrize('datatype', [np.float32, np.float64])
@pytest.mark.parametrize('X_type', ['dataframe', 'ndarray'])
@pytest.mark.parametrize('lr', [0.1, 0.001])
@pytest.mark.parametrize('algorithm', ['cyclic', 'random'])
@pytest.mark.parametrize('nrows', [pytest.param(20, marks=pytest.mark.unit),
                                   pytest.param(500000,
                                                marks=pytest.mark.stress),
                                   pytest.param(5000,
                                                marks=pytest.mark.quality)])
@pytest.mark.parametrize('ncols', [pytest.param(3, marks=pytest.mark.unit),
                                   pytest.param(1000,
                                                marks=pytest.mark.stress),
                                   pytest.param(100,
                                                marks=pytest.mark.quality)])
@pytest.mark.parametrize('n_info', [pytest.param(2, marks=pytest.mark.unit),
                                    pytest.param(500,
                                                 marks=pytest.mark.stress),
                                    pytest.param(50,
                                                 marks=pytest.mark.quality)])
def test_elastic_net(datatype, X_type, lr, algorithm,
                     nrows, ncols, n_info):

    train_rows = np.int32(nrows*0.8)
    X, y = make_regression(n_samples=nrows, n_features=ncols,
                           n_informative=n_info, random_state=0)

    X_test = np.asarray(X[train_rows:, 0:]).astype(datatype)
    X_train = np.asarray(X[0:train_rows, :]).astype(datatype)
    y_train = np.asarray(y[0:train_rows, ]).astype(datatype)

    elastic_sk = ElasticNet(alpha=np.array([0.1]), fit_intercept=True,
                            normalize=False, max_iter=1000,
                            selection=algorithm, tol=1e-10)

    elastic_sk.fit(X_train, y_train)

    elastic_cu = cuElasticNet(alpha=np.array([0.1]), fit_intercept=True,
                              normalize=False, max_iter=1000,
                              selection=algorithm, tol=1e-10)

    if X_type == 'dataframe':
        y_train = pd.DataFrame({'fea0': y_train[0:, ]})
        X_train = pd.DataFrame(
            {'fea%d' % i: X_train[0:, i] for i in range(X_train.shape[1])})
        X_test = pd.DataFrame(
            {'fea%d' % i: X_test[0:, i] for i in range(X_test.shape[1])})
        X_cudf = cudf.DataFrame.from_pandas(X_train)
        X_cudf_test = cudf.DataFrame.from_pandas(X_test)
        y_cudf = y_train.values
        y_cudf = y_cudf[:, 0]
        y_cudf = cudf.Series(y_cudf)
        elastic_cu.fit(X_cudf, y_cudf)
        cu_predict = elastic_cu.predict(X_cudf_test).to_array()

    elif X_type == 'ndarray':

        elastic_cu.fit(X_train, y_train)
        cu_predict = elastic_cu.predict(X_test).to_array()

    sk_predict = elastic_sk.predict(X_test)

    assert array_equal(sk_predict, cu_predict, 1e-1, with_sign=True)
