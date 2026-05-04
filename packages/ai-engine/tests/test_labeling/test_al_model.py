import numpy as np

from ai_engine.labeling.al_model import GPALModel


class TestGPFit:
    def test_fit_and_predict(self, al_config):
        model = GPALModel(al_config)
        rng = np.random.RandomState(42)
        x = rng.randn(30, 10)
        y = (x[:, 0] > 0).astype(int)
        model.fit(x, y)
        preds, unc = model.predict(x[:5])
        assert len(preds) == 5
        assert len(unc) == 5
        assert all(0 <= u <= 1 for u in unc)

    def test_accuracy_reasonable(self, al_config):
        model = GPALModel(al_config)
        rng = np.random.RandomState(42)
        x = rng.randn(50, 10)
        y = (x[:, 0] > 0).astype(int)
        model.fit(x[:40], y[:40])
        acc = model.get_accuracy(x[40:], y[40:])
        assert 0 <= acc <= 1

    def test_unfitted_returns_defaults(self, al_config):
        model = GPALModel(al_config)
        preds, unc = model.predict(np.zeros((5, 10)))
        assert len(preds) == 5
        assert all(u == 1.0 for u in unc)


class TestAutoLabel:
    def test_auto_label_splits(self, al_config):
        model = GPALModel(al_config)
        rng = np.random.RandomState(42)
        x = rng.randn(50, 10)
        y = (x[:, 0] > 0).astype(int)
        model.fit(x, y)
        result = model.auto_label(x, threshold=0.5)
        total = len(result.labeled_indices) + len(result.unlabeled_indices)
        assert total == 50

    def test_high_threshold_fewer_labels(self, al_config):
        model = GPALModel(al_config)
        rng = np.random.RandomState(42)
        x = rng.randn(50, 10)
        y = (x[:, 0] > 0).astype(int)
        model.fit(x, y)
        result_low = model.auto_label(x, threshold=0.3)
        result_high = model.auto_label(x, threshold=0.95)
        assert len(result_high.labeled_indices) <= len(result_low.labeled_indices)

    def test_confidences_above_threshold(self, al_config):
        model = GPALModel(al_config)
        rng = np.random.RandomState(42)
        x = rng.randn(30, 10)
        y = (x[:, 0] > 0).astype(int)
        model.fit(x, y)
        threshold = 0.7
        result = model.auto_label(x, threshold=threshold)
        for c in result.confidences:
            assert c >= threshold
