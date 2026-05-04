import numpy as np

from ai_engine.labeling.acquisition import BABAAcquisition


class TestBABAScore:
    def test_output_shape(self, al_config):
        acq = BABAAcquisition(al_config)
        preds = np.array([0, 1, 2, 0, 1])
        unc = np.array([0.1, 0.5, 0.9, 0.3, 0.7])
        scores = acq.score(preds, unc)
        assert scores.shape == (5,)

    def test_higher_uncertainty_higher_score(self, al_config):
        acq = BABAAcquisition(al_config)
        preds = np.array([0, 0])
        unc = np.array([0.1, 0.9])
        scores = acq.score(preds, unc)
        assert scores[1] > scores[0]

    def test_scores_finite(self, al_config):
        acq = BABAAcquisition(al_config)
        preds = np.zeros(10, dtype=int)
        unc = np.linspace(0, 1, 10)
        scores = acq.score(preds, unc)
        assert np.all(np.isfinite(scores))


class TestBatchSelection:
    def test_selects_correct_count(self, al_config, random_embeddings):
        acq = BABAAcquisition(al_config)
        n = len(random_embeddings)
        preds = np.zeros(n, dtype=int)
        unc = np.random.RandomState(42).rand(n)
        selected = acq.select_batch(preds, unc, random_embeddings, 5)
        assert len(selected) <= 5

    def test_respects_already_labeled(self, al_config, random_embeddings):
        acq = BABAAcquisition(al_config)
        n = len(random_embeddings)
        preds = np.zeros(n, dtype=int)
        unc = np.random.RandomState(42).rand(n)
        already = {0, 1, 2, 3, 4}
        selected = acq.select_batch(preds, unc, random_embeddings, 5, already)
        for idx in selected:
            assert idx not in already

    def test_empty_candidates(self, al_config, random_embeddings):
        acq = BABAAcquisition(al_config)
        n = len(random_embeddings)
        already = set(range(n))
        selected = acq.select_batch(
            np.zeros(n), np.zeros(n), random_embeddings, 5, already
        )
        assert selected == []


class TestCompareWithRandom:
    def test_baba_selects_higher_scores(self, al_config):
        acq = BABAAcquisition(al_config)
        preds = np.zeros(500, dtype=int)
        unc = np.random.RandomState(42).rand(500)
        scores = acq.score(preds, unc)
        result = BABAAcquisition.compare_with_random(scores, 50)
        assert result["baba_mean_score"] >= result["random_mean_score"]
