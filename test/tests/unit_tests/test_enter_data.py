import os
import json
import pytest

from atm import constants, PROJECT_ROOT
from atm.config import SQLConfig, RunConfig
from atm.database import Database, db_session
from atm.enter_data import enter_data, create_dataset, create_datarun
from atm.utilities import get_local_data_path


DB_PATH = os.path.join(PROJECT_ROOT, 'test/atm.db')
DATA_URL = 'https://s3.amazonaws.com/mit-dai-delphi-datastore/downloaded/'
BASELINE_PATH = os.path.join(PROJECT_ROOT, 'test/baselines/best_so_far/')
BASELINE_URL = 'https://s3.amazonaws.com/mit-dai-delphi-datastore/best_so_far/'

METHOD_HYPERPARTS = {
    'logreg': 6,
    'svm': 4,
    'sgd': 24,
    'dt': 2,
    'et': 2,
    'rf': 2,
    'gnb': 1,
    'mnb': 1,
    'bnb': 1,
    'gp': 8,
    'pa': 4,
    'knn': 24,
    'mlp': 60,
}


@pytest.fixture
def db():
    return Database(dialect='sqlite', database=DB_PATH)


@pytest.fixture
def dataset(db):
    ds = db.get_dataset(1)
    if ds:
        return ds
    else:
        data_path = os.path.join(PROJECT_ROOT, 'data/test/pollution_1.csv')
        return create_dataset(db, 'class', data_path)


def test_create_dataset(db):
    train_url = DATA_URL + 'pollution_1_train.csv'
    test_url = DATA_URL + 'pollution_1_test.csv'

    train_path_local, _ = get_local_data_path(train_url)
    if os.path.exists(train_path_local):
        os.remove(train_path_local)

    test_path_local, _ = get_local_data_path(test_url)
    if os.path.exists(test_path_local):
        os.remove(test_path_local)

    run_conf = RunConfig(train_path=train_url,
                         test_path=test_url,
                         data_description='test',
                         class_column='class')
    dataset = create_dataset(db, run_conf)
    dataset = db.get_dataset(dataset.id)

    assert os.path.exists(train_path_local)
    assert os.path.exists(test_path_local)

    assert dataset.train_path == train_url
    assert dataset.test_path == test_url
    assert dataset.description == 'test'
    assert dataset.class_column == 'class'
    assert dataset.n_examples == 60
    assert dataset.d_features == 16
    assert dataset.k_classes == 2
    assert dataset.majority >= 0.5


def test_enter_data_by_methods(dataset):
    sql_conf = SQLConfig(database=DB_PATH)
    db = Database(**vars(sql_conf))
    run_conf = RunConfig(dataset_id=dataset.id)

    for method, n_parts in METHOD_HYPERPARTS.items():
        run_conf.methods = [method]
        run_id = enter_data(sql_conf, run_conf)

        assert db.get_datarun(run_id)
        with db_session(db):
            run = db.get_datarun(run_id)
            assert run.dataset.id == dataset.id
            assert len(run.hyperpartitions) == n_parts


def test_enter_data_all(dataset):
    sql_conf = SQLConfig(database=DB_PATH)
    db = Database(**vars(sql_conf))
    run_conf = RunConfig(dataset_id=dataset.id,
                         methods=METHOD_HYPERPARTS.keys())

    run_id = enter_data(sql_conf, run_conf)

    with db_session(db):
        run = db.get_datarun(run_id)
        assert run.dataset.id == dataset.id
        assert len(run.hyperpartitions) == sum(METHOD_HYPERPARTS.values())


def test_run_per_partition(dataset):
    sql_conf = SQLConfig(database=DB_PATH)
    db = Database(**vars(sql_conf))
    run_conf = RunConfig(dataset_id=dataset.id, methods=['logreg'])

    run_ids = enter_data(sql_conf, run_conf, run_per_partition=True)

    with db_session(db):
        runs = []
        for run_id in run_ids:
            run = db.get_datarun(run_id)
            if run is not None:
                runs.append(run)

        assert len(runs) == METHOD_HYPERPARTS['logreg']
        assert all([len(run.hyperpartitions) == 1 for run in runs])
